/**
 * Model validation and configuration for LLM providers
 */

export type Provider = 'openai' | 'anthropic' | 'groq';

export interface ModelConfig {
  provider: Provider;
  modelName: string;
  isValid: boolean;
  error?: string;
}

/**
 * Supported models by provider (MCP-compatible only)
 * These models support MCP through their respective APIs:
 * - OpenAI: Responses API
 * - Anthropic: Messages API with MCP beta
 * - Groq: Responses API (OpenAI-compatible)
 */
export const SUPPORTED_MODELS = {
  openai: [
    // OpenAI models that support Responses API
    'gpt-4o',
    'gpt-4o-mini',
  ],
  anthropic: [
    // Claude 4 models that support Messages API with MCP
    'claude-sonnet-4-5-20250929',
    'claude-haiku-4-5', // Latest Haiku 4.5
  ],
  groq: [
    // Only Groq models that support Responses API (per Groq docs)
    'gpt-oss-120b',
  ],
} as const;

/**
 * Default models for each provider
 */
export const DEFAULT_MODELS = {
  openai: 'gpt-4o',
  anthropic: 'claude-sonnet-4-5-20250929', // Claude 4.5 Sonnet
  groq: 'gpt-oss-120b', // Using Responses API model for better MCP support
} as const;

/**
 * Parse a model string into provider and model name
 * Supports formats:
 * - "provider/model-name" (e.g., "openai/gpt-4o")
 * - "model-name" (defaults to openai provider)
 */
export function parseModelString(modelString?: string): { provider: Provider; modelName: string } {
  if (!modelString) {
    return { provider: 'openai', modelName: DEFAULT_MODELS.openai };
  }

  if (modelString.includes('/')) {
    const [provider, modelName] = modelString.split('/', 2) as [string, string];

    // Validate provider
    if (provider !== 'openai' && provider !== 'anthropic' && provider !== 'groq') {
      // Default to openai if provider is unknown
      return { provider: 'openai', modelName: DEFAULT_MODELS.openai };
    }

    return { provider, modelName };
  }

  // No provider prefix, default to openai
  return { provider: 'openai', modelName: modelString };
}

/**
 * Validate a model configuration
 */
export function validateModel(modelString?: string): ModelConfig {
  const { provider, modelName } = parseModelString(modelString);

  // Check if model is in supported list
  const supportedModels = SUPPORTED_MODELS[provider];
  const isValid = (supportedModels as readonly string[]).includes(modelName);

  if (!isValid) {
    return {
      provider,
      modelName,
      isValid: false,
      error: `Model '${modelName}' is not supported for provider '${provider}'. Supported models: ${supportedModels.join(', ')}`,
    };
  }

  return {
    provider,
    modelName,
    isValid: true,
  };
}

/**
 * Get the default model for a provider
 */
export function getDefaultModel(provider: Provider): string {
  return DEFAULT_MODELS[provider];
}

/**
 * Check if a provider is supported
 */
export function isSupportedProvider(provider: string): provider is Provider {
  return provider === 'openai' || provider === 'anthropic' || provider === 'groq';
}

/**
 * Get model string with provider prefix
 */
export function getModelString(provider: Provider, modelName: string): string {
  return `${provider}/${modelName}`;
}

/**
 * Ensure model string is compatible with OpenAI Responses API
 * (only OpenAI models work with the Responses API)
 */
export function ensureOpenAIModel(modelString?: string): string {
  const { provider, modelName } = parseModelString(modelString);

  // If it's already an OpenAI model, return it
  if (provider === 'openai') {
    // Validate it's a supported OpenAI model
    const validation = validateModel(modelString);
    if (validation.isValid) {
      return modelName;
    }
    // Fall back to default if invalid
    return DEFAULT_MODELS.openai;
  }

  // For non-OpenAI providers, return default OpenAI model
  return DEFAULT_MODELS.openai;
}
