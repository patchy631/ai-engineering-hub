import { NextResponse } from 'next/server';

/**
 * API route to securely provide environment variables
 * Only exposes API keys from .env.local, never from client
 */
export async function GET() {
  try {
    const config = {
      anthropicConfigured: !!process.env.ANTHROPIC_API_KEY,
      groqConfigured: !!process.env.GROQ_API_KEY,
      openaiConfigured: !!process.env.OPENAI_API_KEY,
      firecrawlConfigured: !!process.env.FIRECRAWL_API_KEY,
      arcadeConfigured: !!process.env.ARCADE_API_KEY,
      hasKeys: !!(
        (process.env.ANTHROPIC_API_KEY || process.env.GROQ_API_KEY || process.env.OPENAI_API_KEY) &&
        process.env.FIRECRAWL_API_KEY
      ),
    };

    return NextResponse.json(config);
  } catch (error) {
    console.error('Config API error:', error);
    return NextResponse.json(
      { error: 'Failed to load configuration' },
      { status: 500 }
    );
  }
}
