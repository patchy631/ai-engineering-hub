/**
 * LLM API Key Management
 *
 * Provides API keys for LLM providers with fallback logic:
 * 1. Check user-specific keys from database
 * 2. Fall back to environment variables if no user key exists
 */

import { ConvexClient } from "convex/browser";
import { api } from "@/convex/_generated/api";

// Initialize Convex client for server-side use
const getConvexClient = () => {
  const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL;
  if (!convexUrl) {
    throw new Error("NEXT_PUBLIC_CONVEX_URL is not configured");
  }
  return new ConvexClient(convexUrl);
};

/**
 * Get the API key for a specific LLM provider
 * Checks user keys first, then falls back to environment variables
 *
 * @param provider - The LLM provider ('anthropic', 'openai', 'groq')
 * @param userId - Optional user ID to check for user-specific keys
 * @returns The API key or null if not found
 */
export async function getLLMApiKey(
  provider: 'anthropic' | 'openai' | 'groq',
  userId?: string
): Promise<string | null> {
  // First, try to get user-specific key if userId is provided
  if (userId) {
    try {
      const client = getConvexClient();
      const userKey = await client.query(api.userLLMKeys.getActiveKey, {
        userId,
        provider,
      });

      if (userKey?.apiKey) {
        // Update usage stats
        await client.mutation(api.userLLMKeys.updateKeyUsage, {
          userId,
          provider,
        }).catch(console.error); // Don't fail if usage update fails

        return userKey.apiKey;
      }
    } catch (error) {
      console.error(`Failed to get user key for ${provider}:`, error);
      // Continue to environment variable fallback
    }
  }

  // Fall back to environment variables
  const envKeyMap = {
    anthropic: 'ANTHROPIC_API_KEY',
    openai: 'OPENAI_API_KEY',
    groq: 'GROQ_API_KEY',
  };

  const envKey = envKeyMap[provider];
  const apiKey = process.env[envKey];

  if (apiKey) {
    return apiKey;
  }

  return null;
}

/**
 * Check if a provider has an API key configured (either user or env)
 */
export async function isProviderConfigured(
  provider: 'anthropic' | 'openai' | 'groq',
  userId?: string
): Promise<boolean> {
  const apiKey = await getLLMApiKey(provider, userId);
  return !!apiKey;
}

/**
 * Get all configured providers for a user
 */
export async function getConfiguredProviders(userId?: string): Promise<string[]> {
  const providers: ('anthropic' | 'openai' | 'groq')[] = ['anthropic', 'openai', 'groq'];
  const configured: string[] = [];

  for (const provider of providers) {
    if (await isProviderConfigured(provider, userId)) {
      configured.push(provider);
    }
  }

  return configured;
}

/**
 * Initialize LLM client with appropriate API key
 * This is a helper function that can be used by the execute routes
 */
export async function initializeLLMClient(
  provider: 'anthropic' | 'openai' | 'groq',
  userId?: string
): Promise<{ apiKey: string; provider: string }> {
  const apiKey = await getLLMApiKey(provider, userId);

  if (!apiKey) {
    throw new Error(
      `No API key found for ${provider}. Please configure your API key in Settings or set the ${
        provider === 'anthropic' ? 'ANTHROPIC_API_KEY' :
        provider === 'openai' ? 'OPENAI_API_KEY' :
        'GROQ_API_KEY'
      } environment variable.`
    );
  }

  return { apiKey, provider };
}

/**
 * Get configuration status for all providers
 * Useful for the settings panel to show which providers are configured
 */
export async function getProvidersStatus(userId?: string): Promise<{
  anthropic: { configured: boolean; source: 'user' | 'env' | null };
  openai: { configured: boolean; source: 'user' | 'env' | null };
  groq: { configured: boolean; source: 'user' | 'env' | null };
}> {
  const status: any = {};

  for (const provider of ['anthropic', 'openai', 'groq'] as const) {
    // Check user key first
    if (userId) {
      try {
        const client = getConvexClient();
        const userKey = await client.query(api.userLLMKeys.getActiveKey, {
          userId,
          provider,
        });

        if (userKey) {
          status[provider] = { configured: true, source: 'user' };
          continue;
        }
      } catch (error) {
        // Continue to env check
      }
    }

    // Check environment variable
    const envKeyMap = {
      anthropic: 'ANTHROPIC_API_KEY',
      openai: 'OPENAI_API_KEY',
      groq: 'GROQ_API_KEY',
    };

    const envKey = envKeyMap[provider];
    if (process.env[envKey]) {
      status[provider] = { configured: true, source: 'env' };
    } else {
      status[provider] = { configured: false, source: null };
    }
  }

  return status;
}