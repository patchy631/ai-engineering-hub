/**
 * API Authentication Utilities
 * Validates API keys for workflow execution endpoints
 * Supports both Clerk (UI) and API Key (external) authentication
 */

import { NextRequest } from 'next/server';
import { getConvexClient, api } from '@/lib/convex/client';
import { auth } from '@clerk/nextjs/server';

export interface ApiAuthResult {
  authenticated: boolean;
  userId?: string;
  error?: string;
  authType?: 'clerk' | 'api-key';
}

/**
 * Validates authentication - checks Clerk first (for UI), then API key (for external)
 * This allows both authenticated UI users and API key users to access endpoints
 */
export async function validateApiKey(request: NextRequest): Promise<ApiAuthResult> {
  try {
    // First, check for Clerk authentication (UI users)
    const { userId } = await auth();
    if (userId) {
      return {
        authenticated: true,
        userId,
        authType: 'clerk'
      };
    }

    // If no Clerk auth, check for API key (external API users)
    const authHeader = request.headers.get('Authorization');

    if (!authHeader) {
      return {
        authenticated: false,
        error: 'Authentication required. Please sign in or provide an API key with format: "Bearer YOUR_API_KEY"'
      };
    }

    // Parse Bearer token
    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0] !== 'Bearer') {
      return {
        authenticated: false,
        error: 'Invalid Authorization header format. Expected: "Bearer YOUR_API_KEY"'
      };
    }

    const apiKey = parts[1];

    if (!apiKey || apiKey.length < 10) {
      return {
        authenticated: false,
        error: 'Invalid API key format'
      };
    }

    // Verify key with Convex
    const convex = getConvexClient();
    const result = await convex.mutation(api.apiKeys.verify, { key: apiKey });

    if (!result.valid) {
      return {
        authenticated: false,
        error: result.error || 'Invalid API key'
      };
    }

    return {
      authenticated: true,
      userId: result.userId,
      authType: 'api-key'
    };
  } catch (error) {
    console.error('API key validation error:', error);
    return {
      authenticated: false,
      error: 'API key validation failed'
    };
  }
}

/**
 * Creates a standardized unauthorized response
 */
export function createUnauthorizedResponse(error: string) {
  return new Response(
    JSON.stringify({
      error: 'Unauthorized',
      message: error,
      hint: 'Generate an API key from Settings and include it in the Authorization header'
    }),
    {
      status: 401,
      headers: {
        'Content-Type': 'application/json',
        'WWW-Authenticate': 'Bearer realm="API Key Required"'
      }
    }
  );
}
