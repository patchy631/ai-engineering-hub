import { WorkflowState } from './types';

/**
 * Replace variable references like {{state.variables.node_1.price}} with actual values
 */
export function substituteVariables(text: string, state: WorkflowState): string {
  if (!text) return text;

  // Find all {{variable}} patterns
  const pattern = /\{\{([^}]+)\}\}/g;

  return text.replace(pattern, (match, expression) => {
    try {
      // Clean up the expression
      const cleanExpr = expression.trim();

      // Evaluate the expression against state
      const value = evaluateExpression(cleanExpr, state);

      // Convert value to string
      if (value === null || value === undefined) {
        return match; // Keep original if not found
      }

      if (typeof value === 'object') {
        return JSON.stringify(value);
      }

      return String(value);
    } catch (e) {
      console.warn(`Failed to substitute variable: ${expression}`, e);
      return match; // Keep original on error
    }
  });
}

/**
 * Safely evaluate expression like "state.variables.node_1.price" or simpler "node_1.price"
 */
function evaluateExpression(expression: string, state: WorkflowState): any {
  // Support both patterns:
  // 1. Full: "state.variables.node_1.price"
  // 2. Simple: "node_1.price" (auto-adds state.variables prefix)

  let normalizedExpr = expression;

  // If expression doesn't start with "state", assume it's a simple node reference
  if (!expression.startsWith('state.')) {
    // Check if it's a known shorthand
    if (expression === 'input' || expression.startsWith('input.')) {
      // Support both input.query (maps to state.variables.input.input.query) and input directly
      // Try nested first (for JSON inputs), then direct
      normalizedExpr = `state.variables.${expression}`;
    } else if (expression === 'lastOutput' || expression.startsWith('lastOutput.')) {
      normalizedExpr = `state.variables.${expression}`;
    } else {
      // Assume it's a node reference like "scrape_website.markdown"
      normalizedExpr = `state.variables.${expression}`;
    }
  }

  // Parse dot notation path
  const parts = normalizedExpr.split('.');

  let current: any = { state };

  for (const part of parts) {
    if (current === null || current === undefined) {
      return undefined;
    }

    // Handle array indexing like items[0]
    const arrayMatch = part.match(/^(\w+)\[(\d+)\]$/);
    if (arrayMatch) {
      const [, arrayName, index] = arrayMatch;
      current = current[arrayName]?.[parseInt(index)];
    } else {
      current = current[part];
    }
  }

  // Special handling for input.X pattern - try multiple resolution strategies
  if (current === undefined && normalizedExpr.startsWith('state.variables.input.')) {
    const inputPath = normalizedExpr.replace('state.variables.input.', '');

    // Strategy 1: Try nested .input.input.X (for JSON inputs)
    const nestedValue = state.variables?.input?.input?.[inputPath];
    if (nestedValue !== undefined) {
      return nestedValue;
    }

    // Strategy 2: Try direct variable access (e.g., state.variables.query when input.query is requested)
    if (state.variables?.[inputPath] !== undefined) {
      return state.variables[inputPath];
    }

    // Strategy 3: Try traversing the full nested path manually
    const nestedPath = `state.variables.input.input.${inputPath}`;
    const nestedParts = nestedPath.split('.');
    let nestedCurrent: any = { state };
    for (const part of nestedParts) {
      if (nestedCurrent === null || nestedCurrent === undefined) break;
      nestedCurrent = nestedCurrent[part];
    }
    if (nestedCurrent !== undefined) {
      return nestedCurrent;
    }
  }

  return current;
}

/**
 * Extract all variable references from text
 */
export function extractVariableReferences(text: string): string[] {
  if (!text) return [];

  const pattern = /\{\{([^}]+)\}\}/g;
  const matches: string[] = [];
  let match;

  while ((match = pattern.exec(text)) !== null) {
    matches.push(match[1].trim());
  }

  return matches;
}

/**
 * Validate that all variable references exist in state
 */
export function validateVariableReferences(
  text: string,
  state: WorkflowState
): { valid: boolean; missing: string[] } {
  const references = extractVariableReferences(text);
  const missing: string[] = [];

  for (const ref of references) {
    try {
      const value = evaluateExpression(ref, state);
      if (value === undefined) {
        missing.push(ref);
      }
    } catch (e) {
      missing.push(ref);
    }
  }

  return {
    valid: missing.length === 0,
    missing,
  };
}

/**
 * Get available variables from state for autocomplete/picker
 */
export function getAvailableVariables(state: WorkflowState): Array<{
  path: string;
  value: any;
  type: string;
}> {
  const variables: Array<{ path: string; value: any; type: string }> = [];

  // Add top-level variables
  variables.push({
    path: 'state.variables.input',
    value: state.variables.input,
    type: typeof state.variables.input,
  });

  variables.push({
    path: 'state.variables.lastOutput',
    value: state.variables.lastOutput,
    type: typeof state.variables.lastOutput,
  });

  // Add all custom variables
  Object.keys(state.variables).forEach(key => {
    if (key !== 'input' && key !== 'lastOutput') {
      const value = state.variables[key];
      variables.push({
        path: `state.variables.${key}`,
        value,
        type: typeof value,
      });

      // If it's an object, add nested properties
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.keys(value).forEach(nestedKey => {
          variables.push({
            path: `state.variables.${key}.${nestedKey}`,
            value: value[nestedKey],
            type: typeof value[nestedKey],
          });
        });
      }
    }
  });

  return variables;
}
