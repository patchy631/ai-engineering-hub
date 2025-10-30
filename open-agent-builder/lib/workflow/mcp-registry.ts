/**
 * @deprecated This file is deprecated in favor of centralized MCP registry in Convex
 *
 * MCP Registry - Global storage for configured MCP servers
 * These can be selected and reused across multiple nodes
 *
 * MIGRATION NOTE: This localStorage-based registry has been replaced
 * with a centralized registry stored in Convex. All MCP configurations
 * are now managed through Settings → MCP Registry and stored persistently
 * in the database.
 *
 * See: /convex/mcpServers.ts for the new implementation
 */

const MCP_REGISTRY_KEY = 'mcp_registry';

export interface MCPServer {
  id: string;
  name: string;
  description: string;
  url: string;
  authType: 'none' | 'api-key' | 'oauth';
  accessToken?: string;
  tools: string[];
  category: 'web' | 'ai' | 'data' | 'custom';
}

/**
 * Get all configured MCP servers from global registry
 */
export function getMCPRegistry(): MCPServer[] {
  if (typeof window === 'undefined') return [];

  const stored = localStorage.getItem(MCP_REGISTRY_KEY);
  if (!stored) return [];

  try {
    return JSON.parse(stored);
  } catch (e) {
    console.error('Failed to parse MCP registry:', e);
    return [];
  }
}

/**
 * Save MCP server to global registry
 */
export function saveMCPToRegistry(server: MCPServer): void {
  const registry = getMCPRegistry();
  const existingIndex = registry.findIndex(s => s.id === server.id);

  if (existingIndex >= 0) {
    registry[existingIndex] = server;
  } else {
    registry.push(server);
  }

  localStorage.setItem(MCP_REGISTRY_KEY, JSON.stringify(registry));
}

/**
 * Remove MCP server from global registry
 */
export function removeMCPFromRegistry(id: string): void {
  const registry = getMCPRegistry();
  const filtered = registry.filter(s => s.id !== id);
  localStorage.setItem(MCP_REGISTRY_KEY, JSON.stringify(filtered));
}

/**
 * Get a specific MCP server by ID
 */
export function getMCPFromRegistry(id: string): MCPServer | null {
  const registry = getMCPRegistry();
  return registry.find(s => s.id === id) || null;
}

/**
 * Check if there are any configured MCP servers
 */
export function hasConfiguredMCPs(): boolean {
  return getMCPRegistry().length > 0;
}
