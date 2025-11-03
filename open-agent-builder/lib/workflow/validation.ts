import { Workflow, WorkflowNode } from './types';

export interface ValidationError {
  nodeId: string;
  field: string;
  message: string;
}

export function validateWorkflow(workflow: Workflow): ValidationError[] {
  const errors: ValidationError[] = [];

  // Check if workflow has at least a start and end node
  const hasStart = workflow.nodes.some(n => n.type === 'start');
  const hasEnd = workflow.nodes.some(n => n.type === 'end');

  if (!hasStart) {
    errors.push({
      nodeId: 'workflow',
      field: 'nodes',
      message: 'Workflow must have a Start node',
    });
  }

  // Validate each node
  workflow.nodes.forEach((node) => {
    const nodeErrors = validateNode(node);
    errors.push(...nodeErrors);
  });

  // Check for disconnected nodes (except end nodes)
  workflow.nodes.forEach((node) => {
    if (node.type !== 'start' && node.type !== 'end') {
      const hasIncoming = workflow.edges.some(e => e.target === node.id);
      if (!hasIncoming) {
        errors.push({
          nodeId: node.id,
          field: 'connections',
          message: 'Node is not connected to workflow',
        });
      }
    }
  });

  return errors;
}

export function validateNode(node: WorkflowNode): ValidationError[] {
  const errors: ValidationError[] = [];
  const nodeType = (node.data as any).nodeType || node.type;

  switch (nodeType) {
    case 'agent':
      if (!node.data.instructions || node.data.instructions.trim() === '') {
        errors.push({
          nodeId: node.id,
          field: 'instructions',
          message: 'Agent must have instructions',
        });
      }
      if (!node.data.model) {
        errors.push({
          nodeId: node.id,
          field: 'model',
          message: 'Agent must have a model selected',
        });
      }
      break;

    case 'mcp':
      if (!node.data.mcpServers || node.data.mcpServers.length === 0) {
        errors.push({
          nodeId: node.id,
          field: 'mcpServers',
          message: 'MCP node must have at least one server configured',
        });
      }
      break;

    case 'if-else':
    case 'if / else':
      if (!node.data.condition || node.data.condition.trim() === '') {
        errors.push({
          nodeId: node.id,
          field: 'condition',
          message: 'If/Else must have a condition',
        });
      }
      break;

    case 'while':
      if (!node.data.condition || node.data.condition.trim() === '') {
        errors.push({
          nodeId: node.id,
          field: 'condition',
          message: 'While loop must have a condition',
        });
      }
      break;

    case 'transform':
      if (!node.data.transformScript || node.data.transformScript.trim() === '') {
        errors.push({
          nodeId: node.id,
          field: 'transformScript',
          message: 'Transform must have a script',
        });
      }
      break;

    case 'set-state':
    case 'set state':
      if (!node.data.stateKey || node.data.stateKey.trim() === '') {
        errors.push({
          nodeId: node.id,
          field: 'stateKey',
          message: 'Set State must have a variable name',
        });
      }
      break;
  }

  return errors;
}

export function getNodeValidationStatus(node: WorkflowNode): 'valid' | 'warning' | 'error' {
  const errors = validateNode(node);

  if (errors.length === 0) return 'valid';
  if (errors.some(e => e.field !== 'connections')) return 'error';
  return 'warning';
}
