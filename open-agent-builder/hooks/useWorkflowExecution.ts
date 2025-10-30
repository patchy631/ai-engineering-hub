import { useState, useCallback, useRef, useEffect } from 'react';
import { Workflow, WorkflowExecution, NodeExecutionResult, WorkflowPendingAuth } from '@/lib/workflow/types';
import { toast } from 'sonner';

interface PendingArcadeResume {
  nodeId: string;
  workflow: Workflow;
  state: any;
  execution: WorkflowExecution;
  pendingAuth: WorkflowPendingAuth;
  pendingInput?: any;
}

const clone = <T>(value: T): T => {
  if (typeof structuredClone === 'function') {
    try {
      return structuredClone(value);
    } catch (error) {
      // Fallback to JSON cloning
    }
  }

  return JSON.parse(JSON.stringify(value)) as T;
};

const loadStoredApiKeys = () => {
  if (typeof window === 'undefined') {
    return {} as Record<string, string>;
  }

  try {
    const raw = localStorage.getItem('firecrawl_api_keys');
    if (!raw) {
      return {} as Record<string, string>;
    }
    const parsed = JSON.parse(raw);
    return typeof parsed === 'object' && parsed !== null ? parsed : {};
  } catch (error) {
    console.warn('Failed to load stored API keys:', error);
    return {} as Record<string, string>;
  }
};

