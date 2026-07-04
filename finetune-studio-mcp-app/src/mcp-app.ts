import { App } from "@modelcontextprotocol/ext-apps";

const app = new App({ name: "FineTuneStudio", version: "1.0.0" });

// ── Types ─────────────────────────────────────────────────────────────
interface ModelCard {
  modelId: string;
  author: string;
  downloads: number;
  likes: number;
  pipeline_tag: string;
  tags: string[];
}

interface DatasetCard {
  datasetId: string;
  author: string;
  downloads: number;
  likes: number;
  description: string;
  tags: string[];
  size: string;
}

interface TrainingConfig {
  trainingType: "sft" | "dpo" | "orpo";
  chatTemplate: string;
  epochs: number;
  batchSize: number;
  learningRate: number;
  blockSize: number;
  gradientAccumulation: number;
  warmupRatio: number;
  weightDecay: number;
  loraR: number;
  loraAlpha: number;
  loraDropout: number;
  targetModules: string;
  quantization: string;
  hardware: string;
  projectName: string;
  datasetSplit: string;
  textColumn: string;
  maxSteps: number;  // 0 = no limit (train full dataset)
}

interface ChatMessage { role: "system" | "user" | "assistant"; content: string; }

interface TrainingJob {
  project_name: string;
  username: string;
  space_url: string;
  model_url: string;
  started_at: number;
  status: string;
}

interface ValidationResult {
  total: number;
  valid: number;
  errors: Array<{ line: number; message: string }>;
}

// ── Constants ─────────────────────────────────────────────────────────
const POPULAR_MODELS: ModelCard[] = [
  { modelId: "HuggingFaceTB/SmolLM2-1.7B-Instruct", author: "HuggingFaceTB", downloads: 5800000, likes: 1300, pipeline_tag: "text-generation", tags: ["pytorch", "transformers", "llm", "small"] },
  { modelId: "Qwen/Qwen2.5-3B-Instruct", author: "Qwen", downloads: 3200000, likes: 850, pipeline_tag: "text-generation", tags: ["pytorch", "qwen", "transformers"] },
  { modelId: "meta-llama/Llama-3.2-3B-Instruct", author: "meta-llama", downloads: 9000000, likes: 2400, pipeline_tag: "text-generation", tags: ["llama", "pytorch", "gated"] },
  { modelId: "microsoft/Phi-3-mini-4k-instruct", author: "microsoft", downloads: 4100000, likes: 1600, pipeline_tag: "text-generation", tags: ["phi", "pytorch", "transformers"] },
];

const POPULAR_INFERENCE_MODELS = [
  "meta-llama/Llama-3.2-3B-Instruct",
  "meta-llama/Llama-3.1-8B-Instruct",
  "Qwen/Qwen2.5-7B-Instruct",
  "mistralai/Mistral-7B-Instruct-v0.3",
  "google/gemma-2-2b-it",
];

const HARDWARE_OPTIONS = [
  { value: "spaces-a10g-large", label: "A10G 24GB — Recommended", est: "~$1.50/hr · ~15 min" },
  { value: "spaces-a10g-small", label: "A10G 24GB (small)", est: "~$0.75/hr · ~20 min" },
  { value: "spaces-a100-large", label: "A100 80GB — Large models", est: "~$4.00/hr · ~10 min" },
  { value: "spaces-t4-medium", label: "T4 16GB — Budget", est: "~$0.40/hr · ~45 min" },
];

// ── State ─────────────────────────────────────────────────────────────
let currentTab: "train" | "inference" = "train";
let trainStep = 1;
let selectedModel: ModelCard | null = null;
let modelSearchResults: ModelCard[] = [];
let modelSearchLoading = false;
let selectedDataset: DatasetCard | null = null;
let datasetSearchResults: DatasetCard[] = [];
let datasetSearchLoading = false;
let datasetMode: "hub" | "custom" = "hub";
let customData = "";
let customValidation: ValidationResult | null = null;
let trainingJob: TrainingJob | null = null;
let trainingPollTimer: ReturnType<typeof setInterval> | null = null;
let trainingStatus = "starting";
let trainingLogs = "";
let lossHistory: number[] = [];
let lastRecordedEpoch: number | null = null;   // epoch value at which loss was last pushed
let trainingMetrics = { loss: null as number | null, epoch: null as number | null };
let totalTrainingSteps: number | null = null;
let logsExpanded = true;
let fineTunedModelId: string | null = null;
let inferenceSpaceUrl: string | null = null;   // Gradio Space URL deployed after training
let frozenElapsed: string | null = null;   // locked when training completes
let startTrainingLoading = false;
let startTrainingError = "";
let setupRequired = false;
let setupUrl = "";

// Inference
let chatModel = POPULAR_INFERENCE_MODELS[0];
let chatModelInput = POPULAR_INFERENCE_MODELS[0];
let customModelMode = false;
let chatMessages: ChatMessage[] = [];
let chatSettings = { temperature: 0.7, topP: 0.9, maxTokens: 512, systemPrompt: "" };
let settingsOpen = false;
let isGenerating = false;
let inferenceError = "";
let modelSearchOpen = false;
let inferenceModelResults: ModelCard[] = [];
let inferenceModelLoading = false;

// Training config defaults
function defaultConfig(): TrainingConfig {
  const shortName = (selectedModel?.modelId || "model").split("/").pop()!.toLowerCase().replace(/[^a-z0-9-]/g, "-");
  const ts = Date.now().toString().slice(-6);
  return {
    trainingType: "sft",
    chatTemplate: "none",
    epochs: 2,
    batchSize: 1,
    learningRate: 0.0002,
    blockSize: 1024,
    gradientAccumulation: 4,
    warmupRatio: 0.1,
    weightDecay: 0.01,
    loraR: 16,
    loraAlpha: 32,
    loraDropout: 0.05,
    targetModules: "all-linear",
    quantization: "int4",
    hardware: "spaces-a10g-large",
    projectName: `ft-${shortName}-${ts}`,
    datasetSplit: "train",
    textColumn: "text",
    maxSteps: 0,
  };
}

let config: TrainingConfig = defaultConfig();

// ── Helpers ───────────────────────────────────────────────────────────
const esc = (s: string) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const fmtNum = (n: number) =>
  n >= 1e6 ? (n / 1e6).toFixed(1) + "M"
  : n >= 1e3 ? (n / 1e3).toFixed(1) + "k"
  : n.toString();

