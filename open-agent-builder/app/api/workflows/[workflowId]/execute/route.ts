import { NextRequest, NextResponse } from 'next/server';
import { LangGraphExecutor } from '@/lib/workflow/langgraph';
import { validateApiKey, createUnauthorizedResponse } from '@/lib/api/auth';

export const dynamic = 'force-dynamic';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  // Validate API key
  const authResult = await validateApiKey(request);
  if (!authResult.authenticated) {
    return createUnauthorizedResponse(authResult.error || 'Authentication required');
  }

  try {
    const { workflowId } = await params;
    const body = await request.json();
    const { input, workflow } = body;

    console.log('API: Executing workflow', workflowId, 'with input:', input);

    if (!workflow || !workflow.nodes) {
      return NextResponse.json(
        { error: 'Workflow data is required in request body' },
        { status: 400 }
      );
    }

    console.log('API: Loaded workflow:', workflow.name);

    const apiKeys = {
      anthropic: process.env.ANTHROPIC_API_KEY,
      groq: process.env.GROQ_API_KEY,
      openai: process.env.OPENAI_API_KEY,
      firecrawl: process.env.FIRECRAWL_API_KEY,
      arcade: process.env.ARCADE_API_KEY,
    };

    // Execute workflow using LangGraph
    const executor = new LangGraphExecutor(workflow, undefined, apiKeys);
    const execution = await executor.execute(input || '');

    console.log('API: Execution complete:', execution.status);

    return NextResponse.json({
      success: execution.status === 'completed',
      execution,
      input,
      workflowName: workflow.name,
    });
  } catch (error) {
    console.error('Workflow execution error:', error);
    return NextResponse.json(
      {
        error: 'Workflow execution failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
