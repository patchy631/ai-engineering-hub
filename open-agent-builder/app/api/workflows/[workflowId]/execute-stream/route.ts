import { NextRequest } from 'next/server';
import { getConvexClient, getAuthenticatedConvexClient, api, isConvexConfigured } from '@/lib/convex/client';
import { LangGraphExecutor } from '@/lib/workflow/langgraph';
import { validateApiKey, createUnauthorizedResponse } from '@/lib/api/auth';

export const dynamic = 'force-dynamic';

/**
 * Streaming workflow execution with real-time updates
 * Uses Server-Sent Events (SSE) to stream node execution progress
 *
 * Uses LangGraph executor for state management with Convex storage
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
        // Get inputs from request body
        const body = await request.json();
        const inputs = body || {};

        // Get workflow from Convex
        if (!isConvexConfigured()) {
          sendEvent('error', {
            error: 'Convex not configured',
            workflowId,
          });
          controller.close();
          return;
        }

        const convex = await getAuthenticatedConvexClient();

        // Look up workflow - try customId first, then try as Convex ID
        let workflowDoc = await convex.query(api.workflows.getWorkflowByCustomId, {
          customId: workflowId,
        });

        // If not found by customId and looks like Convex ID, try direct lookup
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
          sendEvent('error', {
            error: `Workflow ${workflowId} not found`,
            workflowId,
          });
          controller.close();
          return;
        }

        // Convert Convex document to workflow format
        const workflowData = {
          ...workflowDoc,
          id: workflowDoc.customId || workflowDoc._id, // Use customId if exists, otherwise Convex ID
        };

        if (!workflowData) {
          sendEvent('error', {
            error: `Workflow ${workflowId} not found`,
            workflowId,
          });
          controller.close();
          return;
        }

        const workflow = workflowData as any;

        // Send start event
        sendEvent('workflow_started', {
          workflowId,
          workflowName: workflow.name,
          totalNodes: workflow.nodes.length,
          timestamp: new Date().toISOString(),
        });

        // Create a custom execution with progress callbacks
        const executionId = `exec_${Date.now()}`;
        const nodeResults: Record<string, any> = {};

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

        // Prepare initial input - pass as object if it's an object, otherwise as string
        let initialInput: any = '';
        if (typeof inputs === 'object' && Object.keys(inputs).length > 0) {
          // If the body has an "input" field, extract it (common pattern from curl/API calls)
          // Otherwise use the body directly
          initialInput = inputs.input || inputs;
        } else {
          // Otherwise use url or input field
          initialInput = inputs.url || inputs.input || '';
        }

        // LangGraph Execution Path
        const threadId = `thread_${workflowId}_${Date.now()}`;

        let executor;
        try {
          executor = new LangGraphExecutor(
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
            } else if (result.status === 'pending-authorization' || result.status === 'pending-approval') {
              const node = workflow.nodes.find((n: any) => n.id === nodeId);
              sendEvent('node_paused', {
                nodeId,
                nodeName: node?.data?.nodeName || node?.data?.label || nodeId,
                status: result.status,
                timestamp: new Date().toISOString(),
              });
            }
          },
          apiKeys
          );
        } catch (graphBuildError) {
          console.error('❌ Failed to build LangGraph:', graphBuildError);
          sendEvent('error', {
            error: graphBuildError instanceof Error ? graphBuildError.message : 'Graph compilation failed',
            timestamp: new Date().toISOString(),
          });
          controller.close();
          return;
        }

        // Execute with streaming
        const executionStream = await executor.executeStream(initialInput, {
          threadId,
          executionId,
        });

        let finalState: any = null;

        // CRITICAL FIX: Proper async iteration with error handling
        try {
          for await (const stateUpdate of executionStream) {
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

            // Check for pending auth/approval
            if (mergedState.pendingAuth) {
              sendEvent('workflow_paused', {
                reason: 'pending_authorization',
                pendingAuth: mergedState.pendingAuth,
                executionId,
                threadId,
                timestamp: new Date().toISOString(),
              });

              // TODO: Save execution state to Convex for resume capability
              // await convex.mutation(api.executions.createExecution, {...})

              controller.close();
              return;
            }
          }
        } catch (streamError) {
          console.error('Stream iteration error:', streamError);
          sendEvent('error', {
            error: streamError instanceof Error ? streamError.message : 'Stream error',
            timestamp: new Date().toISOString(),
          });
          controller.close();
          return;
        }

        // Send completion event
        const status = finalState?.pendingAuth ? 'waiting-auth' : 'completed';

        sendEvent('workflow_completed', {
          workflowId,
          executionId,
          results: finalState?.nodeResults || {},
          status,
          timestamp: new Date().toISOString(),
        });

        // TODO: Save execution results to Convex
        // await convex.mutation(api.executions.completeExecution, {...})

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
      'X-Accel-Buffering': 'no', // Disable nginx buffering
    },
  });
}
