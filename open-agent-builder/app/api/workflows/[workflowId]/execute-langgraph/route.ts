import { NextRequest, NextResponse } from 'next/server';
import { LangGraphExecutor } from '@/lib/workflow/langgraph';
import { getWorkflow } from '@/lib/workflow/storage';
import { getServerAPIKeys } from '@/lib/api/config';
import { validateApiKey } from '@/lib/api/auth';

export const dynamic = 'force-dynamic';

/**
 * Execute workflow using LangGraph
 * POST /api/workflows/:workflowId/execute-langgraph
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    // Validate API key
    const authResult = await validateApiKey(request);
    if (!authResult.authenticated) {
      return NextResponse.json(
        { error: authResult.error || 'Authentication required' },
        { status: 401 }
      );
    }

    const { workflowId } = await params;
    const body = await request.json();
    const { input, threadId } = body;

    // Load workflow
    const workflow = await getWorkflow(workflowId);
    if (!workflow) {
      return NextResponse.json(
        { error: 'Workflow not found' },
        { status: 404 }
      );
    }

    // Get API keys - check user keys first, then fall back to environment
    const { getLLMApiKey } = await import('@/lib/api/llm-keys');
    const userId = authResult.userId;
    
    const apiKeys = {
      anthropic: userId ? await getLLMApiKey('anthropic', userId) : null || process.env.ANTHROPIC_API_KEY,
      groq: userId ? await getLLMApiKey('groq', userId) : null || process.env.GROQ_API_KEY,
      openai: userId ? await getLLMApiKey('openai', userId) : null || process.env.OPENAI_API_KEY,
      firecrawl: process.env.FIRECRAWL_API_KEY, // Firecrawl keys are still environment-only for now
      arcade: process.env.ARCADE_API_KEY,
    };

    // Create LangGraph executor
    const executor = new LangGraphExecutor(workflow, undefined, apiKeys || undefined);

    // Execute workflow
    const result = await executor.execute(input, { threadId });

    return NextResponse.json({
      success: true,
      executionId: result.id,
      status: result.status,
      nodeResults: result.nodeResults,
      startedAt: result.startedAt,
      completedAt: result.completedAt,
    });
  } catch (error) {
    console.error('LangGraph execution error:', error);
    return NextResponse.json(
      {
        error: 'Workflow execution failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
