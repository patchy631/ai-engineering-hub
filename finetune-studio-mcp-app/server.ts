console.log("Starting FineTune Studio MCP Server...");

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import {
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import cors from "cors";
import express from "express";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { Client as GradioClient } from "@gradio/client";

// ── __dirname compat (works on all Node ESM versions) ─────────────────
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const server = new McpServer({ name: "FineTuneStudio", version: "1.0.0" });
const resourceUri = "ui://finetune-studio/widget.html";

const HF_API = "https://huggingface.co/api";
const HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions";

// ── Inference Space templates ──────────────────────────────────────────
// A Gradio Space that loads the fine-tuned model and serves it via
// a simple /api/predict endpoint. Deployed automatically after training.
const INFERENCE_APP_PY = `
import gradio as gr
import json
import os
import torch
from transformers import pipeline

MODEL_ID = os.environ.get("MODEL_ID", "")
HF_TOKEN = os.environ.get("HF_TOKEN", None)

print(f"[inference] Loading {MODEL_ID} ...", flush=True)
try:
    _pipe = pipeline(
        "text-generation",
        model=MODEL_ID,
        torch_dtype=torch.float32,
        token=HF_TOKEN or None,
    )
    print("[inference] Ready!", flush=True)
except Exception as _e:
    print(f"[inference] Load error: {_e}", flush=True)
    _pipe = None

def predict(messages_json: str, max_tokens: float = 512, temperature: float = 0.7) -> str:
    """Generate a response given a JSON-encoded messages array."""
    if _pipe is None:
        return "Error: model failed to load. Check Space logs."
    try:
        messages = json.loads(messages_json)
        temp = float(temperature)
        result = _pipe(
            messages,
            max_new_tokens=int(max_tokens),
            temperature=temp if temp > 0.01 else None,
            do_sample=temp > 0.01,
            return_full_text=False,
        )
        content = result[0]["generated_text"]
        if isinstance(content, list):
            return content[-1].get("content", str(content[-1]))
        return str(content)
    except Exception as e:
        return f"Error: {e}"

demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Textbox(label="messages_json", lines=3),
        gr.Number(value=512, label="max_tokens"),
        gr.Number(value=0.7, label="temperature"),
    ],
    outputs=gr.Textbox(label="response"),
    title=f"Inference: {MODEL_ID}",
    flagging_mode="never",
    api_name="predict",
)
demo.launch()
`.trim();

const INFERENCE_REQUIREMENTS_TXT = `gradio>=4.0.0
transformers>=4.40.0
torch
accelerate>=0.26.0`.trim();

// Helper: fetch the current HEAD commit SHA of a repo's branch.
// The HF commit API requires parentCommit when the repo already has commits;
// omitting it on a non-empty repo causes a 412 Precondition Failed error.
async function getHeadCommit(
  repoType: "spaces" | "models",
  owner: string,
  name: string,
  branch: string,
  token: string,
): Promise<string | null> {
  try {
    const res = await fetch(
      `https://huggingface.co/api/${repoType}/${owner}/${name}/commits/${branch}`,
      { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(8000) },
    );
    if (!res.ok) return null;
    const data = await res.json() as any[];
    return Array.isArray(data) && data[0]?.id ? String(data[0].id) : null;
  } catch {
    return null;
  }
}

// Deploys a Gradio inference Space for a fine-tuned model.
// Returns the Space URL on success, throws on failure (so callers know it failed).
async function deployInferenceSpace(
  username: string,
  projectName: string,
  token: string,
): Promise<{ space_url: string; space_name: string }> {
  const spaceName = `inference-${projectName}`;
  const modelId   = `${username}/${projectName}`;
  const spaceUrl  = `https://huggingface.co/spaces/${username}/${spaceName}`;

  // ── 1. Create Space (idempotent — 409 means already exists) ─────────
  const createRes = await fetch("https://huggingface.co/api/repos/create", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ type: "space", name: spaceName, private: false, sdk: "gradio" }),
    signal: AbortSignal.timeout(12000),
  });
  const isNew = createRes.status === 200 || createRes.status === 201;
  if (!createRes.ok && createRes.status !== 409) {
    const e = await createRes.text().catch(() => "");
    throw new Error(`Space create failed (HTTP ${createRes.status}): ${e.slice(0, 200)}`);
  }
  console.log(`[inference-space] Space ${isNew ? "created" : "already exists"}: ${username}/${spaceName}`);

  // ── 2. Wait for git repo to initialise (only needed on fresh create) ─
  // HF backend takes 1-3 s to set up the git repo after creation.
  // Committing too early returns 404 on the commit endpoint.
  if (isNew) {
    console.log("[inference-space] Waiting 4s for repo to initialise…");
    await new Promise(r => setTimeout(r, 4000));
  }

  // ── 3. Get HEAD commit SHA (required as parentCommit) ────────────────
  // If we omit parentCommit on a non-empty repo the API returns 412.
  // On a brand-new repo it may still be empty (null is fine — omit it).
  const parentCommit = await getHeadCommit("spaces", username, spaceName, "main", token);
  console.log(`[inference-space] parentCommit=${parentCommit ?? "(none — empty repo)"}`);

  // ── 4. Commit app.py + requirements.txt ──────────────────────────────
  const toB64 = (s: string) => Buffer.from(s, "utf-8").toString("base64");
  const headerValue: Record<string, unknown> = {
    summary: `Deploy inference Space for ${modelId}`,
  };
  if (parentCommit) headerValue.parentCommit = parentCommit;

  const ndjson = [
    JSON.stringify({ key: "header", value: headerValue }),
    JSON.stringify({ key: "file", value: { path: "app.py",           encoding: "base64", content: toB64(INFERENCE_APP_PY) } }),
    JSON.stringify({ key: "file", value: { path: "requirements.txt", encoding: "base64", content: toB64(INFERENCE_REQUIREMENTS_TXT) } }),
  ].join("\n");

  const commitRes = await fetch(
    `https://huggingface.co/api/spaces/${username}/${spaceName}/commit/main`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/x-ndjson" },
      body: ndjson,
      signal: AbortSignal.timeout(30000),
    },
  );
  if (!commitRes.ok) {
    const e = await commitRes.text().catch(() => "");
    throw new Error(`Space commit failed (HTTP ${commitRes.status}): ${e.slice(0, 300)}`);
  }
  console.log(`[inference-space] ✅ app.py committed to ${username}/${spaceName}`);

  // ── 5. Set MODEL_ID and HF_TOKEN secrets ─────────────────────────────
  for (const [key, value] of [["MODEL_ID", modelId], ["HF_TOKEN", token]] as const) {
    const secretRes = await fetch(
      `https://huggingface.co/api/spaces/${username}/${spaceName}/secrets`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
        signal: AbortSignal.timeout(8000),
      },
    );
    if (!secretRes.ok) {
      console.warn(`[inference-space] secret ${key} failed: ${secretRes.status}`);
    } else {
      console.log(`[inference-space] ✅ secret ${key} set`);
    }
  }

  console.log(`[inference-space] ✅ Fully deployed: ${spaceUrl}`);
  return { space_url: spaceUrl, space_name: spaceName };
}

