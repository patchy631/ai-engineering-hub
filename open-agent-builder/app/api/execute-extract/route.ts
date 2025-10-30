import { NextRequest, NextResponse } from 'next/server';
import { getServerAPIKeys } from '@/lib/api/config';
import { executeExtractNode } from '@/lib/workflow/executors/extract';
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
      id: 'extract-api-call',
      type: 'transform' as const,  // Extract uses the transform node type
      position: { x: 0, y: 0 },
      data: {
        label: 'Extract',
        nodeType: 'extract',  // Specify the actual node type in data
        instructions: instructions || 'Extract information from the input',
        model: model || 'gpt-5-mini',
        jsonSchema: jsonSchema,
        mcpTools: mcpTools,
      },
    };

    // Execute the extract node
    const result = await executeExtractNode(node, state, apiKeys);

    return NextResponse.json({
      success: true,
      extractedData: result.extractedData,
      usage: { totalTokens: result.tokensUsed },
      mcpToolsUsed: result.mcpToolsUsed,
    });
  } catch (error) {
    console.error('Extract execution error:', error);
    return NextResponse.json(
      {
        error: 'Extract execution failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}