export function useWorkflowExecution() {
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentNodeId, setCurrentNodeId] = useState<string | null>(null);
  const [nodeResults, setNodeResults] = useState<Record<string, NodeExecutionResult>>({});
  const [pendingAuth, setPendingAuth] = useState<WorkflowPendingAuth | null>(null);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const pendingResumeRef = useRef<PendingArcadeResume | null>(null);

  // Cleanup on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      // Only abort if there's an active workflow running
      if (abortControllerRef.current && isRunning) {
        console.log('🧹 Cleanup: Aborting active workflow on unmount');
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
      // Clear pending resume data
      pendingResumeRef.current = null;
    };
  }, [isRunning]);

  const runWorkflow = useCallback(async (workflow: Workflow, input?: string) => {
    if (!workflow) {
      console.error('No workflow to execute');
      return;
    }

    setIsRunning(true);
    setNodeResults({});
    setCurrentNodeId(null);
    setPendingAuth(null);
    setCurrentWorkflow(workflow);
    pendingResumeRef.current = null;

    // Create abort controller
    abortControllerRef.current = new AbortController();

    try {
      // Fetch API keys from server
      const configResponse = await fetch('/api/config');
      const apiConfig = await configResponse.json();

      // Execute workflow via LangGraph streaming API

      // Parse input if it's a JSON string, otherwise send as-is
      let parsedInput: any;
      try {
        parsedInput = typeof input === 'string' && input.trim().startsWith('{')
          ? JSON.parse(input)
          : { input };
      } catch (e) {
        // If parsing fails, wrap in input object
        parsedInput = { input };
      }

      const response = await fetch(`/api/workflows/${workflow.id}/execute-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedInput),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error('Workflow execution failed');
      }

      // Handle SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let executionId = '';
      let currentEvent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') {
            // Empty line marks end of SSE message
            currentEvent = '';
            continue;
          }

          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
            continue;
          }

          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              console.log(`📨 SSE Event: ${currentEvent}`, data);

              // Handle error events
              if (currentEvent === 'error' && data.error) {
                console.error('❌ Workflow error:', data.error);

                // Show error toast to user
                toast.error('Workflow Error', {
                  description: data.error,
                  duration: 10000, // Show for 10 seconds
                });

                // Set failed execution state
                setExecution({
                  id: executionId || `exec_${Date.now()}`,
                  workflowId: workflow.id,
                  status: 'failed',
                  error: data.error,
                  nodeResults: nodeResults,
                  startedAt: data.timestamp || new Date().toISOString(),
                  completedAt: data.timestamp || new Date().toISOString(),
                });

                // Stop execution
                setIsRunning(false);
                setCurrentNodeId(null);
                break; // Exit the SSE loop
              }

              // Set current node immediately when node starts (before it completes)
              if (currentEvent === 'node_started' && data.nodeId) {
                setCurrentNodeId(data.nodeId);
              }

              // Update node results from stream
              if (data.nodeResults) {
                setNodeResults(prev => {
                  const updated = { ...prev, ...data.nodeResults };
                  console.log('📊 Updated nodeResults:', Object.keys(updated));
                  return updated;
                });
              }

              // Update current node from state updates
              if (data.currentNodeId) {
                setCurrentNodeId(data.currentNodeId);
              }

              // Store execution ID
              if (data.executionId) {
                executionId = data.executionId;
              }

              // Check for pending auth
              if (data.pendingAuth) {
                setPendingAuth(data.pendingAuth);

                // Set execution status to waiting-auth
                const waitingExecution: WorkflowExecution = {
                  id: executionId || data.executionId || `exec_${Date.now()}`,
                  workflowId: workflow.id,
                  status: 'waiting-auth',
                  nodeResults: data.nodeResults || {},
                  startedAt: data.timestamp || new Date().toISOString(),
                };
                setExecution(waitingExecution);
                break;
              }

              // Check for workflow completion
              if (currentEvent === 'workflow_completed' || data.status === 'completed' || data.status === 'waiting-auth') {
                const execution: WorkflowExecution = {
                  id: executionId || data.executionId || `exec_${Date.now()}`,
                  workflowId: workflow.id,
                  status: data.status || 'completed',
                  nodeResults: data.results || data.nodeResults || {},
                  startedAt: data.timestamp || new Date().toISOString(),
                  completedAt: data.timestamp || new Date().toISOString(),
                };
                setExecution(execution);
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e, 'Line:', line);
            }
          }
        }
      }

      console.log('✅ Workflow complete');
    } catch (error) {
      // Don't treat abort as an error - it's intentional user action
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('⏹️ Workflow stopped by user');
        setPendingAuth(null);
        pendingResumeRef.current = null;
        return;
      }

      console.error('❌ Workflow execution failed:', error);
      setPendingAuth(null);
      pendingResumeRef.current = null;
      // Set error state
      setExecution({
        id: `exec_${Date.now()}`,
        workflowId: workflow.id,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        nodeResults: {},
        startedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      });
    } finally {
      console.log('🏁 Setting isRunning = false');
      setIsRunning(false);
      setCurrentNodeId(null);
    }
  }, []);

  const stopWorkflow = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsRunning(false);
    setCurrentNodeId(null);
  }, []);

  const resumeWorkflow = useCallback(async () => {
    if (!currentWorkflow) {
      console.error('❌ No workflow to resume');
      return;
    }

    if (!pendingAuth) {
      console.error('❌ No pending authorization to resume from');
      return;
    }

    const threadId = pendingAuth.threadId;
    const executionId = pendingAuth.executionId;

    if (!threadId) {
      console.error('❌ No threadId in pendingAuth');
      return;
    }

    console.log('⏳ Resuming workflow from approval...');
    setIsRunning(true);

    try {
      // Call resume API endpoint
      const response = await fetch(`/api/workflows/${currentWorkflow.id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          threadId,
          executionId,
          resumeValue: { approved: true, status: 'approved' },
        }),
        signal: abortControllerRef.current?.signal,
      });

      if (!response.ok) {
        throw new Error(`Resume failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body from resume endpoint');
      }

      // Clear pending auth since we're resuming
      setPendingAuth(null);

      // Process SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              // Update current node
              if (data.currentNodeId) {
                setCurrentNodeId(data.currentNodeId);
              }

              // Update node results
              if (data.nodeResults) {
                setNodeResults(prevResults => ({
                  ...prevResults,
                  ...data.nodeResults,
                }));
              }

              // Check for pending auth again (multiple approvals)
              if (data.pendingAuth) {
                setPendingAuth(data.pendingAuth);

                const waitingExecution = {
                  id: executionId || `exec_${Date.now()}`,
                  workflowId: currentWorkflow.id,
                  status: 'waiting-auth' as const,
                  nodeResults: data.nodeResults || {},
                  startedAt: new Date().toISOString(),
                };
                setExecution(waitingExecution);
                break;
              }

              // Check for completion
              if (data.status === 'completed') {
                const completedExecution = {
                  id: executionId || `exec_${Date.now()}`,
                  workflowId: currentWorkflow.id,
                  status: 'completed' as const,
                  nodeResults: data.results || data.nodeResults || {},
                  startedAt: new Date().toISOString(),
                  completedAt: new Date().toISOString(),
                };
                setExecution(completedExecution);
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

      console.log('✅ Workflow resumed and completed');
    } catch (error) {
      // Don't treat abort as an error - it's intentional user action
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('⏹️ Workflow stopped by user');
        return;
      }

      console.error('❌ Workflow resume failed:', error);
      setExecution({
        id: executionId || `exec_${Date.now()}`,
        workflowId: currentWorkflow.id,
        status: 'failed',
        nodeResults: {},
        startedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      });
    } finally {
      setIsRunning(false);
      setCurrentNodeId(null);
    }
  }, [currentWorkflow, pendingAuth]);

  const clearExecution = useCallback(() => {
    setExecution(null);
    setNodeResults({});
    setCurrentNodeId(null);
    setPendingAuth(null);
    setCurrentWorkflow(null);
    pendingResumeRef.current = null;
  }, []);

  return {
    execution,
    isRunning,
    currentNodeId,
    nodeResults,
    pendingAuth,
    runWorkflow,
    stopWorkflow,
    resumeWorkflow,
    clearExecution,
  };
}