function renderMarkdown(text: string): string {
  // Escape HTML first, then apply markdown-like formatting
  let s = esc(text);
  // Code blocks
  s = s.replace(/```[\w]*\n?([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
  // Inline code
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Bold
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  // Italic
  s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  // Headers
  s = s.replace(/^### (.+)$/gm, "<h4 style='margin:6px 0 3px;font-size:13px;color:#f0f6fc'>$1</h4>");
  s = s.replace(/^## (.+)$/gm, "<h3 style='margin:8px 0 4px;font-size:14px;color:#f0f6fc'>$1</h3>");
  s = s.replace(/^# (.+)$/gm, "<h2 style='margin:8px 0 4px;font-size:15px;color:#f0f6fc'>$1</h2>");
  // Lists
  s = s.replace(/^[•·\-] (.+)$/gm, "<li style='margin-left:16px;list-style:disc;'>$1</li>");
  s = s.replace(/^\d+\. (.+)$/gm, "<li style='margin-left:16px;list-style:decimal;'>$1</li>");
  // Newlines (outside of block elements)
  s = s.replace(/\n\n/g, "<br><br>");
  s = s.replace(/\n(?!<\/?(li|h[1-6]|pre|code))/g, "<br>");
  return s;
}

function validateCustomData(text: string, trainingType: "sft" | "dpo" | "orpo"): ValidationResult {
  const lines = text.trim().split("\n").filter(l => l.trim());
  const errors: Array<{ line: number; message: string }> = [];
  let valid = 0;

  for (let i = 0; i < lines.length; i++) {
    const lineNum = i + 1;
    try {
      const obj = JSON.parse(lines[i]);
      if (trainingType === "sft") {
        if (!obj.messages && !obj.text) {
          errors.push({ line: lineNum, message: "Missing 'messages' or 'text' field" });
        } else if (obj.messages) {
          if (!Array.isArray(obj.messages)) {
            errors.push({ line: lineNum, message: "'messages' must be an array" });
          } else {
            const hasUser = obj.messages.some((m: any) => m.role === "user");
            const hasAst = obj.messages.some((m: any) => m.role === "assistant");
            if (!hasUser || !hasAst) {
              errors.push({ line: lineNum, message: "Need both 'user' and 'assistant' roles" });
            } else valid++;
          }
        } else { valid++; }
      } else {
        // DPO / ORPO
        if (!obj.prompt || !obj.chosen || !obj.rejected) {
          errors.push({ line: lineNum, message: "Missing 'prompt', 'chosen', or 'rejected'" });
        } else { valid++; }
      }
    } catch {
      errors.push({ line: lineNum, message: "Invalid JSON" });
    }
  }

  return { total: lines.length, valid, errors: errors.slice(0, 5) };
}

function sparklineSvg(data: number[], w = 120, h = 28): string {
  if (data.length < 2) return "";
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * (h - 4) - 2;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return `<svg width="${w}" height="${h}" style="overflow:visible" viewBox="0 0 ${w} ${h}">
    <polyline points="${pts}" fill="none" stroke="#2563eb" stroke-width="1.5" stroke-linejoin="round"/>
    <circle cx="${(data.length - 1) / (data.length - 1) * w}" cy="${h - ((data[data.length - 1] - min) / range) * (h - 4) - 2}" r="2.5" fill="#2563eb"/>
  </svg>`;
}

function elapsedStr(ms: number): string {
  const s = Math.floor(ms / 1000);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}m ${rem}s`;
}

// ── Render helpers ────────────────────────────────────────────────────
function modelCardHtml(m: ModelCard, selectable = true, selected = false): string {
  const isSelected = selected || (selectedModel?.modelId === m.modelId);
  return `
    <div class="model-card${isSelected ? " selected" : ""}" data-model-id="${esc(m.modelId)}" role="button">
      <div class="card-body">
        <div class="card-name">${esc(m.modelId)}</div>
        <div class="card-meta">
          <span class="card-meta-item">
            <svg width="10" height="10" viewBox="0 0 16 16" fill="currentColor"><path d="M8.878.392a1.75 1.75 0 0 0-1.756 0l-5.25 3.045A1.75 1.75 0 0 0 1 4.951v6.098c0 .624.332 1.2.872 1.514l5.25 3.045a1.75 1.75 0 0 0 1.756 0l5.25-3.045c.54-.313.872-.89.872-1.514V4.951c0-.624-.332-1.2-.872-1.514L8.878.392ZM7.875 1.69a.25.25 0 0 1 .25 0l4.63 2.685L8 7.133 3.245 4.375l4.63-2.685ZM2.5 5.677v5.372c0 .09.047.171.125.216l4.625 2.683V8.432Zm6.25 8.271 4.625-2.683a.25.25 0 0 0 .125-.216V5.677L8.75 8.432Z"/></svg>
            ${esc(m.author)}
          </span>
          <span class="card-meta-item">⬇ ${fmtNum(m.downloads)}</span>
          <span class="card-meta-item">♥ ${fmtNum(m.likes)}</span>
        </div>
        <div class="tag-pills">${m.tags.map(t => `<span class="tag-pill">${esc(t)}</span>`).join("")}</div>
      </div>
      ${selectable ? `<div class="card-action"><button class="btn btn-accent btn-sm select-model-btn" data-model-id="${esc(m.modelId)}">${isSelected ? "✓ Selected" : "Select"}</button></div>` : ""}
    </div>`;
}

function datasetCardHtml(d: DatasetCard): string {
  const isSelected = selectedDataset?.datasetId === d.datasetId;
  return `
    <div class="dataset-card${isSelected ? " selected" : ""}" data-dataset-id="${esc(d.datasetId)}" role="button">
      <div class="card-body">
        <div class="card-name">${esc(d.datasetId)}</div>
        <div class="card-meta">
          <span class="card-meta-item">${esc(d.author)}</span>
          <span class="card-meta-item">⬇ ${fmtNum(d.downloads)}</span>
          ${d.size ? `<span class="card-meta-item">📦 ${esc(d.size)}</span>` : ""}
        </div>
        ${d.description ? `<div class="card-desc">${esc(d.description)}</div>` : ""}
        <div class="tag-pills">${d.tags.map(t => `<span class="tag-pill">${esc(t)}</span>`).join("")}</div>
      </div>
      <div class="card-action"><button class="btn btn-accent btn-sm select-dataset-btn" data-dataset-id="${esc(d.datasetId)}">${isSelected ? "✓ Selected" : "Select"}</button></div>
    </div>`;
}

// ── Wizard bar ────────────────────────────────────────────────────────
function wizardBarHtml(): string {
  const steps = ["Select Model", "Dataset", "Configure", "Training"];
  const connectors = steps.map((_, i) =>
    i < steps.length - 1
      ? `<div class="wizard-connector${i + 1 < trainStep ? " done" : ""}"></div>`
      : ""
  );

  return `<div class="wizard-bar">
    ${steps.map((label, i) => {
      const n = i + 1;
      // Step 4 (Training) is also "done" once training completes
      const done = n < trainStep || (n === 4 && trainingStatus === "completed");
      const active = n === trainStep && !(n === 4 && trainingStatus === "completed");
      const cls = done ? "done" : active ? "active" : "";
      const num = done
        ? `<span class="step-done-icon">✓</span>`
        : `<span class="step-num">${n}</span>`;
      return `<div class="wizard-step ${cls}">
        ${num}
        <span>${label}</span>
      </div>${connectors[i]}`;
    }).join("")}
  </div>`;
}

// ── Step 1: Select Model ──────────────────────────────────────────────
function renderStep1(): string {
  const searchResults = modelSearchLoading
    ? `<div class="empty-results"><span class="loading-spinner"></span></div>`
    : modelSearchResults.length > 0
      ? modelSearchResults.map(m => modelCardHtml(m)).join("")
      : `<div class="section-label" style="margin-bottom:12px">⚡ Popular models</div>${POPULAR_MODELS.map(m => modelCardHtml(m)).join("")}`;

  const selBar = selectedModel
    ? `<div class="selected-model-bar">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="#58a6ff"><path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/></svg>
        ${esc(selectedModel.modelId)}
        <button class="clear-sel" id="clear-model-btn">×</button>
      </div>`
    : "";

  return `
    <div class="step-body">
      ${selBar}
      <div class="search-wrap">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="6.5" cy="6.5" r="4.5"/><line x1="9.5" y1="9.5" x2="14" y2="14"/>
        </svg>
        <input id="model-search" class="search-input" type="text" placeholder="Search Hugging Face models…" value="" autocomplete="off"/>
      </div>
      <div class="card-list" id="model-results">${searchResults}</div>
    </div>`;
}

// ── Step 2: Dataset ───────────────────────────────────────────────────
function formatGuide(trainingType: "sft" | "dpo" | "orpo"): string {
  if (trainingType === "sft") {
    return `<span class="key">{"messages"</span>: [
  <span class="key">{"role"</span>: <span class="string">"system"</span>, <span class="key">"content"</span>: <span class="string">"You are a helpful assistant."</span>},
  <span class="key">{"role"</span>: <span class="string">"user"</span>, <span class="key">"content"</span>: <span class="string">"What is Python?"</span>},
  <span class="key">{"role"</span>: <span class="string">"assistant"</span>, <span class="key">"content"</span>: <span class="string">"Python is..."</span>}
]}`;
  }
  return `<span class="key">{"prompt"</span>: <span class="string">"Explain quantum computing"</span>,
 <span class="key">"chosen"</span>: <span class="string">"Quantum computing uses qubits..."</span>,
 <span class="key">"rejected"</span>: <span class="string">"It's very complicated magic..."</span>}`;
}

function renderStep2(): string {
  const isHub = datasetMode === "hub";
  const searchResults = datasetSearchLoading
    ? `<div class="empty-results"><span class="loading-spinner"></span></div>`
    : datasetSearchResults.length > 0
      ? datasetSearchResults.map(d => datasetCardHtml(d)).join("")
      : `<div class="empty-results">Type to search Hugging Face datasets</div>`;

  const selBar = selectedDataset
    ? `<div class="selected-model-bar">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="#58a6ff"><path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/></svg>
        ${esc(selectedDataset.datasetId)}
        <button class="clear-sel" id="clear-dataset-btn">×</button>
      </div>`
    : "";

  const validation = customValidation;
  const validationHtml = customValidation && customData.trim()
    ? validation!.errors.length === 0
      ? `<div class="validation-bar ok">✅ ${validation!.valid} valid rows detected</div>`
      : `<div class="validation-bar err">❌ ${validation!.errors.length} error(s) — ${validation!.valid} of ${validation!.total} rows valid</div>
         <div class="validation-errors">${validation!.errors.map(e => `Line ${e.line}: ${esc(e.message)}`).join("\n")}</div>`
    : "";

  return `
    <div class="step-body">
      <div class="toggle-group" style="margin-bottom:12px">
        <button class="toggle-btn${isHub ? " active" : ""}" id="mode-hub">🤗 Hub Dataset</button>
        <button class="toggle-btn${!isHub ? " active" : ""}" id="mode-custom">📋 Custom Data</button>
      </div>

      ${isHub ? `
        ${selBar}
        <div class="search-wrap">
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="6.5" cy="6.5" r="4.5"/><line x1="9.5" y1="9.5" x2="14" y2="14"/>
          </svg>
          <input id="dataset-search" class="search-input" type="text" placeholder="Search datasets (e.g. openassistant, alpaca…)" autocomplete="off"/>
        </div>
        <div class="card-list" id="dataset-results">${searchResults}</div>

        ${selectedDataset ? `
        <div class="divider"></div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Split name</label>
            <input class="form-input" id="ds-split" value="${esc(config.datasetSplit)}" placeholder="train"/>
            <span class="hint-text">⚠️ Check the dataset page for the exact split name — many datasets use names like <strong>train_sft</strong> instead of <strong>train</strong>.</span>
          </div>
          <div class="form-group">
            <label class="form-label">Text column</label>
            <input class="form-input" id="ds-text-col" value="${esc(config.textColumn)}" placeholder="text"/>
          </div>
        </div>` : ""}
      ` : `
        <div class="section-label">Expected format (${config.trainingType.toUpperCase()})</div>
        <div class="format-guide">${formatGuide(config.trainingType)}</div>
        <div class="form-group">
          <label class="form-label">Paste your JSONL data</label>
          <textarea class="form-textarea" id="custom-data" rows="8"
            placeholder='{"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]}'
            style="height:160px;font-family:monospace;font-size:11.5px">${esc(customData)}</textarea>
        </div>
        ${validationHtml}
      `}
    </div>`;
}

// ── Step 3: Configure ─────────────────────────────────────────────────
function hwEstimate(): string {
  const hw = HARDWARE_OPTIONS.find(h => h.value === config.hardware);
  return hw ? hw.est : "";
}

function renderStep3(): string {
  return `
    <div class="step-body">
      <div class="form-section">
        <div class="form-section-title">⚙ Training Type</div>
        <div class="radio-group">
          ${[
            { v: "sft", label: "SFT — Supervised Fine-Tuning", desc: "Standard fine-tuning on labeled input/output pairs. Best for most use cases." },
            { v: "dpo", label: "DPO — Direct Preference Optimization", desc: "Train on preference pairs (chosen vs rejected). Great for alignment." },
            { v: "orpo", label: "ORPO — Odds Ratio Preference Optimization", desc: "Alternative to DPO, often more stable." },
          ].map(r => `
            <label class="radio-option${config.trainingType === r.v ? " selected" : ""}" data-type="${r.v}">
              <input type="radio" name="training-type" value="${r.v}" ${config.trainingType === r.v ? "checked" : ""}/>
              <div>
                <div class="radio-label">${r.label}</div>
                <div class="radio-desc">${r.desc}</div>
              </div>
            </label>`).join("")}
        </div>
      </div>

      <div class="form-section">
        <div class="form-section-title">💬 Chat Template</div>
        <div class="form-group">
          <select class="form-select" id="chat-template">
            ${[
              { v: "none",      label: "none — plain text datasets (guanaco, alpaca-style, etc.)" },
              { v: "tokenizer", label: "tokenizer — auto-detect from model (use with messages-format datasets)" },
              { v: "chatml",    label: "chatml" },
              { v: "alpaca",    label: "alpaca" },
              { v: "llama3",    label: "llama3" },
              { v: "phi3",      label: "phi3" },
            ].map(t => `<option value="${t.v}" ${config.chatTemplate === t.v ? "selected" : ""}>${t.label}</option>`).join("")}
          </select>
          <span class="hint-text">
            Use <strong>none</strong> for plain-text datasets (e.g. guanaco, dolly, alpaca) that already contain the full prompt in a single text column.<br>
            Use <strong>tokenizer</strong> only if your dataset has a <code>messages</code> column with a list of <code>{role, content}</code> dicts.
          </span>
        </div>
      </div>

      <div class="form-section">
        <div class="form-section-title">🚀 Hyperparameters</div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Epochs</label>
            <input class="form-input" id="hp-epochs" type="number" min="1" max="10" value="${config.epochs}"/>
          </div>
          <div class="form-group">
            <label class="form-label">Max Steps <span style="font-weight:400;color:#8b949e">(0 = full dataset)</span></label>
            <input class="form-input" id="hp-max-steps" type="number" min="0" step="50" value="${config.maxSteps}" placeholder="0"/>
          </div>
          <div class="form-group">
            <label class="form-label">Batch Size</label>
            <select class="form-select" id="hp-batch">
              ${[1,2,4,8,16].map(n => `<option value="${n}" ${config.batchSize === n ? "selected" : ""}>${n}</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Learning Rate</label>
            <input class="form-input" id="hp-lr" type="number" step="0.00001" value="${config.learningRate}"/>
          </div>
          <div class="form-group">
            <label class="form-label">Block Size</label>
            <select class="form-select" id="hp-block">
              ${[512,1024,2048,4096].map(n => `<option value="${n}" ${config.blockSize === n ? "selected" : ""}>${n}</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Gradient Accumulation</label>
            <select class="form-select" id="hp-grad-acc">
              ${[1,2,4,8,16].map(n => `<option value="${n}" ${config.gradientAccumulation === n ? "selected" : ""}>${n}</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Warmup Ratio</label>
            <input class="form-input" id="hp-warmup" type="number" step="0.01" min="0" max="1" value="${config.warmupRatio}"/>
          </div>
          <div class="form-group">
            <label class="form-label">Weight Decay</label>
            <input class="form-input" id="hp-wdecay" type="number" step="0.001" min="0" value="${config.weightDecay}"/>
          </div>
        </div>
      </div>

      <div class="form-section">
        <div class="collapsible-header" id="lora-toggle">
          <div class="collapsible-title">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="#58a6ff"><path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Zm7-3.25v2.992l2.028.812a.75.75 0 0 1-.557 1.392l-2.5-1A.751.751 0 0 1 7 8.25v-3.5a.75.75 0 0 1 1.5 0Z"/></svg>
            LoRA Settings
          </div>
          <svg class="collapsible-chevron open" id="lora-chevron" width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M6.22 3.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L9.94 8 6.22 4.28a.75.75 0 0 1 0-1.06Z"/></svg>
        </div>
        <div class="collapsible-body open" id="lora-body">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">LoRA Rank (r)</label>
              <select class="form-select" id="hp-lora-r">
                ${[4,8,16,32,64].map(n => `<option value="${n}" ${config.loraR === n ? "selected" : ""}>${n}</option>`).join("")}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">LoRA Alpha</label>
              <input class="form-input" id="hp-lora-alpha" type="number" value="${config.loraAlpha}"/>
            </div>
            <div class="form-group">
              <label class="form-label">LoRA Dropout</label>
              <input class="form-input" id="hp-lora-drop" type="number" step="0.01" min="0" max="1" value="${config.loraDropout}"/>
            </div>
            <div class="form-group">
              <label class="form-label">Quantization</label>
              <select class="form-select" id="hp-quant">
                ${["none","int4","int8"].map(q => `<option value="${q}" ${config.quantization === q ? "selected" : ""}>${q === "none" ? "None" : q}</option>`).join("")}
              </select>
            </div>
            <div class="form-group full">
              <label class="form-label">Target Modules</label>
              <input class="form-input" id="hp-target-mods" value="${esc(config.targetModules)}" placeholder="all-linear"/>
            </div>
          </div>
        </div>
      </div>

      <div class="form-section">
        <div class="form-section-title">🖥 Hardware & Project</div>
        <div class="form-grid">
          <div class="form-group full">
            <label class="form-label">Hardware</label>
            <select class="form-select" id="hp-hardware">
              ${HARDWARE_OPTIONS.map(h => `<option value="${h.value}" ${config.hardware === h.value ? "selected" : ""}>${h.label}</option>`).join("")}
            </select>
          </div>
          <div class="form-group full">
            <label class="form-label">Project Name (becomes your HF model repo name)</label>
            <input class="form-input" id="hp-project" value="${esc(config.projectName)}" placeholder="my-finetuned-model"/>
          </div>
        </div>
        <div class="cost-estimate">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="#e3b341"><path d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763.707a.25.25 0 0 0-.44 0L1.698 13.132a.25.25 0 0 0 .22.368h12.164a.25.25 0 0 0 .22-.368Zm.53 3.996v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"/></svg>
          Estimated: <strong>${hwEstimate()}</strong> · Costs billed to your HF account
        </div>
      </div>

      ${setupRequired ? `
        <div class="error-msg" style="background:#fffbeb;border-color:#fcd34d;color:#92400e">
          <div style="font-weight:700;margin-bottom:6px">⚠️ One-time setup required</div>
          <div style="margin-bottom:10px;line-height:1.6">
            HF retired the old AutoTrain cloud API. You now need to deploy
            <strong>AutoTrain Advanced</strong> as a Space in your HF account (free, one-time setup):
          </div>
          <ol style="margin-left:16px;line-height:1.9;font-size:11.5px">
            <li>Open <a href="${esc(setupUrl)}" target="_blank" style="color:#2563eb;font-weight:600">huggingface.co/spaces/huggingface/autotrain-advanced</a></li>
            <li>Click <strong>"Duplicate this Space"</strong></li>
            <li>Name it exactly <code style="background:rgba(0,0,0,0.06);padding:1px 5px;border-radius:3px">autotrain-advanced</code></li>
            <li>Add your <code style="background:rgba(0,0,0,0.06);padding:1px 5px;border-radius:3px">HF_TOKEN</code> as a Space secret</li>
            <li>Wait ~1 min for it to start, then click <strong>Start Training</strong> again</li>
          </ol>
        </div>` :
        startTrainingError ? `<div class="error-msg">${esc(startTrainingError)}</div>` : ""}
    </div>`;
}

// ── Step 4: Training Progress ─────────────────────────────────────────
function renderStep4(): string {
  // Use frozenElapsed once training is done so the timer doesn't keep ticking
  const elapsed = frozenElapsed
    ?? (trainingJob ? elapsedStr(Date.now() - trainingJob.started_at) : "0s");

  const statusClass = trainingStatus === "completed" ? "completed"
    : trainingStatus === "error" ? "error"
    : trainingStatus === "training" ? "training"
    : "starting";

  const statusText = trainingStatus === "completed" ? "✅ Training complete — check HF Hub for your model"
    : trainingStatus === "error" ? "❌ Training error — check logs below"
    : trainingStatus === "training" ? "Training in progress…"
    : "Starting up training environment…";

  const progressPct = trainingStatus === "completed" ? 100
    : trainingStatus === "training" && trainingMetrics.epoch && config.epochs
      ? Math.min(99, (trainingMetrics.epoch / config.epochs) * 100)
      : trainingStatus === "training" ? 35 : 10;

  const logLines = trainingLogs.split("\n").filter(l => l.trim()).slice(-50);

  return `
    <div class="step-body">
      <div class="status-banner ${statusClass}">
        ${trainingStatus !== "completed" && trainingStatus !== "error"
          ? `<div class="pulse-dot"></div>` : ""}
        <span>${statusText}</span>
        ${trainingJob ? `<span style="margin-left:auto;font-size:11.5px;opacity:0.7">${elapsed}</span>` : ""}
      </div>

      ${trainingStatus === "completed" && trainingJob ? `
        <div class="success-box" style="margin-bottom:14px">
          <h3>🎉 Training complete!</h3>
          ${fineTunedModelId ? `
          <div style="background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:8px 12px;margin-bottom:8px;font-family:monospace;font-size:12px;color:#58a6ff;display:flex;align-items:center;gap:8px">
            <span style="color:#8b949e;flex-shrink:0">Model ID:</span>
            <span style="flex:1">${esc(fineTunedModelId)}</span>
          </div>
          ` : ""}
          ${inferenceSpaceUrl ? `
          <div style="background:#0d2311;border:1px solid #1f6335;border-radius:6px;padding:8px 12px;margin-bottom:8px;font-size:11.5px;color:#3fb950;display:flex;align-items:center;gap:8px">
            <span style="font-size:14px">🚀</span>
            <span>Inference Space deployed — building now (~2–3 min).
              <a href="${esc(inferenceSpaceUrl)}" target="_blank" style="color:#58a6ff;margin-left:4px">View Space →</a>
            </span>
          </div>
          ` : `
          <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:8px 12px;margin-bottom:8px;font-size:11.5px;color:#8b949e">
            ⏳ Deploying inference Space…
          </div>
          `}
          <p style="font-size:11px;color:#8b949e;margin-bottom:8px">The inference Space loads your model via transformers — click "Chat with model" once the Space is running (2–3 min).</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn btn-secondary btn-sm" id="view-on-hub-btn" data-url="${esc(trainingJob.model_url)}">🤗 View on Hub</button>
            <button class="btn btn-accent btn-sm" id="go-to-inference-btn">💬 Chat with model →</button>
            <button class="btn btn-ghost btn-sm" id="redeploy-space-btn" title="Redeploy inference Space with updated code" style="font-size:11px;color:#58a6ff;border:1px solid #58a6ff33">🔄 Redeploy Space</button>
          </div>
        </div>
      ` : ""}

      <div class="progress-wrap">
        <div class="progress-header">
          <span>${trainingStatus === "training" && trainingMetrics.epoch !== null
            ? `Epoch ${Math.min(config.epochs, Math.ceil(trainingMetrics.epoch || 0.001))} of ${config.epochs}`
            : trainingStatus === "completed" ? "Complete"
            : "Initializing…"}</span>
          <span>${progressPct.toFixed(0)}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${progressPct}%"></div>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">Training Loss</div>
          <div class="metric-value">${trainingMetrics.loss !== null ? trainingMetrics.loss.toFixed(4) : "—"}</div>
          <div class="sparkline-wrap">${sparklineSvg(lossHistory)}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Epoch</div>
          <div class="metric-value">${trainingMetrics.epoch !== null
            ? `${Math.min(config.epochs, Math.ceil(trainingMetrics.epoch || 0.001))} of ${config.epochs}`
            : "—"}</div>
          <div class="metric-sub">epochs</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Steps</div>
          <div class="metric-value">${(trainingMetrics.epoch !== null && totalTrainingSteps && config.epochs)
            ? `${Math.round((trainingMetrics.epoch / config.epochs) * totalTrainingSteps).toLocaleString()} of ${totalTrainingSteps.toLocaleString()}`
            : "—"}</div>
          <div class="metric-sub">steps</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Elapsed</div>
          <div class="metric-value" style="font-size:14px">${elapsed}</div>
          <div class="metric-sub">${config.hardware.replace("spaces-", "")}</div>
        </div>
      </div>

      <div class="log-wrap">
        <div class="log-header">
          <span class="section-label" style="margin-bottom:0">Training Logs</span>
          <button class="btn btn-ghost btn-sm" id="toggle-logs">${logsExpanded ? "Collapse" : "Expand"}</button>
        </div>
        ${logsExpanded ? `
        <div class="log-body" id="log-body" style="background:#1e293b;color:#f0f6fc">
          ${logLines.length > 0
            ? logLines.map(line => {
                const cls = /error|exception/i.test(line) ? "error"
                  : /loss|step|epoch/i.test(line) ? "highlight"
                  : /complete|done|finish|push/i.test(line) ? "success"
                  : "";
                return `<div class="log-line${cls ? " " + cls : ""}" style="color:inherit">${esc(line)}</div>`;
              }).join("")
            : `<div class="log-line" style="color:#ffffff">Still waiting for logs…</div>`}
        </div>` : ""}
      </div>

      ${trainingJob ? `
        <div style="font-size:11.5px;color:#484f58;text-align:center">
          <a href="${esc((trainingJob as any).training_space_url || trainingJob.space_url)}" target="_blank" style="color:#58a6ff">View Training Space</a>
          &nbsp;·&nbsp;
          <a href="${esc(((trainingJob as any).training_space_url || trainingJob.space_url) + '?logs=container')}" target="_blank" style="color:#58a6ff">Raw Logs</a>
          &nbsp;·&nbsp; Polling every 10s
        </div>` : ""}
    </div>`;
}

// ── Step navigation footer ─────────────────────────────────────────────
function navBarHtml(): string {
  if (trainStep === 4) return ""; // no nav in progress view

  const canNext = trainStep === 1
    ? !!selectedModel
    : trainStep === 2
      ? (datasetMode === "hub" ? !!selectedDataset : (customData.trim().length > 0 && (customValidation?.errors.length === 0)))
      : true;

  return `<div class="step-nav">
    ${trainStep > 1
      ? `<button class="btn btn-secondary" id="back-btn">← Back</button>`
      : `<div></div>`}
    <div style="display:flex;align-items:center;gap:10px">
      ${trainStep === 3
        ? `<button class="btn btn-primary" id="start-training-btn" ${startTrainingLoading ? "disabled" : ""}>
            ${startTrainingLoading ? `<span class="loading-spinner"></span> Starting…` : "🚀 Start Training"}
          </button>`
        : `<button class="btn btn-accent" id="next-btn" ${!canNext ? "disabled" : ""}>Next →</button>`}
    </div>
  </div>`;
}

// ── Inference Tab ─────────────────────────────────────────────────────
function renderInferenceTab(): string {
  const empty = chatMessages.length === 0;
  const msgHtml = empty
    ? `<div class="chat-empty">
        <div class="chat-empty-icon">💬</div>
        <div class="chat-empty-title">Chat with any HF model</div>
        <div class="chat-empty-sub">Select a model above and start a conversation. Works with any model on the Inference API.</div>
      </div>`
    : chatMessages.filter(m => m.role !== "system").map((m, i) => {
        const isUser = m.role === "user";
        const activeModel = customModelMode ? (chatModelInput || chatModel) : chatModel;
        const label = isUser ? "You" : (activeModel.split("/").pop() || "Model");
        const content = isUser ? esc(m.content) : renderMarkdown(m.content);
        return `<div class="msg-row ${m.role}" data-msg-idx="${i}">
          <div class="msg-label">${esc(label)}</div>
          <div class="msg-bubble">${content}</div>
        </div>`;
      }).join("");

  const popularOpts = [
    ...(fineTunedModelId ? [fineTunedModelId] : []),
    ...POPULAR_INFERENCE_MODELS.filter(m => m !== fineTunedModelId),
  ];

  return `
    <div class="chat-layout" style="height:100%">
      <div class="chat-topbar">
        <div class="model-selector-wrap" id="model-sel-wrap" style="display:flex;gap:6px;flex:1;min-width:0">
          <select class="model-selector" id="inference-model-sel" style="flex:1;min-width:0">
            ${popularOpts.map(m =>
              `<option value="${esc(m)}" ${!customModelMode && chatModel === m ? "selected" : ""}>${esc(m)}</option>`
            ).join("")}
            <option value="__custom__" ${customModelMode ? "selected" : ""}>Custom model ID…</option>
          </select>
          ${customModelMode ? `<input class="form-input" id="custom-model-input" type="text"
            placeholder="e.g. avi81/my-fine-tuned-model"
            value="${esc(chatModelInput)}"
            style="flex:2;min-width:0;font-size:11.5px"/>` : ""}
        </div>
        <button class="btn btn-ghost btn-sm" id="settings-toggle" title="Settings">
          <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0a8.2 8.2 0 0 1 .701.031C9.444.095 9.99.645 10.16 1.29l.288 1.107c.018.066.079.158.212.224.231.114.454.243.668.386.123.082.233.09.299.071l1.103-.303c.644-.176 1.392.021 1.82.63.27.385.506.792.704 1.218.315.675.111 1.422-.364 1.891l-.814.806c-.049.048-.098.147-.088.294.016.257.016.515 0 .772-.01.147.038.246.088.294l.814.806c.475.469.679 1.216.364 1.891a7.977 7.977 0 0 1-.704 1.217c-.428.61-1.176.807-1.82.63l-1.103-.303c-.066-.019-.176-.011-.299.071a5.909 5.909 0 0 1-.668.386c-.133.066-.194.158-.212.224l-.288 1.107c-.17.645-.715 1.195-1.458 1.259a8.25 8.25 0 0 1-1.402 0c-.744-.064-1.289-.614-1.458-1.26l-.288-1.106c-.018-.066-.079-.158-.212-.224a5.738 5.738 0 0 1-.668-.386c-.123-.082-.233-.09-.299-.071l-1.103.303c-.644.176-1.392-.021-1.82-.63a8.12 8.12 0 0 1-.704-1.218c-.315-.675-.111-1.422.363-1.891l.815-.806c.05-.048.098-.147.088-.294a6.214 6.214 0 0 1 0-.772c.01-.147-.038-.246-.088-.294l-.815-.806C.635 6.045.431 5.298.746 4.623a7.92 7.92 0 0 1 .704-1.217c.428-.61 1.176-.807 1.82-.63l1.103.303c.066.019.176.011.299-.071.214-.143.437-.272.668-.386.133-.066.194-.158.212-.224l.288-1.107c.17-.645.715-1.195 1.458-1.259A8.25 8.25 0 0 1 8 0ZM6.5 8a1.5 1.5 0 1 0 3 0 1.5 1.5 0 0 0-3 0Z"/></svg>
          Settings
        </button>
        ${chatMessages.length > 0 ? `<button class="btn btn-ghost btn-sm" id="clear-chat-btn">Clear</button>` : ""}
      </div>

      <div class="settings-panel${settingsOpen ? " open" : ""}">
        <div class="settings-grid">
          <div class="slider-group">
            <div class="slider-label-row">
              <span>Temperature</span>
              <span class="slider-val" id="temp-val">${chatSettings.temperature.toFixed(2)}</span>
            </div>
            <input type="range" id="temp-slider" min="0" max="2" step="0.01" value="${chatSettings.temperature}"/>
          </div>
          <div class="slider-group">
            <div class="slider-label-row">
              <span>Top-P</span>
              <span class="slider-val" id="topp-val">${chatSettings.topP.toFixed(2)}</span>
            </div>
            <input type="range" id="topp-slider" min="0" max="1" step="0.01" value="${chatSettings.topP}"/>
          </div>
          <div class="slider-group">
            <div class="slider-label-row">
              <span>Max Tokens</span>
              <span class="slider-val" id="maxt-val">${chatSettings.maxTokens}</span>
            </div>
            <input type="range" id="maxt-slider" min="64" max="2048" step="32" value="${chatSettings.maxTokens}"/>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">System Prompt (optional)</label>
          <textarea class="form-textarea" id="sys-prompt" rows="2" placeholder="You are a helpful assistant…" style="min-height:50px">${esc(chatSettings.systemPrompt)}</textarea>
        </div>
      </div>

      ${inferenceError ? `
        <div style="padding:8px 16px;flex-shrink:0">
          <div class="error-msg">${esc(inferenceError)}</div>
          ${fineTunedModelId && (inferenceError.includes("building") || inferenceError.includes("waking") || inferenceError.includes("inference Space") || inferenceError.includes("serverless inference")) ? `
          <div style="margin-top:6px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <button class="btn btn-ghost btn-sm" id="redeploy-space-inline-btn" style="font-size:11px;color:#58a6ff;border:1px solid #58a6ff55">
              🔄 Redeploy Inference Space
            </button>
            ${inferenceSpaceUrl ? `<a href="${esc(inferenceSpaceUrl)}" target="_blank" style="font-size:11px;color:#58a6ff">View Space →</a>` : ""}
          </div>` : ""}
        </div>` : ""}

      <div class="chat-area" id="chat-area">
        ${msgHtml}
        ${isGenerating ? `
          <div class="msg-row assistant">
            <div class="msg-label">${esc((customModelMode ? (chatModelInput || chatModel) : chatModel).split("/").pop() || "Model")}</div>
            <div class="typing-indicator">
              <div class="typing-dot"></div>
              <div class="typing-dot"></div>
              <div class="typing-dot"></div>
            </div>
          </div>` : ""}
      </div>

      <div class="chat-inputbar">
        <textarea class="chat-input" id="chat-input" placeholder="Send a message…" rows="1" ${isGenerating ? "disabled" : ""}></textarea>
        <button class="send-btn" id="send-btn" ${isGenerating ? "disabled" : ""}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="white">
            <path d="M1.5 1.5 14 8l-12.5 6.5V1.5Zm1.5 1.5v4.5l6-4.5-6 0Zm0 9V7.5l6 4.5-6 0Z"/>
          </svg>
        </button>
      </div>
    </div>`;
}

// ── Full render ───────────────────────────────────────────────────────
function renderAll() {
  const isTrain = currentTab === "train";
  const trainContent = isTrain ? renderTrainContent() : "";
  const inferenceContent = !isTrain ? renderInferenceTab() : "";

  document.getElementById("app")!.innerHTML = `
    <div style="display:flex;flex-direction:column;height:100%;overflow:hidden">
      <div class="studio-header">
        <div class="studio-brand">
          <div class="studio-brand-icon">
            <svg width="16" height="16" viewBox="0 0 95 88" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M47.2 0C21.1 0 0 19.7 0 44c0 9.4 3 18.2 8.2 25.4L3.5 85.2A2 2 0 0 0 5.4 88l16.8-4.5A49 49 0 0 0 47.2 88C73.3 88 95 68.3 95 44S73.3 0 47.2 0Z" fill="white" opacity="0.15"/>
              <ellipse cx="30" cy="40" rx="7" ry="8" fill="white"/>
              <ellipse cx="65" cy="40" rx="7" ry="8" fill="white"/>
              <path d="M28 56 Q47.5 70 67 56" stroke="white" stroke-width="4" stroke-linecap="round" fill="none"/>
              <path d="M20 22 L30 32" stroke="white" stroke-width="3.5" stroke-linecap="round"/>
              <path d="M75 22 L65 32" stroke="white" stroke-width="3.5" stroke-linecap="round"/>
            </svg>
          </div>
          FineTune Studio
        </div>
        <div class="tab-bar">
          <button class="tab-btn${isTrain ? " active" : ""}" id="tab-train">
            🔧 Train
          </button>
          <button class="tab-btn${!isTrain ? " active" : ""}" id="tab-inference">
            💬 Inference
          </button>
        </div>
      </div>

      <div class="tab-content" style="${!isTrain ? "display:none" : ""}">
        ${isTrain ? trainContent : ""}
      </div>

      <div style="flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden;${isTrain ? "display:none" : ""}">
        ${!isTrain ? inferenceContent : ""}
      </div>
    </div>`;

  bindEvents();
}

function renderTrainContent(): string {
  if (trainStep === 4) {
    return `
      ${wizardBarHtml()}
      <div class="tab-content" style="flex:1">
        ${renderStep4()}
      </div>`;
  }

  const stepContent = trainStep === 1 ? renderStep1()
    : trainStep === 2 ? renderStep2()
    : renderStep3();

  return `
    ${wizardBarHtml()}
    <div style="flex:1;min-height:0;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#30363d transparent">
      ${stepContent}
    </div>
    ${navBarHtml()}`;
}

// ── Event binding ─────────────────────────────────────────────────────
let modelSearchDebounce: ReturnType<typeof setTimeout> | null = null;
let datasetSearchDebounce: ReturnType<typeof setTimeout> | null = null;
let inferenceSearchDebounce: ReturnType<typeof setTimeout> | null = null;

function bindEvents() {
  // ── Tab switching ─────────────────────────────────────────────
  document.getElementById("tab-train")?.addEventListener("click", () => {
    if (currentTab !== "train") { currentTab = "train"; renderAll(); }
  });
  document.getElementById("tab-inference")?.addEventListener("click", () => {
    if (currentTab !== "inference") { currentTab = "inference"; renderAll(); }
  });

  // ── Train: Step 1 ─────────────────────────────────────────────
  document.getElementById("clear-model-btn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    selectedModel = null;
    modelSearchResults = [];
    renderAll();
  });

  document.querySelectorAll(".select-model-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = (btn as HTMLElement).dataset.modelId!;
      const found = [...POPULAR_MODELS, ...modelSearchResults].find(m => m.modelId === id);
      if (found) {
        selectedModel = found;
        config = defaultConfig();
        renderAll();
      }
    });
  });

  document.querySelectorAll(".model-card").forEach(card => {
    card.addEventListener("click", (e) => {
      if ((e.target as HTMLElement).closest(".select-model-btn")) return;
      const id = (card as HTMLElement).dataset.modelId!;
      const found = [...POPULAR_MODELS, ...modelSearchResults].find(m => m.modelId === id);
      if (found) { selectedModel = found; config = defaultConfig(); renderAll(); }
    });
  });

  const modelSearchInput = document.getElementById("model-search") as HTMLInputElement | null;
  if (modelSearchInput) {
    modelSearchInput.addEventListener("input", () => {
      const q = modelSearchInput.value.trim();
      if (modelSearchDebounce) clearTimeout(modelSearchDebounce);
      if (!q) { modelSearchResults = []; renderPartialModelResults(); return; }
      modelSearchDebounce = setTimeout(() => doSearchModels(q), 300);
    });
    // Restore focus if searching
    if (modelSearchResults.length > 0) modelSearchInput.focus();
  }

  document.getElementById("next-btn")?.addEventListener("click", () => {
    if (trainStep < 3) { trainStep++; renderAll(); }
  });

  document.getElementById("back-btn")?.addEventListener("click", () => {
    if (trainStep > 1) { trainStep--; renderAll(); }
  });

  // ── Train: Step 2 ─────────────────────────────────────────────
  document.getElementById("mode-hub")?.addEventListener("click", () => {
    datasetMode = "hub"; renderAll();
  });
  document.getElementById("mode-custom")?.addEventListener("click", () => {
    datasetMode = "custom"; renderAll();
  });

  document.getElementById("clear-dataset-btn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    selectedDataset = null;
    datasetSearchResults = [];
    renderAll();
  });

  document.querySelectorAll(".select-dataset-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = (btn as HTMLElement).dataset.datasetId!;
      const found = datasetSearchResults.find(d => d.datasetId === id);
      if (found) {
        selectedDataset = found;
        // Auto-set text column based on known dataset schemas
        const knownMessagesCols: Record<string, string> = {
          "HuggingFaceTB/smol-smoltalk": "messages",
          "HuggingFaceTB/smoltalk": "messages",
          "teknium/OpenHermes-2.5": "conversations",
        };
        const autoCol = knownMessagesCols[id];
        if (autoCol) config.textColumn = autoCol;
        renderAll();
      }
    });
  });

  document.querySelectorAll(".dataset-card").forEach(card => {
    card.addEventListener("click", (e) => {
      if ((e.target as HTMLElement).closest(".select-dataset-btn")) return;
      const id = (card as HTMLElement).dataset.datasetId!;
      const found = datasetSearchResults.find(d => d.datasetId === id);
      if (found) { selectedDataset = found; renderAll(); }
    });
  });

  const dsSearchInput = document.getElementById("dataset-search") as HTMLInputElement | null;
  if (dsSearchInput) {
    dsSearchInput.addEventListener("input", () => {
      const q = dsSearchInput.value.trim();
      if (datasetSearchDebounce) clearTimeout(datasetSearchDebounce);
      if (!q) { datasetSearchResults = []; renderPartialDatasetResults(); return; }
      datasetSearchDebounce = setTimeout(() => doSearchDatasets(q), 300);
    });
  }

  const customDataEl = document.getElementById("custom-data") as HTMLTextAreaElement | null;
  if (customDataEl) {
    customDataEl.addEventListener("input", () => {
      customData = customDataEl.value;
      customValidation = validateCustomData(customData, config.trainingType);
      // Update validation display without full re-render
      const valBar = document.querySelector(".validation-bar, .validation-errors");
      if (valBar) {
        const parent = valBar.parentElement!;
        renderPartialValidation(parent);
      } else {
        const stepBodyEl = document.querySelector(".step-body");
        if (stepBodyEl) renderAll();
      }
    });
  }

  // Split / text-col changes
  document.getElementById("ds-split")?.addEventListener("input", (e) => {
    config.datasetSplit = (e.target as HTMLInputElement).value;
  });
  document.getElementById("ds-text-col")?.addEventListener("change", (e) => {
    config.textColumn = (e.target as HTMLInputElement).value;
  });

  // ── Train: Step 3 ─────────────────────────────────────────────
  document.querySelectorAll("[data-type]").forEach(el => {
    el.addEventListener("click", () => {
      config.trainingType = (el as HTMLElement).dataset.type as "sft" | "dpo" | "orpo";
      renderAll();
    });
  });

  const bindNumInput = (id: string, setter: (v: number) => void) => {
    document.getElementById(id)?.addEventListener("change", (e) => {
      setter(parseFloat((e.target as HTMLInputElement).value));
    });
  };
  const bindSelInput = (id: string, setter: (v: string) => void) => {
    document.getElementById(id)?.addEventListener("change", (e) => {
      setter((e.target as HTMLSelectElement).value);
    });
  };
  const bindStrInput = (id: string, setter: (v: string) => void) => {
    document.getElementById(id)?.addEventListener("input", (e) => {
      setter((e.target as HTMLInputElement).value);
    });
  };

  bindSelInput("chat-template", v => { config.chatTemplate = v; });
  bindNumInput("hp-epochs", v => { if (!isNaN(v)) config.epochs = v; });
  bindNumInput("hp-max-steps", v => { if (!isNaN(v)) config.maxSteps = Math.max(0, Math.round(v)); });
  bindSelInput("hp-batch", v => { config.batchSize = parseInt(v); });
  bindNumInput("hp-lr", v => { if (!isNaN(v)) config.learningRate = v; });
  bindSelInput("hp-block", v => { config.blockSize = parseInt(v); });
  bindSelInput("hp-grad-acc", v => { config.gradientAccumulation = parseInt(v); });
  bindNumInput("hp-warmup", v => { if (!isNaN(v)) config.warmupRatio = v; });
  bindNumInput("hp-wdecay", v => { if (!isNaN(v)) config.weightDecay = v; });
  bindSelInput("hp-lora-r", v => { config.loraR = parseInt(v); });
  bindNumInput("hp-lora-alpha", v => { if (!isNaN(v)) config.loraAlpha = v; });
  bindNumInput("hp-lora-drop", v => { if (!isNaN(v)) config.loraDropout = v; });
  bindSelInput("hp-quant", v => { config.quantization = v; });
  bindStrInput("hp-target-mods", v => { config.targetModules = v; });
  bindSelInput("hp-hardware", v => {
    config.hardware = v;
    const est = document.querySelector(".cost-estimate strong");
    if (est) est.textContent = hwEstimate();
  });
  bindStrInput("hp-project", v => { config.projectName = v; });

  document.getElementById("lora-toggle")?.addEventListener("click", () => {
    const body = document.getElementById("lora-body");
    const chevron = document.getElementById("lora-chevron");
    if (body) body.classList.toggle("open");
    if (chevron) chevron.classList.toggle("open");
  });

  document.getElementById("start-training-btn")?.addEventListener("click", () => {
    doStartTraining();
  });

  // ── Train: Step 4 ─────────────────────────────────────────────
  document.getElementById("toggle-logs")?.addEventListener("click", () => {
    logsExpanded = !logsExpanded;
    const step4 = document.querySelector(".step-body");
    if (step4) step4.innerHTML = renderStep4().replace(/<div class="step-body">|<\/div>$/, "");
    renderAll();
  });

  document.getElementById("view-on-hub-btn")?.addEventListener("click", () => {
    const btn = document.getElementById("view-on-hub-btn") as HTMLButtonElement | null;
    const url = btn?.dataset.url;
    if (url) app.openLink({ url });
  });

  document.getElementById("go-to-inference-btn")?.addEventListener("click", () => {
    if (fineTunedModelId) {
      chatModel = fineTunedModelId;
      chatModelInput = fineTunedModelId;
      customModelMode = true;  // use the custom input so the model ID is shown correctly
    }
    currentTab = "inference";
    renderAll();
  });

  document.getElementById("redeploy-space-btn")?.addEventListener("click", async () => {
    if (!trainingJob) return;
    const btn = document.getElementById("redeploy-space-btn") as HTMLButtonElement | null;
    if (btn) { btn.disabled = true; btn.textContent = "⏳ Deploying…"; }
    try {
      const result = await app.callServerTool({ name: "deploy_inference_space", arguments: { project_name: trainingJob.project_name } });
      const rawText = (result as any)?.content?.[0]?.text ?? JSON.stringify(result);
      const parsed = typeof rawText === "string" ? JSON.parse(rawText) : rawText;
      if (parsed.success) {
        inferenceSpaceUrl = parsed.space_url;
        renderAll();
        alert(`✅ Inference Space redeployed!\n\nIt will rebuild in ~2-3 min.\nOnce it's running, click "Chat with model →".\n\nSpace: ${parsed.space_url}`);
      } else {
        alert(`❌ Deploy failed: ${parsed.error}`);
        if (btn) { btn.disabled = false; btn.textContent = "🔄 Redeploy Space"; }
      }
    } catch (err: any) {
      alert(`❌ Error: ${err?.message || String(err)}`);
      if (btn) { btn.disabled = false; btn.textContent = "🔄 Redeploy Space"; }
    }
  });

  // ── Inference ─────────────────────────────────────────────────
  // Inline "Redeploy Space" button shown in the inference error area
  document.getElementById("redeploy-space-inline-btn")?.addEventListener("click", async () => {
    const projectName = fineTunedModelId?.split("/")[1];
    if (!projectName) { alert("No trained model found. Train a model first."); return; }
    const btn = document.getElementById("redeploy-space-inline-btn") as HTMLButtonElement | null;
    if (btn) { btn.disabled = true; btn.textContent = "⏳ Deploying…"; }
    try {
      const result = await app.callServerTool({ name: "deploy_inference_space", arguments: { project_name: projectName } });
      const rawText = (result as any)?.content?.[0]?.text ?? JSON.stringify(result);
      const parsed = typeof rawText === "string" ? JSON.parse(rawText) : rawText;
      if (parsed.success) {
        inferenceSpaceUrl = parsed.space_url;
        inferenceError = "⏳ Inference Space is rebuilding (~2–3 min). Try again once it's running.";
        renderAll();
      } else {
        alert(`❌ Deploy failed: ${parsed.error}`);
        if (btn) { btn.disabled = false; btn.textContent = "🔄 Redeploy Inference Space"; }
      }
    } catch (err: any) {
      alert(`❌ Error: ${err?.message || String(err)}`);
      if (btn) { btn.disabled = false; btn.textContent = "🔄 Redeploy Inference Space"; }
    }
  });

  document.getElementById("inference-model-sel")?.addEventListener("change", (e) => {
    const val = (e.target as HTMLSelectElement).value;
    if (val === "__custom__") {
      customModelMode = true;
      chatModelInput = "";
      inferenceError = "";
      renderAll();
      // Focus the input after render
      setTimeout(() => (document.getElementById("custom-model-input") as HTMLInputElement)?.focus(), 50);
      return;
    }
    customModelMode = false;
    chatModel = val;
    chatModelInput = val;
    inferenceError = "";
    renderAll();
  });

  document.getElementById("custom-model-input")?.addEventListener("input", (e) => {
    chatModelInput = (e.target as HTMLInputElement).value.trim();
  });

  document.getElementById("custom-model-input")?.addEventListener("keydown", (e) => {
    if ((e as KeyboardEvent).key === "Enter" && chatModelInput) {
      chatModel = chatModelInput;
      inferenceError = "";
      renderAll();
    }
  });

  document.getElementById("settings-toggle")?.addEventListener("click", () => {
    settingsOpen = !settingsOpen;
    renderAll();
  });

  document.getElementById("clear-chat-btn")?.addEventListener("click", () => {
    chatMessages = [];
    inferenceError = "";
    renderAll();
  });

  // Sliders
  const bindSlider = (id: string, valId: string, setter: (v: number) => void, decimals = 2) => {
    const sl = document.getElementById(id) as HTMLInputElement | null;
    const valEl = document.getElementById(valId);
    if (sl) {
      sl.addEventListener("input", () => {
        const v = parseFloat(sl.value);
        setter(v);
        if (valEl) valEl.textContent = decimals === 0 ? v.toFixed(0) : v.toFixed(decimals);
      });
    }
  };
  bindSlider("temp-slider", "temp-val", v => { chatSettings.temperature = v; });
  bindSlider("topp-slider", "topp-val", v => { chatSettings.topP = v; });
  bindSlider("maxt-slider", "maxt-val", v => { chatSettings.maxTokens = v; }, 0);

  const sysPromptEl = document.getElementById("sys-prompt") as HTMLTextAreaElement | null;
  sysPromptEl?.addEventListener("input", () => { chatSettings.systemPrompt = sysPromptEl.value; });

  // Chat send
  const chatInput = document.getElementById("chat-input") as HTMLTextAreaElement | null;
  const sendBtn = document.getElementById("send-btn");

  chatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      doSendMessage();
    }
  });
  chatInput?.addEventListener("input", () => {
    // auto-resize textarea
    if (chatInput) {
      chatInput.style.height = "auto";
      chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
    }
  });

  sendBtn?.addEventListener("click", () => doSendMessage());
}

