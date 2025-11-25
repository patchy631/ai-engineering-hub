import { NextRequest } from 'next/server';
import { getConvexClient, getAuthenticatedConvexClient, api, isConvexConfigured } from '@/lib/convex/client';
import { LangGraphExecutor } from '@/lib/workflow/langgraph';
import { validateApiKey, createUnauthorizedResponse } from '@/lib/api/auth';

export const dynamic = 'force-dynamic';

/**
 * Resume a paused workflow execution
 * Uses LangGraph's resumeFromAuth to continue from interrupt point
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  // Validate API key
  const authResult = await validateApiKey(request);
  if (!authResult.authenticated) {
    return createUnauthorizedResponse(authResult.error || 'Authentication required');
  }

  const { workflowId } = await params;

  // Create SSE stream
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (event: string, data: any) => {
        try {
          const message = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
          controller.enqueue(encoder.encode(message));
        } catch (error) {
          console.error('Failed to send SSE event:', error);
        }
      };

      try {
        // Get resume data from request
        const body = await request.json();
        const { threadId, resumeValue, executionId } = body;

        if (!threadId) {
          sendEvent('error', { error: 'threadId is required for resume' });
          controller.close();
          return;
        }

        // Get workflow from Convex
        if (!isConvexConfigured()) {
          sendEvent('error', { error: 'Convex not configured' });
          controller.close();
          return;
        }

        const convex = await getAuthenticatedConvexClient();

        // Look up workflow
        let workflowDoc = await convex.query(api.workflows.getWorkflowByCustomId, {
          customId: workflowId,
        });

        if (!workflowDoc && workflowId.startsWith('j')) {
          try {
            workflowDoc = await convex.query(api.workflows.getWorkflow, {
              id: workflowId as any,
            });
          } catch (e) {
            // Not a valid Convex ID
          }
        }

        if (!workflowDoc) {
          sendEvent('error', { error: `Workflow ${workflowId} not found` });
          controller.close();
          return;
        }

        const workflow = {
          ...workflowDoc,
          id: workflowDoc.customId || workflowDoc._id,
        } as any;

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

        const nodeResults: Record<string, any> = {};

        // Create executor
        const executor = new LangGraphExecutor(
          workflow,
          (nodeId, result) => {
            nodeResults[nodeId] = result;

            if (result.status === 'running') {
              const node = workflow.nodes.find((n: any) => n.id === nodeId);
              sendEvent('node_started', {
                nodeId,
                nodeName: node?.data?.nodeName || node?.data?.label || nodeId,
                nodeType: node?.type || 'unknown',
                timestamp: new Date().toISOString(),
              });
            } else if (result.status === 'completed') {
              const node = workflow.nodes.find((n: any) => n.id === nodeId);
              sendEvent('node_completed', {
                nodeId,
                nodeName: node?.data?.nodeName || node?.data?.label || nodeId,
                result,
                timestamp: new Date().toISOString(),
              });
            } else if (result.status === 'failed') {
              const node = workflow.nodes.find((n: any) => n.id === nodeId);
              sendEvent('node_failed', {
                nodeId,
                nodeName: node?.data?.nodeName || node?.data?.label || nodeId,
                error: result.error,
                timestamp: new Date().toISOString(),
              });
            }
          },
          apiKeys
        );

        // Resume execution from pause point
        const resumeStream = await executor.resumeFromAuth(
          threadId,
          resumeValue || { approved: true, status: 'approved' },
          { executionId }
        );

        sendEvent('workflow_resumed', {
          threadId,
          executionId,
          timestamp: new Date().toISOString(),
        });

        let finalState: any = null;

        // Stream resumed execution
        try {
          for await (const stateUpdate of resumeStream) {
            const mergedState = {
              ...stateUpdate,
              nodeResults: {
                ...stateUpdate.nodeResults,
                ...nodeResults,
              },
            };

            finalState = mergedState;

            sendEvent('state_update', {
              nodeResults: mergedState.nodeResults,
              currentNodeId: mergedState.currentNodeId,
              pendingAuth: mergedState.pendingAuth,
              timestamp: new Date().toISOString(),
            });

            // Check for another pending auth/approval
            if (mergedState.pendingAuth) {
              sendEvent('workflow_paused', {
                reason: 'pending_authorization',
                pendingAuth: mergedState.pendingAuth,
                executionId,
                threadId,
                timestamp: new Date().toISOString(),
              });

              controller.close();
              return;
            }
          }
        } catch (streamError) {
          console.error('Resume stream error:', streamError);
          sendEvent('error', {
            error: streamError instanceof Error ? streamError.message : 'Stream error',
            timestamp: new Date().toISOString(),
          });
          controller.close();
          return;
        }

        // Send completion event
        sendEvent('workflow_completed', {
          workflowId,
          executionId,
          results: finalState?.nodeResults || {},
          status: 'completed',
          timestamp: new Date().toISOString(),
        });

        controller.close();
      } catch (error) {
        sendEvent('error', {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        });
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}
