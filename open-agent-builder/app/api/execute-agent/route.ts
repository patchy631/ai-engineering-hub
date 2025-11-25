import { NextRequest, NextResponse } from 'next/server';
import { getServerAPIKeys } from '@/lib/api/config';
import { executeAgentNode } from '@/lib/workflow/executors/agent';
import { WorkflowNode, WorkflowState } from '@/lib/workflow/types';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { instructions, model, context, jsonSchema, mcpTools = [] } = body;

    // Get API keys from server
    const apiKeys = getServerAPIKeys();
    if (!apiKeys) {
      return NextResponse.json(
        { error: 'API keys not configured in .env.local' },
        { status: 500 }
      );
    }

    // Create a minimal workflow state
    const state: WorkflowState = {
      variables: {
        input: context || '',
        lastOutput: context || '',
      },
      chatHistory: [],
    };

    // Create a minimal workflow node
    const node: WorkflowNode = {
      id: 'api-call',
      type: 'agent' as const,
      position: { x: 0, y: 0 },
      data: {
        label: 'Agent',
        instructions: instructions || 'Process the input',
        model: model || 'anthropic/claude-sonnet-4-20250514',
        outputFormat: jsonSchema ? 'JSON' : 'Text',
        jsonOutputSchema: jsonSchema,
        mcpTools: mcpTools,
        includeChatHistory: false,
      },
    };

    // Execute the agent node
    const result = await executeAgentNode(node, state, apiKeys);

    // Extract the response data
    const responseText = result.__agentValue;
    const toolCalls = result.__agentToolCalls || [];

    return NextResponse.json({
      success: true,
      text: typeof responseText === 'string' ? responseText : JSON.stringify(responseText),
      mcpToolsUsed: toolCalls,
      // Include any additional metadata if needed
      stopReason: result.stopReason,
    });
  } catch (error) {
    console.error('Agent execution error:', error);
    return NextResponse.json(
      {
        error: 'Agent execution failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}