import { NextRequest } from 'next/server';
import { LangGraphExecutor } from '@/lib/workflow/langgraph';
import { Workflow } from '@/lib/workflow/types';

/**
 * POST /api/workflow/execute
 * Execute a workflow and stream results via SSE
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { workflow, input } = body as { workflow: Workflow; input?: string };

    if (!workflow) {
      return new Response(
        JSON.stringify({ error: 'Workflow is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Create SSE stream
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        // Send initial event
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({
            type: 'start',
            workflow: workflow.name,
            input
          })}\n\n`)
        );

        const apiKeys = {
          anthropic: process.env.ANTHROPIC_API_KEY,
          groq: process.env.GROQ_API_KEY,
          openai: process.env.OPENAI_API_KEY,
          firecrawl: process.env.FIRECRAWL_API_KEY,
          arcade: process.env.ARCADE_API_KEY,
        };

        // Create executor with update callback
        const executor = new LangGraphExecutor(
          workflow,
          (nodeId, result) => {
            // Stream node updates
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({
                type: 'node_update',
                nodeId,
                result
              })}\n\n`)
            );
          },
          apiKeys
        );

        try {
          // Execute workflow
          const execution = await executor.execute(input || '');

          // Send completion event
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({
              type: 'complete',
              execution
            })}\n\n`)
          );
        } catch (error) {
          // Send error event
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({
              type: 'error',
              error: error instanceof Error ? error.message : 'Unknown error'
            })}\n\n`)
          );
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Workflow execution error:', error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Unknown error'
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