// Read token dynamically so it is always current regardless of when the
// env var was injected (e.g. mcp-use dashboard sets it after process start).
function getHFToken(): string {
  return process.env.HF_TOKEN || "";
}

// ── Helper: HF API fetch ──────────────────────────────────────────────
async function hfGet(url: string) {
  const token = getHFToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(url, { headers });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HF API error ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

async function hfPost(url: string, body: unknown) {
  const token = getHFToken();
  if (!token) throw new Error("HF_TOKEN environment variable is not set. Add it to your environment and restart.");
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HF API error ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

// ── Tool 1: launch_studio ─────────────────────────────────────────────
registerAppTool(
  server,
  "launch_studio",
  {
    title: "FineTune Studio",
    description:
      "Opens the FineTune Studio — an interactive dashboard for fine-tuning any Hugging Face model and chatting with it, all inside this conversation.",
    inputSchema: {},
    _meta: { ui: { resourceUri } },
  },
  async () => {
    return { content: [{ type: "text" as const, text: "" }] };
  }
);

// ── Tool 2: search_models ─────────────────────────────────────────────
registerAppTool(
  server,
  "search_models",
  {
    title: "Search HF Models",
    description: "Search Hugging Face Hub for text-generation models.",
    inputSchema: {
      query: z.string().describe("Search query"),
      limit: z.number().optional().describe("Max results, default 10"),
    },
    _meta: {},
  },
  async ({ query, limit }: { query: string; limit?: number }) => {
    try {
      const n = limit || 10;
      const url = `${HF_API}/models?search=${encodeURIComponent(query)}&limit=${n}&filter=text-generation&sort=downloads`;
      const data = await hfGet(url) as any[];
      const models = data.map((m: any) => ({
        modelId: m.modelId || m.id || "",
        author: m.author || (m.modelId || m.id || "").split("/")[0] || "",
        downloads: m.downloads || 0,
        likes: m.likes || 0,
        pipeline_tag: m.pipeline_tag || "text-generation",
        tags: (m.tags || []).filter((t: string) => !t.startsWith("arxiv:")).slice(0, 6),
        lastModified: m.lastModified || "",
      }));
      return { content: [{ type: "text" as const, text: JSON.stringify({ models }) }] };
    } catch (err: unknown) {
      return { content: [{ type: "text" as const, text: JSON.stringify({ models: [], error: String(err) }) }] };
    }
  }
);

// ── Tool 3: search_datasets ───────────────────────────────────────────
registerAppTool(
  server,
  "search_datasets",
  {
    title: "Search HF Datasets",
    description: "Search Hugging Face Hub for datasets.",
    inputSchema: {
      query: z.string().describe("Search query"),
      limit: z.number().optional().describe("Max results, default 10"),
    },
    _meta: {},
  },
  async ({ query, limit }: { query: string; limit?: number }) => {
    try {
      const n = limit || 10;
      const url = `${HF_API}/datasets?search=${encodeURIComponent(query)}&limit=${n}&sort=downloads`;
      const data = await hfGet(url) as any[];
      const datasets = data.map((d: any) => ({
        datasetId: d.id || "",
        author: d.author || (d.id || "").split("/")[0] || "",
        downloads: d.downloads || 0,
        likes: d.likes || 0,
        description: ((d.description || d.cardData?.description || "")).slice(0, 200),
        tags: (d.tags || []).slice(0, 5),
        size: d.cardData?.size_categories?.[0] || "",
      }));
      return { content: [{ type: "text" as const, text: JSON.stringify({ datasets }) }] };
    } catch (err: unknown) {
      return { content: [{ type: "text" as const, text: JSON.stringify({ datasets: [], error: String(err) }) }] };
    }
  }
);

// ── Tool 4: start_training ────────────────────────────────────────────
registerAppTool(
  server,
  "start_training",
  {
    title: "Start Training",
    description: "Start a fine-tuning job on Hugging Face AutoTrain.",
    inputSchema: {
      base_model: z.string(),
      dataset: z.string(),
      dataset_split: z.string().optional(),
      project_name: z.string(),
      task: z.string().optional(),
      hardware: z.string().optional(),
      training_type: z.string().optional(),
      chat_template: z.string().optional(),
      hyperparameters: z.object({
        epochs: z.number().optional(),
        batch_size: z.number().optional(),
        learning_rate: z.number().optional(),
        block_size: z.number().optional(),
        lora_r: z.number().optional(),
        lora_alpha: z.number().optional(),
        lora_dropout: z.number().optional(),
        quantization: z.string().optional(),
        gradient_accumulation: z.number().optional(),
        mixed_precision: z.string().optional(),
        warmup_ratio: z.number().optional(),
        weight_decay: z.number().optional(),
        target_modules: z.string().optional(),
        max_steps: z.number().optional(),
      }).optional(),
      column_mapping: z.record(z.string()).optional(),
    },
    _meta: {},
  },
  async (params: any) => {
    const token = getHFToken();
    try {
      if (!token) throw new Error("HF_TOKEN environment variable is not set.");

      // Fetch username
      const me = await hfGet("https://huggingface.co/api/whoami-v2") as any;
      const username = me.name as string;

      const hp = params.hyperparameters || {};
      const trainingType = params.training_type || "sft";

      // ── Find user's AutoTrain Advanced Space ───────────────────────────
      // HF removed the old cloud API. Training now routes through an
      // AutoTrain Advanced Space the user runs in their HF account.
      // We look for it by the standard name; if missing, return setup instructions.
      let spaceSubdomain = "";
      const AUTOTRAIN_SPACE_NAME = "autotrain-advanced";

      try {
        const spaceInfo = await hfGet(`${HF_API}/spaces/${username}/${AUTOTRAIN_SPACE_NAME}`) as any;
        // subdomain is the slug used in the .hf.space URL
        spaceSubdomain = spaceInfo.subdomain || "";
      } catch {
        // Space not found — return actionable setup instructions
        return {
          content: [{
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              setup_required: true,
              error:
                `AutoTrain Advanced Space not found in your HF account (@${username}). ` +
                `HF retired the old cloud training API. You need a one-time setup: ` +
                `go to https://huggingface.co/spaces/autotrain-projects/autotrain-advanced, ` +
                `click "Duplicate this Space", name it "${AUTOTRAIN_SPACE_NAME}", ` +
                `add your HF_TOKEN as a Space secret, then try again.`,
              setup_url: "https://huggingface.co/spaces/autotrain-projects/autotrain-advanced",
            }),
          }],
        };
      }

      if (!spaceSubdomain) {
        throw new Error(`Could not determine the URL for your AutoTrain Space (@${username}/${AUTOTRAIN_SPACE_NAME}).`);
      }

      const spaceApiBase = `https://${spaceSubdomain}.hf.space`;

      // ── Compute effective epochs (honouring max_steps if set) ────────
      // AutoTrain's API doesn't expose max_steps as a config field — it is
      // silently dropped by Pydantic. We implement it ourselves by fetching the
      // dataset split size and converting max_steps → a fractional epoch count.
      //   effective_epochs = min(max_steps, steps_per_epoch × config_epochs)
      //                      ÷ steps_per_epoch
      const configEpochs   = hp.epochs ?? 2;
      const batchSize      = hp.batch_size ?? 1;
      const gradAcc        = hp.gradient_accumulation ?? 4;

      // When max_steps is set, fetch dataset size so we can calculate the minimum
      // number of *integer* epochs needed for those steps to be reachable.
      // AutoTrain requires epochs to be an integer and passes max_steps directly
      // to HF Trainer which stops training at min(max_steps, total_steps).
      let maxStepsEpochs: number | null = null; // integer epochs needed
      if (hp.max_steps && hp.max_steps > 0 && params.dataset) {
        const dsEnc   = encodeURIComponent(params.dataset);
        const splitKey = params.dataset_split || "train";
        let trainRows: number | null = null;

        try {
          const r = await fetch(
            `https://datasets-server.huggingface.co/info?dataset=${dsEnc}`,
            { headers: token ? { Authorization: `Bearer ${token}` } : {}, signal: AbortSignal.timeout(8000) }
          );
          const d = await r.json() as any;
          const info   = d?.dataset_info ?? {};
          const splits = info.splits ?? info[Object.keys(info)[0]]?.splits ?? {};
          trainRows    = splits[splitKey]?.num_examples ?? splits.train?.num_examples ?? null;
        } catch { /* ignore */ }

        if (trainRows && trainRows > 0) {
          const stepsPerEpoch = Math.ceil(trainRows / batchSize) / gradAcc;
          // Minimum whole epochs needed so max_steps can actually be reached
          maxStepsEpochs = Math.max(1, Math.ceil(hp.max_steps / stepsPerEpoch));
          console.log(`[max_steps] rows=${trainRows} stepsPerEpoch=${stepsPerEpoch.toFixed(0)} maxStepsEpochs=${maxStepsEpochs}`);
        } else {
          console.warn(`[max_steps] could not fetch dataset size for "${params.dataset}" — using epochs=${configEpochs}`);
        }
      }

      // ── Build the training request body ───────────────────────────────
      // Note: `push_to_hub` must be at the TOP LEVEL — AutoTrain ignores it
      // when nested inside `params` (silently dropped by Pydantic). Same pattern
      // as `username` and `token` which also live at top level and flow through
      // to the training config.
      const body: Record<string, unknown> = {
        username,
        project_name: params.project_name,
        task: params.task || "llm:sft",
        base_model: params.base_model,
        hub_dataset: params.dataset,
        train_split: params.dataset_split || "train",
        hardware: params.hardware || "spaces-a10g-large",
        column_mapping: params.column_mapping || { text_column: "text" },
        // push_to_hub must live inside a top-level "hub" object —
        // the API ignores it when nested in "params" or bare at the top level.
        hub: {
          username,
          token,
          push_to_hub: true,
        },
        hub_model: `${username}/${params.project_name}`,
        token,   // also kept at top level for the Space auth header
        params: {
          epochs: maxStepsEpochs ?? Math.max(1, Math.round(configEpochs)),
          batch_size: hp.batch_size ?? 1,
          lr: hp.learning_rate ?? 0.0002,
          block_size: hp.block_size ?? 1024,
          peft: true,
          quantization: hp.quantization ?? "int4",
          mixed_precision: hp.mixed_precision ?? "bf16",
          lora_r: hp.lora_r ?? 16,
          lora_alpha: hp.lora_alpha ?? 32,
          lora_dropout: hp.lora_dropout ?? 0.05,
          gradient_accumulation: hp.gradient_accumulation ?? 4,
          warmup_ratio: hp.warmup_ratio ?? 0.1,
          weight_decay: hp.weight_decay ?? 0.01,
          target_modules: hp.target_modules ?? "all-linear",
          // "none" means a plain-text dataset — omit the field so AutoTrain
          // skips apply_chat_template (avoids the ast.literal_eval SyntaxError).
          ...(params.chat_template && params.chat_template !== "none"
            ? { chat_template: params.chat_template }
            : {}),
          trainer: trainingType,
          merge_adapter: true,  // merge LoRA weights into base model before push
          ...(hp.max_steps && hp.max_steps > 0 ? { max_steps: Math.round(hp.max_steps) } : {}),
        },
      };

      // ── POST to the user's AutoTrain Space API ─────────────────────────
      const res = await fetch(`${spaceApiBase}/api/create_project`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        throw new Error(`AutoTrain Space API error ${res.status}: ${errText.slice(0, 300)}`);
      }

      const result = await res.json() as any;

      // ── Inject push_to_hub=true directly into the training Space secret ──
      //
      // Root cause (confirmed by reading AutoTrain source):
      //   SpaceRunner._add_secrets() serialises LLMTrainingParams → JSON and stores
      //   it as the PARAMS env secret on the training sub-Space
      //   (e.g. autotrain-{project_name}).  LLMTrainingParams.push_to_hub defaults
      //   to False, and because push_to_hub is in FIELDS_TO_EXCLUDE the API body
      //   can never override it.  The training script reads os.environ["PARAMS"],
      //   deserialises it, and honours push_to_hub — so updating the secret to
      //   True is the definitive fix.
      //
      // Timing: create_project is synchronous — by the time it returns the
      //   training Space already exists with its secrets set.  Updating a secret
      //   triggers a Space restart (HF behaviour).  Since the Space is still in
      //   its 2-5 min build phase this restart is free; it re-builds and starts
      //   training with push_to_hub=True.
      const trainingSpaceName = `autotrain-${params.project_name}`;
      const textCol = (params.column_mapping as Record<string, string>)?.text_column || "text";
      const effectiveEpochs = maxStepsEpochs ?? Math.max(1, Math.round(configEpochs));

      // Build the LLMTrainingParams-compatible JSON that the training script
      // deserialises from the PARAMS secret.  Extra/unknown keys are fine —
      // LLMTrainingParams(**json) ignores them via Pydantic's default behaviour.
      const paramsSecret: Record<string, unknown> = {
        model:                params.base_model,
        project_name:         params.project_name,
        username,
        token,
        data_path:            params.dataset,
        train_split:          params.dataset_split || "train",
        text_column:          textCol,
        push_to_hub:          true,        // ← THE FIX
        log:                  "tensorboard",
        epochs:               effectiveEpochs,
        batch_size:           hp.batch_size ?? 1,
        lr:                   hp.learning_rate ?? 0.0002,
        block_size:           hp.block_size ?? 1024,
        peft:                 true,
        quantization:         hp.quantization ?? "int4",
        mixed_precision:      hp.mixed_precision ?? "bf16",
        lora_r:               hp.lora_r ?? 16,
        lora_alpha:           hp.lora_alpha ?? 32,
        lora_dropout:         hp.lora_dropout ?? 0.05,
        gradient_accumulation: hp.gradient_accumulation ?? 4,
        warmup_ratio:         hp.warmup_ratio ?? 0.1,
        weight_decay:         hp.weight_decay ?? 0.01,
        target_modules:       hp.target_modules ?? "all-linear",
        trainer:              trainingType,
        merge_adapter:        true,
        padding:              "right",
        chat_template:        (params.chat_template && params.chat_template !== "none")
                                ? params.chat_template : "none",
        ...(hp.max_steps && hp.max_steps > 0 ? { max_steps: Math.round(hp.max_steps) } : {}),
      };

      // POST to HF Hub Secrets API — same endpoint/method used by huggingface_hub
      // Python library's add_space_secret().
      try {
        const secretRes = await fetch(
          `https://huggingface.co/api/spaces/${username}/${trainingSpaceName}/secrets`,
          {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ key: "PARAMS", value: JSON.stringify(paramsSecret) }),
            signal: AbortSignal.timeout(10000),
          }
        );
        if (secretRes.ok) {
          console.log(`[push_to_hub] ✅ PARAMS secret updated on ${trainingSpaceName} — push_to_hub=true`);
        } else {
          const errBody = await secretRes.text().catch(() => "");
          console.warn(`[push_to_hub] ⚠️  Secret update HTTP ${secretRes.status}: ${errBody.slice(0, 200)}`);
        }
      } catch (secretErr) {
        // Non-fatal — training will proceed, just may not push to Hub
        console.warn(`[push_to_hub] ⚠️  Could not update PARAMS secret: ${secretErr}`);
      }

      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            success: true,
            project_id: result.id || result.project_id || params.project_name,
            // AutoTrain creates the training Space with "autotrain-" prefix
            space_url: `https://huggingface.co/spaces/${username}/autotrain-${params.project_name}`,
            autotrain_space_url: `https://huggingface.co/spaces/${username}/${AUTOTRAIN_SPACE_NAME}`,
            model_url: `https://huggingface.co/${username}/${params.project_name}`,
            username,
            status: "starting",
          }),
        }],
      };
    } catch (err: unknown) {
      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            success: false,
            error: err instanceof Error ? err.message : String(err),
          }),
        }],
      };
    }
  }
);

