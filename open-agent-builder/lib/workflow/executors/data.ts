import { WorkflowNode, WorkflowState } from '../types';
import CodeInterpreter from '@e2b/code-interpreter';

/**
 * Execute Data Nodes - Transform, Set State
 *
 * SECURITY NOTE: Transform Node Script Execution
 *
 * E2B SANDBOX INTEGRATION (ENABLED):
 * - Uses E2B CodeInterpreter for secure sandboxed JavaScript/TypeScript execution
 * - Executes in isolated cloud environment with 5-minute timeout
 * - Safe for untrusted code execution
 * - Requires E2B_API_KEY environment variable
 *
 * FALLBACK: If E2B is not available (missing key or server-side only execution),
 * falls back to Function constructor with security patterns (NOT recommended for production)
 *
 * E2B Execution:
 * - Creates isolated sandbox per execution
 * - Supports JavaScript and TypeScript
 * - 5-minute timeout per execution
 * - Automatic cleanup after execution
 */
export async function executeDataNode(
  node: WorkflowNode,
  state: WorkflowState
): Promise<any> {
  const { data } = node;
  const nodeType = data.nodeType || node.type;

  try {
    switch (nodeType) {
      case 'transform':
      case 'data-transform':
        return await executeTransform(data, state);

      case 'set-state':
      case 'set state':
        return await executeSetState(data, state);

      case 'export':
        return await executeExport(data, state);

      default:
        throw new Error(`Unknown data node type: ${nodeType}`);
    }
  } catch (error) {
    // Log error with context
    console.error(`Data node ${node.id} (${nodeType}) failed:`, error);

    // Re-throw with more context
    throw new Error(
      `Node ${node.id} execution failed: ${
        error instanceof Error ? error.message : 'Unknown error'
      }`
    );
  }
}

/**
 * Execute transform using E2B sandbox or fallback to Function constructor
 */
async function executeTransform(data: any, state: WorkflowState): Promise<any> {
  // Get the transform script from node data
  // Support both transformScript (UI) and transformation (templates)
  const transformScript = data.transformScript || data.transformation;

  // If no transform script, just pass through the input
  if (!transformScript || transformScript.trim() === '') {
    console.log('⚠️ No transform script provided, passing through input');
    return state.variables.lastOutput || {};
  }

  // Try E2B execution first (secure sandbox)
  const useE2B = typeof process !== 'undefined' && process.env?.E2B_API_KEY;

  if (useE2B) {
    try {
      return await executeTransformE2B(transformScript, state);
    } catch (error) {
      console.error('❌ E2B execution failed, falling back to Function:', error);
      // Fall through to fallback execution
    }
  }

  // Fallback to Function constructor (with security patterns)
  return await executeTransformFallback(transformScript, state);
}

/**
 * Execute transform using E2B CodeInterpreter (SECURE)
 * Now uses JavaScript/TypeScript execution
 */
async function executeTransformE2B(transformScript: string, state: WorkflowState): Promise<any> {
  console.log('🔒 Executing transform in E2B sandbox...');

  // Prepare the data for the sandbox
  const sandboxedInput = JSON.parse(JSON.stringify(state.variables.lastOutput || {}));
  const sandboxedState = {
    variables: JSON.parse(JSON.stringify(state.variables))
  };

  // Create E2B sandbox
  const sandbox = await CodeInterpreter.create({
    apiKey: process.env.E2B_API_KEY,
  });

  try {
    // Prepare the code to execute using JavaScript
    // We wrap the user's code in a function that provides the context
    const codeToExecute = `
const input = ${JSON.stringify(sandboxedInput)};
const lastOutput = ${JSON.stringify(sandboxedInput)};
const state = ${JSON.stringify(sandboxedState)};

// Execute user's transform code
const transform = () => {
${transformScript.split('\n').map((line: string) => '  ' + line).join('\n')}
};

const result = transform();

// Output result as JSON
console.log(JSON.stringify(result));
`;

    console.log('🔍 E2B code to execute:', codeToExecute);

    // Execute in the sandbox using JavaScript
    const execution = await sandbox.runCode(codeToExecute);

    // Check for errors
    if (execution.error) {
      throw new Error(`E2B execution error: ${execution.error.name}: ${execution.error.value}`);
    }

    // Parse the result from stdout
    const resultText = execution.logs.stdout.join('\n');
    const result = JSON.parse(resultText);

    console.log('✅ E2B execution successful:', result);

    // Update state with the result
    state.variables['lastOutput'] = result;

    return result;
  } finally {
    // Always close the sandbox
    await sandbox.kill();
  }
}

/**
 * Fallback execution using Function constructor (LESS SECURE)
 */
