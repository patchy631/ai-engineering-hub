/**
 * LLM Configuration
 *
 * Configure available LLM providers and models
 * API keys are still in .env.local for security
 */

export interface LLMModel {
  id: string;
  name: string;
  provider: 'anthropic' | 'openai' | 'groq' | 'novita';
  contextWindow: number;
  inputCostPer1M: number;
  outputCostPer1M: number;
  supportsJSON: boolean;
  supportsMCP: boolean;
  maxTokens: number;
  description?: string;
}

export interface LLMProvider {
  id: string;
  name: string;
  envKey: string;
  models: LLMModel[];
  defaultModel: string;
}

/**
 * LLM Providers Configuration
 */
export const llmProviders: LLMProvider[] = [
  {
    id: 'anthropic',
    name: 'Anthropic',
    envKey: 'ANTHROPIC_API_KEY',
    defaultModel: 'claude-sonnet-4-5-20250929',
    models: [
      {
        id: 'claude-sonnet-4-5-20250929',
        name: 'Claude Sonnet 4.5',
        provider: 'anthropic',
        contextWindow: 200000,
        inputCostPer1M: 3.00,
        outputCostPer1M: 15.00,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 8192,
        description: 'Most capable model, best for complex tasks',
      },
      {
        id: 'claude-haiku-4-5',
        name: 'Claude Haiku 4.5',
        provider: 'anthropic',
        contextWindow: 200000,
        inputCostPer1M: 1.00,
        outputCostPer1M: 5.00,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 8192,
        description: 'Latest Haiku - fastest, matches Sonnet 4 on coding & agents',
      },
    ],
  },
  {
    id: 'openai',
    name: 'OpenAI',
    envKey: 'OPENAI_API_KEY',
    defaultModel: 'gpt-4o',
    models: [
      {
        id: 'gpt-4o',
        name: 'GPT-5',
        provider: 'openai',
        contextWindow: 128000,
        inputCostPer1M: 2.50,
        outputCostPer1M: 10.00,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 16384,
        description: 'Multimodal flagship model with function calling',
      },
      {
        id: 'gpt-4o-mini',
        name: 'GPT-5 Mini',
        provider: 'openai',
        contextWindow: 128000,
        inputCostPer1M: 0.15,
        outputCostPer1M: 0.60,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 16384,
        description: 'Affordable and fast with function calling',
      },
    ],
  },
  {
    id: 'groq',
    name: 'Groq',
    envKey: 'GROQ_API_KEY',
    defaultModel: 'gpt-oss-120b',
    models: [
      {
        id: 'gpt-oss-120b',
        name: 'GPT OSS 120B',
        provider: 'groq',
        contextWindow: 128000,
        inputCostPer1M: 0.20,
        outputCostPer1M: 0.20,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 32768,
        description: 'Larger Responses API model with MCP support',
      },
    ],
  },
  {
    id: 'novita',
    name: 'Novita AI',
    envKey: 'NOVITA_API_KEY',
    defaultModel: 'moonshotai/kimi-k2.5',
    models: [
      {
        id: 'moonshotai/kimi-k2.5',
        name: 'Kimi K2.5',
        provider: 'novita',
        contextWindow: 262144,
        inputCostPer1M: 0.6,
        outputCostPer1M: 3.0,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 262144,
        description: 'MoE model with function calling, structured output, reasoning, and vision',
      },
      {
        id: 'zai-org/glm-5',
        name: 'GLM 5',
        provider: 'novita',
        contextWindow: 202800,
        inputCostPer1M: 1.0,
        outputCostPer1M: 3.2,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 131072,
        description: 'MoE model with function calling, structured output, and reasoning',
      },
      {
        id: 'minimax/minimax-m2.5',
        name: 'MiniMax M2.5',
        provider: 'novita',
        contextWindow: 204800,
        inputCostPer1M: 0.3,
        outputCostPer1M: 1.2,
        supportsJSON: true,
        supportsMCP: true,
        maxTokens: 131100,
        description: 'MoE model with function calling, structured output, and reasoning',
      },
    ],
  },
];

/**
 * Get default model for a provider
 */
export function getDefaultModel(provider: 'anthropic' | 'openai' | 'groq' | 'novita'): string {
  const config = llmProviders.find(p => p.id === provider);
  return config?.defaultModel || '';
}

/**
 * Get all models for a provider
 */
export function getModelsForProvider(provider: 'anthropic' | 'openai' | 'groq' | 'novita'): LLMModel[] {
  const config = llmProviders.find(p => p.id === provider);
  return config?.models || [];
}

/**
 * Get model info by full ID (provider/model-id)
 */
export function getModelInfo(fullModelId: string): LLMModel | null {
  const firstSlashIndex = fullModelId.indexOf('/');
  if (firstSlashIndex === -1) return null;
  
  const provider = fullModelId.substring(0, firstSlashIndex);
  const modelId = fullModelId.substring(firstSlashIndex + 1);
  const providerConfig = llmProviders.find(p => p.id === provider);
  if (!providerConfig) return null;

  return providerConfig.models.find(m => m.id === modelId) || null;
}

/**
 * Format model ID for API calls
 */
export function formatModelId(provider: string, modelId: string): string {
  return `${provider}/${modelId}`;
}

/**
 * Get all available models (flattened)
 */
export function getAllModels(): Array<LLMModel & { fullId: string }> {
  return llmProviders.flatMap(provider =>
    provider.models.map(model => ({
      ...model,
      fullId: `${provider.id}/${model.id}`,
    }))
  );
}

/**
 * Check if provider API key is configured
 */
export function isProviderConfigured(provider: 'anthropic' | 'openai' | 'groq' | 'novita'): boolean {
  const config = llmProviders.find(p => p.id === provider);
  if (!config) return false;

  // This only works server-side
  if (typeof process === 'undefined') return false;

  return !!process.env[config.envKey];
}

/**
 * Get configured providers
 */
export function getConfiguredProviders(): string[] {
  return llmProviders
    .filter(p => isProviderConfigured(p.id as any))
    .map(p => p.id);
}
