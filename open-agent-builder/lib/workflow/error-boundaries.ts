/**
 * Workflow Error Boundaries
 * Provides better error handling and user-friendly messages
 */

export class WorkflowExecutionError extends Error {
  constructor(
    message: string,
    public nodeId: string,
    public nodeType: string,
    public originalError?: Error
  ) {
    super(`[${nodeType}] ${nodeId}: ${message}`);
    this.name = 'WorkflowExecutionError';
  }
}

/**
 * Wrap node execution with error handling
 */
export function wrapNodeExecution<T>(
  nodeId: string,
  nodeType: string,
  fn: () => Promise<T>
): Promise<T> {
  return fn().catch(err => {
    throw new WorkflowExecutionError(
      err.message,
      nodeId,
      nodeType,
      err
    );
  });
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyError(error: Error): string {
  const message = error.message;

  // API key errors
  if (message.includes('API key') || message.includes('api_key')) {
    return 'Missing API key. Please add your LLM provider key in Settings.';
  }

  // Rate limit errors
  if (message.includes('rate limit') || message.includes('429')) {
    return 'Rate limited. Please wait a moment and try again.';
  }

  // Network errors
  if (message.includes('fetch') || message.includes('network')) {
    return 'Network error. Please check your connection and try again.';
  }

  // Firecrawl-specific errors
  if (message.includes('FIRECRAWL')) {
    return 'Firecrawl API error. Please verify your FIRECRAWL_API_KEY in .env.local';
  }

  // Variable substitution errors
  if (message.includes('variable') || message.includes('{{')) {
    return `Variable error: ${message}. Check your variable references.`;
  }

  // Generic error
  return `Execution failed: ${message}`;
}
