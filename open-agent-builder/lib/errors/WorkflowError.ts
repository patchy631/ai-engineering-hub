/**
 * Base error class for all workflow-related errors.
 * Provides structured error information for better debugging and user feedback.
 */
export class WorkflowError extends Error {
  constructor(
    message: string,
    public code: string,
    public nodeId?: string,
    public cause?: Error
  ) {
    super(message);
    this.name = 'WorkflowError';

    // Maintains proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, WorkflowError);
    }
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      nodeId: this.nodeId,
      cause: this.cause?.message,
      stack: this.stack,
    };
  }
}

/**
 * Error thrown when a node fails to execute.
 */
export class NodeExecutionError extends WorkflowError {
  constructor(nodeId: string, message: string, cause?: Error) {
    super(`Node ${nodeId} failed: ${message}`, 'NODE_EXECUTION_ERROR', nodeId, cause);
    this.name = 'NodeExecutionError';
  }
}

/**
 * Error thrown when workflow validation fails.
 */
export class ValidationError extends WorkflowError {
  constructor(message: string, nodeId?: string) {
    super(message, 'VALIDATION_ERROR', nodeId);
    this.name = 'ValidationError';
  }
}

/**
 * Error thrown when an API call fails.
 */
export class APIError extends WorkflowError {
  constructor(
    message: string,
    public statusCode?: number,
    public endpoint?: string,
    cause?: Error
  ) {
    super(message, 'API_ERROR', undefined, cause);
    this.name = 'APIError';
  }

  toJSON() {
    return {
      ...super.toJSON(),
      statusCode: this.statusCode,
      endpoint: this.endpoint,
    };
  }
}

/**
 * Error thrown when authorization is required or fails.
 */
export class AuthorizationError extends WorkflowError {
  constructor(message: string, public toolName?: string) {
    super(message, 'AUTHORIZATION_ERROR');
    this.name = 'AuthorizationError';
  }

  toJSON() {
    return {
      ...super.toJSON(),
      toolName: this.toolName,
    };
  }
}

/**
 * Error codes used throughout the workflow system.
 */
export const ErrorCodes = {
  NODE_EXECUTION_ERROR: 'NODE_EXECUTION_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  API_ERROR: 'API_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  WORKFLOW_NOT_FOUND: 'WORKFLOW_NOT_FOUND',
  INVALID_CONFIGURATION: 'INVALID_CONFIGURATION',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
} as const;

export type ErrorCode = typeof ErrorCodes[keyof typeof ErrorCodes];