// ── Tool 5: check_training_status ─────────────────────────────────────
registerAppTool(
  server,
  "check_training_status",
  {
    title: "Check Training Status",
    description: "Poll the status of a running AutoTrain fine-tuning job.",
    inputSchema: {
      project_name: z.string(),
      username: z.string().optional(),
    },
    _meta: {},
  },
  async ({ project_name, username }: { project_name: string; username?: string }) => {
    try {
      let user = username;
      if (!user) {
        const me = await hfGet("https://huggingface.co/api/whoami-v2") as any;
        user = me.name as string;
      }

      const stageMap: Record<string, string> = {
        RUNNING: "training",
        BUILDING: "starting",
        STOPPED: "completed",
        ERROR: "error",
        SLEEPING: "starting",
        PAUSED: "starting",
        NO_APP_FILE: "starting",
        CONFIG_ERROR: "error",
        APP_STARTING: "starting",
      };

      // AutoTrain names the training Space "autotrain-{project_name}".
      // After training it renames the space to "{project_name}" (drops prefix).
      // We poll with the autotrain- prefix while it's running; the JWT in the
      // container logs confirms: sub = /spaces/avi81/autotrain-{project_name}.
      const trainingSpaceName = `autotrain-${project_name}`;

      let rawStage = "BUILDING";
      let status = "starting";
      let spaceSubdomain = "";
      try {
        // Fetch the Space info (includes subdomain we need for logs)
        const spaceInfo = await hfGet(`${HF_API}/spaces/${user}/${trainingSpaceName}`) as any;
        spaceSubdomain = spaceInfo.subdomain || "";
        // Also fetch runtime for the live stage
        const runtime = await hfGet(`${HF_API}/spaces/${user}/${trainingSpaceName}/runtime`) as any;
        rawStage = runtime.stage || "BUILDING";
        status = stageMap[rawStage] || "starting";
      } catch (runtimeErr: unknown) {
        const msg = String(runtimeErr);
        // 404 = Space not yet provisioned by AutoTrain — keep as "starting"
        if (!msg.includes("404")) {
          status = "error";
          rawStage = "ERROR";
        }
      }
      // AutoTrain pauses its Space when training finishes, so PAUSED / STOPPED
      // alone can't distinguish "not-started-yet" from "just-finished".
      // We disambiguate by looking for shutdown / cleanup log lines.
      // This is applied AFTER logs are collected below, so we store the
      // preliminary status and patch it if needed.
      const preliminaryStatus = status;

      // ── Fetch container logs via HF Hub SSE endpoint ─────────────────
      // Correct endpoint is /logs/run (not /logs).
      // Streams SSE events: data: {"type":"stdout","text":"<line>\n"}
      let logs = "";
      let logsDebug = "";
      const token = getHFToken();
      const logsUrl = `${HF_API}/spaces/${user}/${trainingSpaceName}/logs/run`;
      try {
        const logRes = await fetch(logsUrl, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          signal: AbortSignal.timeout(8000),
        });
        logsDebug = `[logs fetch: HTTP ${logRes.status}]`;
        if (logRes.ok && logRes.body) {
          const reader = logRes.body.getReader();
          const decoder = new TextDecoder();
          let raw = "";

          // Hard-cancel the reader after 4 s — reader.cancel() causes
          // reader.read() to reject, which is our signal to stop.
          const cancelTimer = setTimeout(
            () => reader.cancel("timeout").catch(() => {}),
            4000
          );
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              raw += decoder.decode(value, { stream: true });
            }
          } catch {
            // reader.cancel() threw — normal exit path
          } finally {
            clearTimeout(cancelTimer);
          }

          logsDebug += ` [raw bytes: ${raw.length}]`;

          // Parse SSE lines: "data: {"type":"stdout","text":"log line\n"}"
          const ansiRe = /\x1b\[[0-9;]*m/g;
          logs = raw
            .split("\n")
            .filter(l => l.startsWith("data:"))
            .map(l => {
              const payload = l.slice(5).trim();
              if (!payload) return "";
              try {
                const obj = JSON.parse(payload) as any;
                if (obj.type === "run") return "";
                return String(obj.text ?? obj.data ?? payload)
                  .replace(/\n$/, "")
                  .replace(ansiRe, "");
              } catch {
                return payload.replace(ansiRe, "");
              }
            })
            .filter(Boolean)
            .join("\n");
        } else {
          const errBody = await logRes.text().catch(() => "");
          logsDebug += ` [body: ${errBody.slice(0, 200)}]`;
        }
      } catch (logErr: unknown) {
        logsDebug = `[logs fetch error: ${String(logErr)}]`;
      }

      // ── Patch status using log content ────────────────────────────────
      // AutoTrain pauses the Space after training completes.  The PAUSED stage
      // alone is ambiguous (could be "not started yet").  If the logs contain
      // AutoTrain / HF Trainer shutdown signatures we know training finished.
      if (preliminaryStatus !== "training" && preliminaryStatus !== "error") {
        const completionRe = /SIGTERM|graceful\.exit|Application\.shutdown|Training complete|model.*pushed|Pausing space|pause_space/i;
        if (completionRe.test(logs)) {
          status = "completed";
        }
      }

      // Parse metrics from logs — handle both 'key': val and key: val formats.
      // AutoTrain logs: {'loss': 9.73, 'learning_rate': 0.0002, 'epoch': 0.02}
      // Always use the LAST match so stale early-epoch values don't stick.
      const lastMatch = (text: string, ...patterns: RegExp[]) => {
        for (const re of patterns) {
          const all = [...text.matchAll(new RegExp(re.source, re.flags.replace("g","") + "g"))];
          if (all.length > 0) return all[all.length - 1];
        }
        return null;
      };
      const lossMatch       = lastMatch(logs, /'loss':\s*([0-9]+\.[0-9]+)/, /(?:train_)?loss[:\s=]+([0-9]+\.[0-9]+)/i);
      const epochMatch      = lastMatch(logs, /'epoch':\s*([0-9]+(?:\.[0-9]*)?)/, /epoch[:\s]+([0-9]+\.?[0-9]*)/i);
      const lrMatch         = lastMatch(logs, /'learning_rate':\s*([0-9.e+\-]+)/, /(?:learning_rate|lr)[:\s=]+([0-9.e+\-]+)/i);
      // tqdm uses \r to overwrite lines, so only the initial 0/N line arrives cleanly.
      // Send totalSteps to the client so it can compute current step as:
      //   step = round((epoch / config.epochs) * totalSteps)
      // (epoch goes 0→config.epochs continuously, totalSteps spans all epochs)
      const totalStepsMatch = lastMatch(logs, /\d+\/(\d+)\s*\[/);
      const totalSteps = totalStepsMatch ? parseInt(totalStepsMatch[1]) : null;

      // ── Auto-publish model when training completes ─────────────────────
      // AutoTrain hardcodes private=True when creating the model repo.
      // We flip it to public so the inference Space can access it.
      // This is a one-shot operation: the HF API ignores it if already public.
      let madePublic = false;
      let inferenceSpaceResult: { space_url: string; space_name: string } | null = null;

      if (status === "completed" && token) {
        try {
          const pubRes = await fetch(
            `https://huggingface.co/api/models/${user}/${project_name}/settings`,
            {
              method: "PUT",
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ private: false }),
              signal: AbortSignal.timeout(8000),
            }
          );
          madePublic = pubRes.ok;
          if (pubRes.ok) {
            console.log(`[visibility] ✅ ${user}/${project_name} set to public`);
          } else {
            const t = await pubRes.text().catch(() => "");
            console.warn(`[visibility] ⚠️  HTTP ${pubRes.status}: ${t.slice(0, 200)}`);
          }
        } catch (pubErr) {
          console.warn(`[visibility] ⚠️  ${pubErr}`);
        }

        // ── Deploy inference Space ─────────────────────────────────────
        // HF serverless inference (inferenceProviderMapping) no longer serves
        // arbitrary custom fine-tuned models. We work around this by deploying
        // a small Gradio Space that loads the model with transformers directly.
        // The Space name is inference-{project_name}.
        try {
          inferenceSpaceResult = await deployInferenceSpace(user, project_name, token);
        } catch (spaceErr) {
          console.warn(`[inference-space] deployment failed: ${spaceErr}`);
        }
      }

      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            status,
            stage: rawStage,
            training_space: `https://huggingface.co/spaces/${user}/${trainingSpaceName}`,
            logs: (logsDebug ? logsDebug + "\n" : "") + logs.slice(-4000),
            metrics: {
              loss: lossMatch ? parseFloat(lossMatch[1]) : null,
              epoch: epochMatch ? parseFloat(epochMatch[1]) : null,
              totalSteps,
              learning_rate: lrMatch ? parseFloat(lrMatch[1]) : null,
            },
            ...(status === "completed" ? {
              model_made_public: madePublic,
              inference_space_url: inferenceSpaceResult?.space_url ?? null,
              inference_space_name: inferenceSpaceResult?.space_name ?? null,
            } : {}),
          }),
        }],
      };
    } catch (err: unknown) {
      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({ status: "error", error: String(err) }),
        }],
      };
    }
  }
);