// ── Partial re-renders (avoid full re-render for perf) ────────────────
function renderPartialModelResults() {
  const el = document.getElementById("model-results");
  if (!el) return;
  if (modelSearchLoading) {
    el.innerHTML = `<div class="empty-results"><span class="loading-spinner"></span></div>`;
    return;
  }
  if (modelSearchResults.length === 0) {
    el.innerHTML = `<div class="section-label" style="margin-bottom:12px">⚡ Popular models</div>${POPULAR_MODELS.map(m => modelCardHtml(m)).join("")}`;
  } else {
    el.innerHTML = modelSearchResults.map(m => modelCardHtml(m)).join("");
  }
  // Re-bind card events
  el.querySelectorAll(".select-model-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = (btn as HTMLElement).dataset.modelId!;
      const found = [...POPULAR_MODELS, ...modelSearchResults].find(m => m.modelId === id);
      if (found) { selectedModel = found; config = defaultConfig(); renderAll(); }
    });
  });
  el.querySelectorAll(".model-card").forEach(card => {
    card.addEventListener("click", (e) => {
      if ((e.target as HTMLElement).closest(".select-model-btn")) return;
      const id = (card as HTMLElement).dataset.modelId!;
      const found = [...POPULAR_MODELS, ...modelSearchResults].find(m => m.modelId === id);
      if (found) { selectedModel = found; config = defaultConfig(); renderAll(); }
    });
  });
}

