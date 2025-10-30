import { WorkflowNode, WorkflowState } from '../types';
import { getMCPServer } from '../storage';
import { substituteVariables } from '../variable-substitution';
import { getServerAPIKeys } from '@/lib/api/config';
import { resolveMCPServer } from '@/lib/mcp/resolver';

/**
 * Extract specific field from Firecrawl response
 */
function extractField(data: any, field: string, customPath?: string): any {
  if (field === 'full') return data;
  if (field === 'custom' && customPath) {
    return getNestedValue(data, customPath);
  }

  // Predefined field mappings
  switch (field) {
    case 'markdown':
      return data.markdown || data;
    case 'html':
      return data.html || data;
    case 'metadata':
      return data.metadata || {};
    case 'results':
      return data.results || data;
    case 'urls':
      if (Array.isArray(data.results)) {
        return data.results.map((r: any) => r.url);
      }
      if (Array.isArray(data.urls)) {
        return data.urls;
      }
      if (Array.isArray(data.links)) {
        return data.links;
      }
      return data;
    case 'first':
      return data.results?.[0] || data[0] || data;
    case 'json':
      // For JSON mode in scrape/crawl
      return data.json || data.data || data;
    default:
      return data[field] || data;
  }
}

/**
 * Get nested value from object using dot notation
 */
function getNestedValue(obj: any, path: string): any {
  const parts = path.split('.');
  let current = obj;

  for (const part of parts) {
    // Handle array indexing
    const arrayMatch = part.match(/^(\w+)\[(\d+)\]$/);
    if (arrayMatch) {
      const [, arrayName, index] = arrayMatch;
      current = current[arrayName]?.[parseInt(index)];
    } else {
      current = current?.[part];
    }

    if (current === undefined) break;
  }

  return current;
}

/**
 * Execute a generic MCP server (DeepWiki, etc.)
 */
async function executeGenericMCPServer(serverConfig: any, state: WorkflowState): Promise<any> {
  const input = state.variables?.input || state.variables?.lastOutput;
  const serverName = serverConfig.name.toLowerCase();

  // For DeepWiki
  if (serverName.includes('deepwiki') || serverName.includes('devin')) {
    // Parse the input to determine which tool to use
    const inputText = typeof input === 'string' ? input : JSON.stringify(input);

    // Determine which DeepWiki tool to use based on input
    let tool = 'ask_question'; // Default
    let params: any = {};

    if (inputText.includes('wiki structure') || inputText.includes('topics')) {
      tool = 'read_wiki_structure';
      // Extract repo from input (e.g., "anthropics/anthropic-sdk-python")
      const repoMatch = inputText.match(/([a-zA-Z0-9-]+\/[a-zA-Z0-9-]+)/);
      params.repository = repoMatch ? repoMatch[1] : 'anthropics/anthropic-sdk-python';
    } else if (inputText.includes('wiki content') || inputText.includes('documentation')) {
      tool = 'read_wiki_contents';
      const repoMatch = inputText.match(/([a-zA-Z0-9-]+\/[a-zA-Z0-9-]+)/);
      params.repository = repoMatch ? repoMatch[1] : 'anthropics/anthropic-sdk-python';
    } else {
      tool = 'ask_question';
      // Extract repo if mentioned
      const repoMatch = inputText.match(/([a-zA-Z0-9-]+\/[a-zA-Z0-9-]+)/);
      params.repository = repoMatch ? repoMatch[1] : 'anthropics/anthropic-sdk-python';
      params.question = inputText;
    }

    return {
      tool,
      data: {
        server: 'DeepWiki',
        tool,
        params,
        note: 'DeepWiki MCP execution is not yet implemented. This is a placeholder response.',
        input: inputText,
        suggestedImplementation: 'Call the DeepWiki MCP server API at ' + serverConfig.url,
      },
    };
  }

  // Generic fallback for unknown MCP servers
  throw new Error(`MCP server "${serverConfig.name}" execution not yet implemented. Server URL: ${serverConfig.url}`);
}

/**
 * Execute MCP Node - Calls MCP server tools (Firecrawl)
 * Uses API route when running client-side to avoid CORS
 */
export async function executeMCPNode(
  node: WorkflowNode,
  state: WorkflowState,
  apiKey?: string
): Promise<any> {
  const { data } = node;

  // MCP executor always runs on server side in LangGraph context
  // No client-side detection needed
  
  const nodeName = data.nodeName?.toLowerCase() || '';
  const nodeData = data as any;
  const lastOutput = state.variables?.lastOutput;

  // Resolve MCP server configuration
  let mcpServers = nodeData.mcpServers || [];

  // If using new format with server ID, resolve it
  if (nodeData.mcpServerId) {
    const resolvedServer = await resolveMCPServer(nodeData.mcpServerId);
    if (resolvedServer) {
      mcpServers = [resolvedServer];
    } else {
      console.warn(`Could not resolve MCP server ID: ${nodeData.mcpServerId}`);
    }
  }

  if (!mcpServers || mcpServers.length === 0) {
    return {
      error: 'No MCP servers configured or could not resolve server',
    };
  }

  const results: any[] = [];

  for (const serverConfig of mcpServers) {
    // Handle Firecrawl servers - now disabled
    if (serverConfig.name.toLowerCase().includes('firecrawl')) {
      console.log('⚠️ Firecrawl MCP server detected but firecrawl has been removed from the project');
      
      const nodeData = data as any;
      const action = nodeData.mcpAction || 'scrape';
      
      // Return a helpful error message
      const errorMessage = `Firecrawl has been removed from this project. Please use alternative web scraping solutions or remove this MCP server from your workflow.`;
      
      results.push({
        server: 'Firecrawl',
        tool: action,
        success: false,
        error: errorMessage,
      });
      
      continue;
    } else {
      // Generic MCP server support (DeepWiki, etc.)
      try {
        const result = await executeGenericMCPServer(serverConfig, state);
        results.push({
          server: serverConfig.name,
          tool: result.tool || 'unknown',
          success: true,
          data: result.data,
        });
        state.variables.lastOutput = result.data;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.error(`${serverConfig.name} execution error:`, error);
        results.push({
          server: serverConfig.name,
          error: errorMessage,
          success: false,
        });
      }
    }
  }

  return {
    results,
    mcpServers: mcpServers.map(s => s.name),
  };
}