// ── Tool 6: chat_with_model ───────────────────────────────────────────
registerAppTool(
  server,
  "chat_with_model",
  {
    title: "Chat with Model",
    description: "Send messages to a Hugging Face model via the inference API and get a response.",
    inputSchema: {
      model_id: z.string().describe("HF model ID, e.g. meta-llama/Llama-3.2-3B-Instruct"),
      messages: z.array(z.object({
        role: z.enum(["system", "user", "assistant"]),
        content: z.string(),
      })),
      parameters: z.object({
        temperature: z.number().optional(),
        top_p: z.number().optional(),
        max_tokens: z.number().optional(),
      }).optional(),
    },
    _meta: {},
  },
  async ({ model_id, messages, parameters }: {
    model_id: string;
    messages: Array<{ role: "system" | "user" | "assistant"; content: string }>;
    parameters?: { temperature?: number; top_p?: number; max_tokens?: number };
  }) => {
    try {
      const token = getHFToken();
      if (!token) throw new Error("HF_TOKEN environment variable is not set.");

      const chatBody = {
        model: model_id,
        messages,
        temperature: parameters?.temperature ?? 0.7,
        max_tokens: parameters?.max_tokens ?? 512,
        top_p: parameters?.top_p ?? 0.9,
        stream: false,
      };

      // ── Inference strategy — four attempts in order ────────────────────
      //
      //  0. Dedicated Inference Space ({owner}/inference-{model_name}).
      //     We auto-deploy this Gradio Space after training completes.
      //     It loads the model with transformers directly — works for ANY
      //     Hub model regardless of HF's inferenceProviderMapping.
      //     This is the primary path for custom fine-tuned models.
      //
      //  1. HF Inference Router (router.huggingface.co).
      //     Works for popular public models supported by providers.
      //
      //  2. HF per-model Messages API (api-inference.huggingface.co /v1/chat).
      //     Works for public models indexed by HF's TGI fleet.
      //
      //  3. HF Legacy Text-Generation API (api-inference.huggingface.co /models).
      //     Last resort for public models that support the older endpoint.

      let responseText = "";

      // ── Attempt 0: Dedicated Inference Space (Gradio 4.x raw HTTP API) ──
      // For custom fine-tuned models we auto-deploy a Gradio Space post-training
      // named {owner}/inference-{model_name}.
      //
      // Gradio 4.x dropped the old /api/predict sync endpoint.  The current API is:
      //   POST /gradio_api/call/predict  → {"event_id": "abc"}
      //   GET  /gradio_api/call/predict/{event_id} → SSE "event: complete\ndata: [...]"
      //
      // We use raw HTTP so we have full control over errors (the @gradio/client
      // package silently swallows connection errors which masked failures).
      if (!responseText && model_id.includes("/")) {
        const [owner, modelName] = model_id.split("/");
        const inferSpaceName = `inference-${modelName}`;

        // ── 1. Does the Space exist? Get subdomain while we're at it. ────
        const spaceInfoRes = await fetch(
          `${HF_API}/spaces/${owner}/${inferSpaceName}`,
          { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(8000) },
        ).catch(() => null);

        if (spaceInfoRes?.ok) {
          const spaceData = await spaceInfoRes.json() as any;
          const subdomain = spaceData.subdomain as string | undefined;

          // ── 2. Check runtime stage ──────────────────────────────────
          const runtimeRes = await fetch(
            `${HF_API}/spaces/${owner}/${inferSpaceName}/runtime`,
            { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(8000) },
          ).catch(() => null);

          // If the runtime endpoint returns 404, the Space was just created and
          // hasn't started its build cycle yet — treat it as BUILDING.
          const stage: string = runtimeRes?.ok
            ? (((await runtimeRes.json()) as any).stage || "UNKNOWN")
            : "BUILDING";

          console.log(`[chat] inference-space ${owner}/${inferSpaceName} stage=${stage}`);

          if (["BUILDING", "APP_STARTING", "STARTING", "NO_APP_FILE", "UNKNOWN"].includes(stage)) {
            throw new Error(
              `⏳ Your inference Space (${owner}/${inferSpaceName}) is still building — ` +
              `takes 2–3 min on first deploy. Please wait and try again.\n` +
              `Track progress: https://huggingface.co/spaces/${owner}/${inferSpaceName}`,
            );
          }

          if (stage === "SLEEPING") {
            throw new Error(
              `😴 Your inference Space (${owner}/${inferSpaceName}) was sleeping and is now waking up. ` +
              `Please wait ~1 minute and try again.`,
            );
          }

          if (stage === "RUNNING" && subdomain) {
            // ── 3. POST to Gradio 4.x queue endpoint ─────────────────
            const gradioBase = `https://${subdomain}.hf.space/gradio_api/call/predict`;
            const submitRes = await fetch(gradioBase, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                // gr.Interface uses positional parameters — same order as fn signature:
                // predict(messages_json, max_tokens, temperature)
                data: [
                  JSON.stringify(messages),
                  chatBody.max_tokens,
                  chatBody.temperature,
                ],
              }),
              signal: AbortSignal.timeout(30000),
            });

            if (!submitRes.ok) {
              const b = await submitRes.text().catch(() => "");
              throw new Error(
                `Inference Space submit failed (HTTP ${submitRes.status}): ${b.slice(0, 200)}`,
              );
            }

            const { event_id } = await submitRes.json() as { event_id: string };
            if (!event_id) throw new Error("Inference Space did not return an event_id");

            // ── 4. Stream SSE result ───────────────────────────────────
            const sseRes = await fetch(`${gradioBase}/${event_id}`, {
              signal: AbortSignal.timeout(180_000), // 3 min — first inference on CPU is slow
            });

            if (!sseRes.ok) {
              throw new Error(`Inference Space SSE failed (HTTP ${sseRes.status})`);
            }

            const reader = sseRes.body!.getReader();
            const decoder = new TextDecoder();
            let buf = "";

            parseSSE: while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              buf += decoder.decode(value, { stream: true });

              for (const chunk of buf.split("\n\n")) {
                const eventLine = chunk.split("\n").find(l => l.startsWith("event:"))?.slice(7).trim() ?? "";
                const dataLine  = chunk.split("\n").find(l => l.startsWith("data:"))?.slice(6).trim()  ?? "";

                if (eventLine === "error") {
                  throw new Error(`Inference Space error: ${dataLine.slice(0, 200)}`);
                }
                if (eventLine === "complete" && dataLine) {
                  const parsed = JSON.parse(dataLine);
                  const resp = String(parsed?.[0] ?? "");
                  if (resp.startsWith("Error:")) {
                    throw new Error(`Inference Space returned: ${resp}`);
                  }
                  responseText = resp;
                  reader.cancel().catch(() => {});
                  break parseSSE;
                }
              }

              // Keep only the last incomplete chunk
              buf = buf.includes("\n\n") ? buf.slice(buf.lastIndexOf("\n\n") + 2) : buf;
            }
          } else if (!["STOPPED", "PAUSED", "ERROR", "CONFIG_ERROR"].includes(stage)) {
            // Unexpected stage — tell the user rather than silently failing
            throw new Error(
              `Inference Space (${owner}/${inferSpaceName}) is in an unexpected state: ${stage}. ` +
              `Check https://huggingface.co/spaces/${owner}/${inferSpaceName}`,
            );
          }
          // STOPPED / PAUSED / ERROR / CONFIG_ERROR → fall through to HF inference attempts
        }
        // Space doesn't exist (404) → fall through silently to HF inference attempts
      }

      // ── Attempt 1: HF Inference Router ────────────────────────────────
      if (!responseText) {
        const routerModel = model_id.includes(":") ? model_id : `${model_id}:fastest`;
        const res1 = await fetch(HF_ROUTER_URL, {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({ ...chatBody, model: routerModel }),
        });
        if (res1.ok) {
          const d = await res1.json() as any;
          responseText = d.choices?.[0]?.message?.content || "";
        } else {
          if (res1.status === 401 || res1.status === 403) {
            throw new Error(`Access denied for "${model_id}". Check your HF_TOKEN and model license.`);
          }
          // 404 / "not supported by any provider" → try next endpoint
        }
      }

      // ── Attempt 2: Messages API (chat-completions style) ──────────────
      if (!responseText) {
        const url2 = `https://api-inference.huggingface.co/models/${model_id}/v1/chat/completions`;
        const res2 = await fetch(url2, {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({ ...chatBody, model: model_id }),
        });
        if (res2.ok) {
          const d2 = await res2.json() as any;
          responseText = d2.choices?.[0]?.message?.content || "";
        }
        // 404 or 503 → fall through to attempt 3
      }

      // ── Attempt 3: Legacy Text-Generation API ─────────────────────────
      if (!responseText) {
        const promptParts: string[] = [];
        for (const msg of messages) {
          if (msg.role === "system") {
            promptParts.push(`<|im_start|>system\n${msg.content}<|im_end|>`);
          } else if (msg.role === "user") {
            promptParts.push(`<|im_start|>user\n${msg.content}<|im_end|>`);
          } else {
            promptParts.push(`<|im_start|>assistant\n${msg.content}<|im_end|>`);
          }
        }
        promptParts.push("<|im_start|>assistant\n");
        const prompt = promptParts.join("\n");

        const url3 = `https://api-inference.huggingface.co/models/${model_id}`;
        const res3 = await fetch(url3, {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({
            inputs: prompt,
            parameters: {
              max_new_tokens: chatBody.max_tokens,
              temperature: chatBody.temperature,
              top_p: chatBody.top_p,
              return_full_text: false,
              do_sample: true,
            },
          }),
        });

        if (!res3.ok) {
          const b3 = await res3.text().catch(() => "");
          if (res3.status === 404) {
            // Check whether we deployed an inference Space for this model
            const hasInferenceSpace = model_id.includes("/");
            const [owner2, modelName2] = hasInferenceSpace ? model_id.split("/") : ["", ""];
            throw new Error(
              hasInferenceSpace
                ? `Model "${model_id}" is not yet available via HF serverless inference. ` +
                  `An inference Space (${owner2}/inference-${modelName2}) was deployed for you — ` +
                  `it takes 2–3 min to start. Check https://huggingface.co/spaces/${owner2}/inference-${modelName2}`
                : `Model "${model_id}" was not found on the Hugging Face Hub. ` +
                  `Verify it exists at https://huggingface.co/${model_id}`
            );
          }
          if (res3.status === 503 || b3.includes("loading") || b3.includes("estimated_time")) {
            const eta = (() => { try { return JSON.parse(b3).estimated_time; } catch { return null; } })();
            throw new Error(
              `Model "${model_id}" is warming up${eta ? ` (~${Math.ceil(eta)}s)` : ""}. ` +
              `Please try again in a moment.`
            );
          }
          throw new Error(`Inference failed (HTTP ${res3.status}): ${b3.slice(0, 300)}`);
        }

        const d3 = await res3.json() as any;
        const raw = Array.isArray(d3) ? d3[0]?.generated_text : d3?.generated_text;
        responseText = (raw || "").replace(/^<\|im_start\|>assistant\n?/, "").trim();
      }

      if (!responseText) {
        throw new Error(`No response from "${model_id}". The model may not support text generation via the HF Inference API.`);
      }

      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({ text: responseText, model_id }),
        }],
      };
    } catch (err: unknown) {
      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// ── Tool 7: deploy_inference_space ───────────────────────────────────────
registerAppTool(
  server,
  "deploy_inference_space",
  {
    title: "Deploy Inference Space",
    description:
      "Manually deploy (or redeploy) a Gradio inference Space for a fine-tuned model. " +
      "The Space loads the model with transformers and exposes an API endpoint, " +
      "bypassing the HF serverless inference provider limitation.",
    inputSchema: {
      project_name: z.string().describe("The project / model name (without username prefix)"),
    },
    _meta: {},
  },
  async ({ project_name }: { project_name: string }) => {
    try {
      const token = getHFToken();
      if (!token) throw new Error("HF_TOKEN is not set.");
      const me = await hfGet("https://huggingface.co/api/whoami-v2") as any;
      const username = me.name as string;

      const result = await deployInferenceSpace(username, project_name, token);

      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            success: true,
            message: "✅ Inference Space deployed! It takes 2–3 min to build and load the model.",
            space_url: result.space_url,
            space_name: result.space_name,
          }),
        }],
      };
    } catch (err: unknown) {
      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({ success: false, error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// ── Tool 8: patch_autotrain_space ─────────────────────────────────────
// Fixes the push_to_hub=False bug present in autotrain-advanced ≤ 0.8.36.
// Strategy: add a sitecustomize.py monkey-patch to the user's AutoTrain Space
// repo so Python auto-imports it at startup and forces push_to_hub=True before
// any training job runs.
registerAppTool(
  server,
  "patch_autotrain_space",
  {
    title: "Patch AutoTrain Space (Fix Push to Hub)",
    description:
      "One-click fix for the autotrain-advanced push_to_hub=False bug. " +
      "Commits a sitecustomize.py monkey-patch and updated Dockerfile to your " +
      "AutoTrain Space so future training jobs automatically push to the Hub.",
    inputSchema: {},
    _meta: {},
  },
  async () => {
    try {
      const token = getHFToken();
      if (!token) throw new Error("HF_TOKEN is not set.");

      const me = await hfGet("https://huggingface.co/api/whoami-v2") as any;
      const username = me.name as string;
      const AUTOTRAIN_SPACE_NAME = "autotrain-advanced";
      const spaceRepo = `${username}/${AUTOTRAIN_SPACE_NAME}`;

      // ── Why the previous sitecustomize.py approach failed ─────────────
      // Python's site.getsitepackages()[0] often points to a dist-packages
      // directory the autotrain interpreter doesn't check first.  The reliable
      // alternative is to DIRECTLY REWRITE the installed params.py source file
      // on disk after each `pip install`, then also clear the .pyc cache so
      // Python recompiles from the patched source.

      // ── 1. fix_push_to_hub.py — run once after pip install ─────────────
      const fixScript = `"""
Patch autotrain-advanced so that every training job pushes to the Hub.

Root cause (all versions <= 0.8.36):
  PARAMS["llm"] is built from LLMTrainingParams().model_dump() which always
  includes push_to_hub=False.  The guard in _munge_common_params:
      if "push_to_hub" not in _params:
          _params["push_to_hub"] = True
  never fires because the key IS already present (as False).

Fix: rewrite the installed params.py so the guard becomes unconditional.
"""
import importlib, inspect, os, re, sys

# ── locate params.py ──────────────────────────────────────────────────
import autotrain.app.params as _m
src = inspect.getfile(_m)
print(f"[push_to_hub patch] target: {src}", flush=True)

with open(src) as fh:
    code = fh.read()

# ── apply patch ───────────────────────────────────────────────────────
# Match the conditional block regardless of exact indentation.
PATTERN = r'([ \\t]+)if ["\\'\\']push_to_hub["\\'\\'] not in _params:[\\s\\S]*?_params["\\'\\']["\\'\\']push_to_hub["\\'\\']["\\'\\'] = True'
REPLACEMENT = r'\\1_params["push_to_hub"] = True  # patched: force hub push'

patched_code, n = re.subn(PATTERN, REPLACEMENT, code)

if n > 0:
    with open(src, "w") as fh:
        fh.write(patched_code)
    # Bust the bytecode cache so the interpreter picks up the new source.
    cache_dir = os.path.join(os.path.dirname(src), "__pycache__")
    if os.path.isdir(cache_dir):
        removed = [
            os.remove(os.path.join(cache_dir, f))
            for f in os.listdir(cache_dir)
            if f.startswith("params") and f.endswith(".pyc")
        ]
    print(f"[push_to_hub patch] ✅ params.py patched ({n} substitution(s))", flush=True)
elif "# patched: force hub push" in code:
    print("[push_to_hub patch] ✅ params.py already patched", flush=True)
else:
    # Fallback: try a simpler literal replacement (handles minor whitespace diffs).
    SIMPLE_OLD = '        if "push_to_hub" not in _params:\\n            _params["push_to_hub"] = True'
    SIMPLE_NEW = '        _params["push_to_hub"] = True  # patched: force hub push'
    if SIMPLE_OLD in code:
        with open(src, "w") as fh:
            fh.write(code.replace(SIMPLE_OLD, SIMPLE_NEW))
        print("[push_to_hub patch] ✅ params.py patched (literal fallback)", flush=True)
    else:
        print(f"[push_to_hub patch] ⚠️  Could not locate patch target in {src}.", file=sys.stderr, flush=True)
        print("[push_to_hub patch]    Inspecting file…", file=sys.stderr, flush=True)
        for i, line in enumerate(code.splitlines(), 1):
            if "push_to_hub" in line:
                print(f"  L{i}: {line!r}", file=sys.stderr, flush=True)
`;

      // ── 2. Dockerfile ───────────────────────────────────────────────────
      const dockerfileContent = `FROM huggingface/autotrain-advanced:latest
COPY fix_push_to_hub.py /tmp/fix_push_to_hub.py
CMD pip uninstall -y autotrain-advanced && \\
    pip install -U autotrain-advanced && \\
    python /tmp/fix_push_to_hub.py && \\
    autotrain app --host 0.0.0.0 --port 7860 --workers 1
`;

      // ── 3. Commit both files to the Space repo ─────────────────────────
      const toB64 = (s: string) => Buffer.from(s, "utf-8").toString("base64");

      const ndjson = [
        JSON.stringify({
          key: "header",
          value: {
            summary: "Fix push_to_hub=False: rewrite params.py after pip install",
            description:
              "Replace fragile sitecustomize.py approach with direct source-file " +
              "rewrite of autotrain/app/params.py after each pip install. " +
              "Clears .pyc cache so the patched source is used immediately.",
          },
        }),
        JSON.stringify({
          key: "file",
          value: { path: "fix_push_to_hub.py", encoding: "base64", content: toB64(fixScript) },
        }),
        JSON.stringify({
          key: "file",
          value: { path: "Dockerfile", encoding: "base64", content: toB64(dockerfileContent) },
        }),
      ].join("\n");

      const commitRes = await fetch(
        `https://huggingface.co/api/spaces/${spaceRepo}/commit/main`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/x-ndjson",
          },
          body: ndjson,
        }
      );

      if (!commitRes.ok) {
        const errText = await commitRes.text().catch(() => "");
        throw new Error(`HF Hub commit failed (HTTP ${commitRes.status}): ${errText.slice(0, 400)}`);
      }

      const commitData = await commitRes.json() as any;

      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            success: true,
            message:
              "✅ Patch committed! Your AutoTrain Space is rebuilding (~2-3 min). " +
              "Once it's back online, new training jobs will automatically push " +
              "the fine-tuned model to the Hub.",
            space_url: `https://huggingface.co/spaces/${spaceRepo}`,
            commit_url: commitData.commitUrl || `https://huggingface.co/spaces/${spaceRepo}/commit/main`,
            next_step:
              "Wait for the Space status to go green, then start a new training run.",
          }),
        }],
      };
    } catch (err: unknown) {
      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            success: false,
            error: err instanceof Error ? err.message : String(err),
          }),
        }],
      };
    }
  }
);