async function executeTransformFallback(transformScript: string, state: WorkflowState): Promise<any> {
  console.log('⚠️ Using fallback Function execution (not recommended for production)');

  // Enhanced security patterns to prevent malicious code execution
  const dangerousPatterns = [
    /require\s*\(/gi,
    /import\s+/gi,
    /eval\s*\(/gi,
    /Function\s*\(/gi,
    /setTimeout\s*\(/gi,
    /setInterval\s*\(/gi,
    /setImmediate\s*\(/gi,
    /process\./gi,
    /__dirname/gi,
    /__filename/gi,
    /global\./gi,
    /globalThis\./gi,
    /window\./gi,
    /document\./gi,
    /fetch\s*\(/gi,
    /XMLHttpRequest/gi,
    /fs\./gi,
    /child_process/gi,
    /exec\s*\(/gi,
    /spawn\s*\(/gi,
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(transformScript)) {
      throw new Error(`Security violation: Script contains forbidden pattern: ${pattern.source}`);
    }
  }

  // Script length limit
  const MAX_SCRIPT_LENGTH = 5000;
  if (transformScript.length > MAX_SCRIPT_LENGTH) {
    throw new Error(`Script too long (max ${MAX_SCRIPT_LENGTH} characters)`);
  }

  try {
    // Create restricted context with deep clones to prevent mutation
    const sandboxedInput = JSON.parse(JSON.stringify(state.variables.lastOutput || {}));
    const sandboxedState = {
      variables: JSON.parse(JSON.stringify(state.variables))
    };

    // Debug: Log the state structure
    console.log('🔍 Transform Debug - state.variables.input:', JSON.stringify(state.variables.input, null, 2));
    console.log('🔍 Transform Debug - input (lastOutput):', JSON.stringify(sandboxedInput, null, 2));
    console.log('🔍 Transform Debug - ALL state.variables keys:', Object.keys(state.variables));

    // Use strict mode to prevent certain unsafe operations
    const strictScript = `"use strict";\n${transformScript}\n//# sourceURL=transform-script.js`;
    const transformFunction = new Function('input', 'lastOutput', 'state', strictScript);

    // Execute with timeout protection
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Transform timeout (3s limit)')), 3000)
    );

    const executionPromise = Promise.resolve(
      transformFunction(sandboxedInput, sandboxedInput, sandboxedState)
    );

    const result = await Promise.race([executionPromise, timeoutPromise]);

    // Validate output isn't suspiciously large (1MB limit)
    const resultString = JSON.stringify(result);
    if (resultString.length > 1000000) {
      throw new Error('Transform output too large (>1MB)');
    }

    console.log('🔍 Transform Debug - result:', JSON.stringify(result, null, 2));

    // Update state with the result
    state.variables['lastOutput'] = result;

    return result;
  } catch (error) {
    throw new Error(`Transform failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

async function executeSetState(data: any, state: WorkflowState): Promise<any> {
  const key = data.stateKey || 'variable';

  try {
    let rawValue = data.stateValue || null;
    const valueType = data.valueType || 'string';

    console.log('🔧 Set State - Key:', key);
    console.log('🔧 Set State - Raw Value:', rawValue);
    console.log('🔧 Set State - Type:', valueType);

    // Import variable substitution
    const { substituteVariables } = await import('../variable-substitution');

    // Substitute variables in the value (e.g., {{lastOutput.price}})
    if (typeof rawValue === 'string') {
      rawValue = substituteVariables(rawValue, state);
      console.log('🔧 Set State - After substitution:', rawValue);
    }

    // Parse value based on type
    let finalValue: any;

    switch (valueType) {
      case 'number':
        finalValue = parseFloat(rawValue);
        if (isNaN(finalValue)) {
          throw new Error(`Cannot convert "${rawValue}" to number`);
        }
        break;

      case 'boolean':
        if (typeof rawValue === 'boolean') {
          finalValue = rawValue;
        } else {
          const str = String(rawValue).toLowerCase();
          finalValue = str === 'true' || str === '1' || str === 'yes';
        }
        break;

      case 'json':
        try {
          finalValue = typeof rawValue === 'string' ? JSON.parse(rawValue) : rawValue;
        } catch (e) {
          throw new Error(`Invalid JSON: ${e instanceof Error ? e.message : 'Parse error'}`);
        }
        break;

      case 'expression':
        // Evaluate JavaScript expression
        try {
          const evalFunction = new Function('input', 'lastOutput', 'state', `return ${rawValue}`);
          finalValue = evalFunction(
            state.variables.input,
            state.variables.lastOutput,
            state
          );
        } catch (e) {
          throw new Error(`Expression evaluation failed: ${e instanceof Error ? e.message : 'Unknown error'}`);
        }
        break;

      default:
        // String - just use the substituted value
        finalValue = rawValue;
    }

    console.log('🔧 Set State - Final Value:', finalValue);

    // Set the state variable
    state.variables[key] = finalValue;

    return {
      key,
      value: finalValue,
      valueType,
      stateUpdated: true,
    };
  } catch (error) {
    // Provide context about what failed
    throw new Error(
      `Failed to set state variable '${key}': ${
        error instanceof Error ? error.message : 'Unknown error'
      }`
    );
  }
}

async function executeExport(data: any, state: WorkflowState): Promise<any> {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 100));

  // Get the data to export from lastOutput
  const input = state.variables['lastOutput'] || {};

  // For now, just return the data formatted for export
  // In a real implementation, this would handle different export formats
  return {
    exportData: input,
    exported: true,
  };
}

/**
 * TODO: Real implementation
 *
 * For transform:
 * - Execute JavaScript transform script safely (sandboxed)
 * - Support common transformation libraries (lodash, etc)
 * - Handle errors gracefully
 * - Support async transformations
 *
 * For set-state:
 * - Parse value expressions
 * - Support references to other variables
 * - Validate types
 * - Support nested object paths
 */