function renderPartialDatasetResults() {
  const el = document.getElementById("dataset-results");
  if (!el) return;
  if (datasetSearchLoading) {
    el.innerHTML = `<div class="empty-results"><span class="loading-spinner"></span></div>`;
    return;
  }
  el.innerHTML = datasetSearchResults.length > 0
    ? datasetSearchResults.map(d => datasetCardHtml(d)).join("")
    : `<div class="empty-results">Type to search Hugging Face datasets</div>`;

  el.querySelectorAll(".select-dataset-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = (btn as HTMLElement).dataset.datasetId!;
      const found = datasetSearchResults.find(d => d.datasetId === id);
      if (found) { selectedDataset = found; renderAll(); }
    });
  });
}

function renderPartialValidation(container: HTMLElement) {
  if (!customValidation || !customData.trim()) {
    // Remove old validation
    container.querySelectorAll(".validation-bar, .validation-errors").forEach(el => el.remove());
    return;
  }
  const v = customValidation;
  const html = v.errors.length === 0
    ? `<div class="validation-bar ok">✅ ${v.valid} valid rows detected</div>`
    : `<div class="validation-bar err">❌ ${v.errors.length} error(s) — ${v.valid} of ${v.total} rows valid</div>
       <div class="validation-errors">${v.errors.map(e => `Line ${e.line}: ${esc(e.message)}`).join("\n")}</div>`;

  container.querySelectorAll(".validation-bar, .validation-errors").forEach(el => el.remove());
  container.insertAdjacentHTML("beforeend", html);
}

