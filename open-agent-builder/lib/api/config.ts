/**
 * Server-side API configuration utilities
 * Use this for getting API keys in API routes and server components
 */

export interface APIKeys {
  anthropic?: string;
  groq?: string;
  openai?: string;
  novita?: string;
  arcade?: string;
  e2b?: string;
}

/**
 * Get API keys from environment variables (server-side only)
 * Returns available keys even if some are missing
 */
export function getServerAPIKeys(): APIKeys {
  const anthropic = process.env.ANTHROPIC_API_KEY;
  const groq = process.env.GROQ_API_KEY;
  const openai = process.env.OPENAI_API_KEY;
  const novita = process.env.NOVITA_API_KEY;
  const arcade = process.env.ARCADE_API_KEY;
  const e2b = process.env.E2B_API_KEY;

  return {
    anthropic,
    groq,
    openai,
    novita,
    arcade,
    e2b,
  };
}

/**
 * Check if required API keys are configured
 */
export function hasServerAPIKeys(): boolean {
  const hasLLMKey = !!(process.env.ANTHROPIC_API_KEY || process.env.GROQ_API_KEY || process.env.OPENAI_API_KEY || process.env.NOVITA_API_KEY);
  return hasLLMKey;
}