// ── Resource ──────────────────────────────────────────────────────────
registerAppResource(
  server,
  resourceUri,
  resourceUri,
  { mimeType: RESOURCE_MIME_TYPE, _meta: { ui: { csp: { resourceDomains: [] }, permissions: { openLinks: {} } } } },
  async () => {
    const html = await fs.readFile(
      path.join(__dirname, "dist", "widget.html"),
      "utf-8"
    );
    return { contents: [{ uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html }] };
  }
);

// ── Express server ────────────────────────────────────────────────────
const expressApp = express();
expressApp.use(cors());
expressApp.use(express.json({ limit: "10mb" }));

// Health check — required by many cloud platforms and MCP hosts
expressApp.get("/", (_req, res) => {
  res.json({ name: "FineTune Studio MCP", status: "ok", version: "1.0.0" });
});

// Some MCP hosts probe GET /mcp before connecting
expressApp.get("/mcp", (_req, res) => {
  res.json({ name: "FineTune Studio MCP", status: "ok" });
});

expressApp.post("/mcp", async (req, res) => {
  try {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });
    res.on("close", () => transport.close());
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (err) {
    console.error("MCP handler error:", err);
    if (!res.headersSent) {
      res.status(500).json({ error: "Internal server error" });
    }
  }
});

const PORT = process.env.PORT || 3002;
expressApp.listen(PORT, () =>
  console.log(`FineTune Studio MCP Server running at http://localhost:${PORT}/mcp`)
);