// ── API calls ─────────────────────────────────────────────────────────
async function doSearchModels(query: string) {
  modelSearchLoading = true;
  renderPartialModelResults();
  try {
    const result = await app.callServerTool({ name: "search_models", arguments: { query, limit: 10 } });
    const text = (result.content[0] as any).text;
    const parsed = JSON.parse(text);
    modelSearchResults = parsed.models || [];
  } catch {
    modelSearchResults = [];
  } finally {
    modelSearchLoading = false;
    renderPartialModelResults();
  }
}

async function doSearchDatasets(query: string) {
  datasetSearchLoading = true;
  renderPartialDatasetResults();
  try {
    const result = await app.callServerTool({ name: "search_datasets", arguments: { query, limit: 10 } });
    const text = (result.content[0] as any).text;
    const parsed = JSON.parse(text);
    datasetSearchResults = parsed.datasets || [];
  } catch {
    datasetSearchResults = [];
  } finally {
    datasetSearchLoading = false;
    renderPartialDatasetResults();
  }
}

async function doStartTraining() {
  if (!selectedModel) return;
  startTrainingLoading = true;
  startTrainingError = "";
  setupRequired = false;
  renderAll();

  try {
    const args: Record<string, unknown> = {
      base_model: selectedModel.modelId,
      project_name: config.projectName,
      task: `llm:${config.trainingType}`,
      hardware: config.hardware,
      training_type: config.trainingType,
      chat_template: config.chatTemplate,
      hyperparameters: {
        epochs: config.epochs,
        batch_size: config.batchSize,
        learning_rate: config.learningRate,
        block_size: config.blockSize,
        lora_r: config.loraR,
        lora_alpha: config.loraAlpha,
        lora_dropout: config.loraDropout,
        quantization: config.quantization,
        gradient_accumulation: config.gradientAccumulation,
        warmup_ratio: config.warmupRatio,
        weight_decay: config.weightDecay,
        target_modules: config.targetModules,
        ...(config.maxSteps > 0 ? { max_steps: config.maxSteps } : {}),
      },
    };

    if (datasetMode === "hub" && selectedDataset) {
      args.dataset = selectedDataset.datasetId;
      args.dataset_split = config.datasetSplit;
      args.column_mapping = { text_column: config.textColumn };
    } else if (datasetMode === "custom") {
      // For custom data we use a placeholder; in practice the user would need to upload to HF Hub first
      args.dataset = "custom";
      args.column_mapping = { text_column: "text" };
    }

    const result = await app.callServerTool({ name: "start_training", arguments: args });
    const text = (result.content[0] as any).text;
    const parsed = JSON.parse(text);

    if (!parsed.success) {
      if (parsed.setup_required) {
        setupRequired = true;
        setupUrl = parsed.setup_url || "https://huggingface.co/spaces/autotrain-projects/autotrain-advanced";
        startTrainingError = "";
      } else {
        setupRequired = false;
        startTrainingError = parsed.error || "Training failed to start";
      }
      startTrainingLoading = false;
      renderAll();
      return;
    }

    setupRequired = false;
    trainingJob = {
      project_name: config.projectName,
      username: parsed.username,
      space_url: parsed.space_url,
      model_url: parsed.model_url,
      started_at: Date.now(),
      status: "starting",
    };
    trainingStatus = "starting";
    trainingLogs = "";
    lossHistory = [];
    lastRecordedEpoch = null;
    frozenElapsed = null;
    inferenceSpaceUrl = null;
    trainStep = 4;
    startTrainingLoading = false;
    renderAll();

    // Start polling
    startPolling();
  } catch (err: unknown) {
    startTrainingLoading = false;
    startTrainingError = err instanceof Error ? err.message : String(err);
    renderAll();
  }
}

