import { WorkflowNode, WorkflowState, WorkflowEdge } from '../types';

/**
 * Execute Logic Nodes - If/Else, While, User Approval
 */

// Type for the executor callback (used by LangGraph)
interface WhileIterationOptions {
  iterationState?: WorkflowState;
  whileNodeId?: string;
}

type NodeExecutor = (nodeId: string, options?: WhileIterationOptions) => Promise<any>;

// Context passed to while loop execution (used by LangGraph)
export interface WhileLoopContext {
  edges: WorkflowEdge[];
  executeNode: NodeExecutor;
}

export async function executeLogicNode(
  node: WorkflowNode,
  state: WorkflowState
): Promise<any> {
  const { type, data } = node;

  switch (type) {
    case 'if-else':
      return await executeIfElse(data, state);

    case 'while':
      return await executeWhile(node, data, state);

    case 'user-approval':
      return await executeUserApproval(data, state);

    default:
      throw new Error(`Unknown logic node type: ${type}`);
  }
}

async function executeIfElse(data: any, state: WorkflowState): Promise<any> {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 200));

  const conditionExpr = data.condition || 'true';

  try {
    // Get input from previous node, but prefer original classification data for conditions
    let input = state.variables['lastOutput'] || state.variables['input'] || {};
    
    // For classification-based conditions, use the original classification data
    if (conditionExpr.includes('classification') && state.variables.originalClassification) {
      input = state.variables.originalClassification;
      console.log('Using original classification data for condition evaluation');
    }

    console.log('Evaluating If/Else condition:', conditionExpr);
    console.log('Available input:', input);

    // Create evaluation function with input, state, and lastOutput context
    const lastOutput = state.variables['lastOutput'];
    
    // Enhanced evaluation with better error handling and debugging
    let result;
    try {
      const evalFunction = new Function('input', 'state', 'lastOutput', `return ${conditionExpr}`);
      result = evalFunction(input, state, lastOutput);
    } catch (evalError) {
      console.error('Condition evaluation error:', evalError);

      // Try alternative evaluation with better type coercion
      if (conditionExpr.includes('==')) {
        const parts = conditionExpr.split('==');
        if (parts.length === 2) {
          const left = parts[0].trim();
          const right = parts[1].trim().replace(/['"]/g, '');

          try {
            const leftEval = new Function('input', 'state', 'lastOutput', `return ${left}`);
            const leftValue = leftEval(input, state, lastOutput);

            // Try both strict and loose equality
            const strictMatch = leftValue === right;
            const looseMatch = String(leftValue).toLowerCase().trim() === String(right).toLowerCase().trim();

            console.log('🔍 Condition fallback evaluation:', {
              leftExpr: left,
              leftValue,
              rightValue: right,
              strictMatch,
              looseMatch,
            });

            result = strictMatch || looseMatch;
          } catch (e) {
            console.error('Fallback evaluation also failed:', e);
            result = false;
          }
        }
      } else {
        result = false;
      }
    }

    console.log('Condition result:', result);

    return {
      condition: Boolean(result),
      branch: result ? 'if' : 'else',
      evaluatedCondition: conditionExpr,
    };
  } catch (error) {
    console.error('Failed to evaluate condition:', error);
    // Default to false if evaluation fails
    return {
      condition: false,
      branch: 'else',
      evaluatedCondition: conditionExpr,
      error: error instanceof Error ? error.message : 'Evaluation failed',
    };
  }
}

async function executeWhile(node: WorkflowNode, data: any, state: WorkflowState): Promise<any> {
  // This function is deprecated and should not be used
  // While loops are now handled by LangGraph's executeWhileNode method
  // This is kept for backward compatibility but will throw an error if called
  throw new Error('While loop execution via custom executor is deprecated. Use LangGraph executor instead.');
}


/**
 * User Approval - Pauses workflow execution pending approval
 */
async function executeUserApproval(data: any, state: WorkflowState): Promise<any> {
  const { generateApprovalId } = await import('../../approval/approval-store');
  const { substituteVariables } = await import('../variable-substitution');

  const approvalId = generateApprovalId();
  const rawMessage = data.approvalMessage || 'Approval required';

  // Substitute variables in the approval message
  // This converts {{lastOutput.task}} to the actual task value
  const message = substituteVariables(rawMessage, state);

  console.log('User Approval - Raw message:', rawMessage);
  console.log('User Approval - Substituted message:', message);
  console.log('User Approval - State variables:', Object.keys(state.variables));

  // Return special response to signal workflow should pause
  return {
    __pendingApproval: true,
    approvalId,
    message,
    status: 'pending',
    createdAt: new Date().toISOString(),
  };
}

/**
 * TODO: Real implementation
 *
 * For if-else:
 * - Parse and evaluate condition string
 * - Support variable references from state
 * - Return boolean result
 *
 * For while:
 * - Evaluate condition in loop
 * - Execute loop body (connected nodes)
 * - Update state and check condition again
 *
 * For user-approval:
 * - Pause execution
 * - Show approval UI to user
 * - Wait for user response
 * - Resume with approval result
 */
