import { Workflow, MCPServer } from './types';

// NOTE: localStorage removed - all workflows now stored in Redis via API
// These functions are kept for backwards compatibility but are no-ops

// Workflow Storage (NO-OP - Use Redis via API instead)
export const saveWorkflow = (workflow: Workflow): void => {
  console.log('⚠️ saveWorkflow called - localStorage disabled, use API instead');
  // No-op: workflows saved via POST /api/workflows
};

export const getWorkflows = (): Workflow[] => {
  console.log('⚠️ getWorkflows called - localStorage disabled, use API instead');
  return [];
};

export const getWorkflow = (id: string): Workflow | null => {
  console.log('⚠️ getWorkflow called - localStorage disabled, use API instead');
  return null;
};

export const deleteWorkflow = (id: string): void => {
  console.log('⚠️ deleteWorkflow called - localStorage disabled, use API instead');
  // No-op: workflows deleted via DELETE /api/workflows/[id]
};

export const setCurrentWorkflow = (workflowId: string): void => {
  console.log('⚠️ setCurrentWorkflow called - localStorage disabled');
  // No-op: workflow ID tracked via URL params
};

export const getCurrentWorkflowId = (): string | null => {
  console.log('⚠️ getCurrentWorkflowId called - localStorage disabled');
  return null;
};

// MCP Server Storage (NO-OP - localStorage disabled)
export const saveMCPServer = (server: MCPServer): void => {
  console.log('⚠️ saveMCPServer called - localStorage disabled');
  // No-op: MCP servers should be managed via API if needed
};

export const getMCPServers = (): MCPServer[] => {
  console.log('⚠️ getMCPServers called - localStorage disabled');
  return [];
};

export const getMCPServer = (id: string): MCPServer | null => {
  console.log('⚠️ getMCPServer called - localStorage disabled');
  return null;
};

export const deleteMCPServer = (id: string): void => {
  console.log('⚠️ deleteMCPServer called - localStorage disabled');
  // No-op
};