function startPolling() {
  if (trainingPollTimer) clearInterval(trainingPollTimer);
  trainingPollTimer = setInterval(async () => {
    if (!trainingJob) { clearInterval(trainingPollTimer!); return; }
    if (trainingStatus === "completed" || trainingStatus === "error") {
      clearInterval(trainingPollTimer!);
      return;
    }
    try {
      const result = await app.callServerTool({
        name: "check_training_status",
        arguments: { project_name: trainingJob.project_name, username: trainingJob.username },
      });
      const text = (result.content[0] as any).text;
      const parsed = JSON.parse(text);

      trainingStatus = parsed.status || "starting";
      if (parsed.logs) trainingLogs = parsed.logs;
      if (parsed.training_space && trainingJob) {
        (trainingJob as any).training_space_url = parsed.training_space;
      }
      if (parsed.metrics) {
        trainingMetrics = {
          loss: parsed.metrics.loss ?? trainingMetrics.loss,
          epoch: parsed.metrics.epoch ?? trainingMetrics.epoch,
        };
        if (typeof parsed.metrics.totalSteps === "number") {
          totalTrainingSteps = parsed.metrics.totalSteps;
        }
        // Only record a new loss data-point when the epoch has actually
        // advanced since the last poll.  Appending on every poll while the
        // epoch stays the same creates flat horizontal segments that look
        // like the loss has plateaued / oscillated.
        const newEpoch = parsed.metrics.epoch ?? null;
        const newLoss  = parsed.metrics.loss  ?? null;
        if (typeof newLoss === "number" && typeof newEpoch === "number") {
          const epochChanged = lastRecordedEpoch === null || newEpoch > lastRecordedEpoch;
          if (epochChanged) {
            lossHistory.push(newLoss);
            if (lossHistory.length > 30) lossHistory.shift();
            lastRecordedEpoch = newEpoch;
          }
        }
      }

      if (trainingStatus === "completed") {
        fineTunedModelId = trainingJob.model_url.replace("https://huggingface.co/", "");
        // Save inference Space URL if the server deployed one
        if (parsed.inference_space_url && !inferenceSpaceUrl) {
          inferenceSpaceUrl = parsed.inference_space_url;
        }
        // Freeze the elapsed timer at the moment training completed
        if (!frozenElapsed) {
          frozenElapsed = elapsedStr(Date.now() - trainingJob.started_at);
        }
        clearInterval(trainingPollTimer!);
      }

      // Update only the step 4 content if we're in step 4
      if (trainStep === 4) {
        const stepBody = document.querySelector(".step-body");
        if (stepBody) {
          stepBody.outerHTML = renderStep4();
          // Re-bind step 4 specific events
          document.getElementById("toggle-logs")?.addEventListener("click", () => {
            logsExpanded = !logsExpanded; renderAll();
          });
          document.getElementById("view-on-hub-btn")?.addEventListener("click", () => {
            const btn = document.getElementById("view-on-hub-btn") as HTMLButtonElement | null;
            const url = btn?.dataset.url;
            if (url) app.openLink({ url });
          });
          document.getElementById("go-to-inference-btn")?.addEventListener("click", () => {
            if (fineTunedModelId) { chatModel = fineTunedModelId; chatModelInput = fineTunedModelId; customModelMode = true; }
            currentTab = "inference"; renderAll();
          });
          document.getElementById("redeploy-space-btn")?.addEventListener("click", async () => {
            if (!trainingJob) return;
            const btn = document.getElementById("redeploy-space-btn") as HTMLButtonElement | null;
            if (btn) { btn.disabled = true; btn.textContent = "⏳ Deploying…"; }
            try {
              const result = await app.callServerTool({ name: "deploy_inference_space", arguments: { project_name: trainingJob.project_name } });
              const rawText = (result as any)?.content?.[0]?.text ?? JSON.stringify(result);
              const parsed = typeof rawText === "string" ? JSON.parse(rawText) : rawText;
              if (parsed.success) {
                inferenceSpaceUrl = parsed.space_url;
                renderAll();
                alert(`✅ Inference Space redeployed! Rebuilding in ~2-3 min.\n${parsed.space_url}`);
              } else {
                alert(`❌ Deploy failed: ${parsed.error}`);
                if (btn) { btn.disabled = false; btn.textContent = "🔄 Redeploy Space"; }
              }
            } catch (err: any) {
              alert(`❌ Error: ${err?.message || String(err)}`);
              if (btn) { btn.disabled = false; btn.textContent = "🔄 Redeploy Space"; }
            }
          });
          // Auto-scroll logs
          const logBody = document.getElementById("log-body");
          if (logBody) logBody.scrollTop = logBody.scrollHeight;
        } else {
          renderAll();
        }
      }
    } catch {
      // Polling error, continue polling
    }
  }, 10000);
}

async function doSendMessage() {
  const input = document.getElementById("chat-input") as HTMLTextAreaElement | null;
  if (!input) return;
  const text = input.value.trim();
  if (!text || isGenerating) return;

  input.value = "";
  input.style.height = "auto";

  // Build messages array
  const msgs: ChatMessage[] = [];
  if (chatSettings.systemPrompt) {
    msgs.push({ role: "system", content: chatSettings.systemPrompt });
  }
  msgs.push(...chatMessages.filter(m => m.role !== "system"));
  msgs.push({ role: "user", content: text });

  chatMessages = msgs.filter(m => m.role !== "system");
  isGenerating = true;
  inferenceError = "";
  renderAll();

  // Scroll to bottom
  const chatArea = document.getElementById("chat-area");
  if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;

  try {
    const result = await app.callServerTool({
      name: "chat_with_model",
      arguments: {
        model_id: customModelMode ? (chatModelInput || chatModel) : chatModel,
        messages: msgs,
        parameters: {
          temperature: chatSettings.temperature,
          top_p: chatSettings.topP,
          max_tokens: chatSettings.maxTokens,
        },
      },
    });
    const raw = (result.content[0] as any).text;
    const parsed = JSON.parse(raw);

    if (parsed.error) {
      inferenceError = parsed.error;
      isGenerating = false;
      renderAll();
      return;
    }

    const responseText: string = parsed.text || "";
    chatMessages.push({ role: "assistant", content: "" });
    isGenerating = false;
    renderAll();

    // Progressive reveal
    await revealText(responseText);
  } catch (err: unknown) {
    inferenceError = err instanceof Error ? err.message : "Unknown error";
    isGenerating = false;
    renderAll();
  }
}

async function revealText(fullText: string) {
  const chatArea = document.getElementById("chat-area");
  // Find the last assistant bubble
  const bubbles = chatArea?.querySelectorAll(".msg-row.assistant .msg-bubble");
  const lastBubble = bubbles?.[bubbles.length - 1] as HTMLElement | undefined;
  if (!lastBubble) return;

  let i = 0;
  const CHUNK = 3;
  const DELAY = 12;

  const tick = () => {
    if (i >= fullText.length) {
      // Apply markdown formatting at end
      lastBubble.innerHTML = renderMarkdown(fullText);
      // Update state
      if (chatMessages.length > 0) {
        chatMessages[chatMessages.length - 1].content = fullText;
      }
      if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
      return;
    }
    i = Math.min(i + CHUNK, fullText.length);
    lastBubble.textContent = fullText.slice(0, i);
    if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
    setTimeout(tick, DELAY);
  };
  tick();
}

// ── Bootstrap ─────────────────────────────────────────────────────────
app.ontoolresult = () => {
  // launch_studio was called — render the full UI
  renderAll();
};

app.connect();
