import { Workflow } from './types';

export interface DuplicateCredentialWarning {
  type: 'duplicate-credential';
  message: string;
  serverName: string;
  serverUrl: string;
  credential: string; // Masked version for display
  nodeIds: string[];
  nodeNames: string[];
}

/**
 * Detect duplicate MCP credentials across workflow nodes
 * Returns warnings for credentials that appear in multiple nodes
 */
export function detectDuplicateCredentials(workflow: Workflow): DuplicateCredentialWarning[] {
  const credentialMap = new Map<string, {
    serverName: string;
    serverUrl: string;
    credential: string;
    nodeIds: string[];
    nodeNames: string[];
  }>();

  // Scan all nodes for MCP servers
  workflow.nodes.forEach(node => {
    const mcpTools = (node.data as any)?.mcpTools || [];

    mcpTools.forEach((mcp: any) => {
      // Skip if no authentication
      if (!mcp.accessToken || mcp.authType === 'None') return;

      // Create unique key for this credential
      // Use URL + token (or token pattern for env vars)
      const isEnvVar = mcp.accessToken.startsWith('${') && mcp.accessToken.endsWith('}');
      const credentialKey = `${mcp.url}:${mcp.accessToken}`;

      if (!credentialMap.has(credentialKey)) {
        credentialMap.set(credentialKey, {
          serverName: mcp.name,
          serverUrl: mcp.url,
          credential: isEnvVar ? mcp.accessToken : maskCredential(mcp.accessToken),
          nodeIds: [],
          nodeNames: [],
        });
      }

      const entry = credentialMap.get(credentialKey)!;
      entry.nodeIds.push(node.id);

      // Get node name from data
      const nodeName = (node.data as any)?.nodeName ||
                      (node.data as any)?.name ||
                      (typeof node.data?.label === 'string' ? node.data.label : node.id);
      entry.nodeNames.push(nodeName);
    });
  });

  // Filter to only duplicates (used in 2+ nodes)
  const warnings: DuplicateCredentialWarning[] = [];

  credentialMap.forEach((entry) => {
    if (entry.nodeIds.length > 1) {
      // Skip warnings for common shared services like Firecrawl
      const isSharedService = entry.serverName.toLowerCase().includes('firecrawl') ||
                             entry.serverName.toLowerCase().includes('arcade') ||
                             entry.serverUrl.includes('firecrawl.dev') ||
                             entry.serverUrl.includes('arcade.dev');
      
      if (!isSharedService) {
        warnings.push({
          type: 'duplicate-credential',
          message: `MCP server "${entry.serverName}" uses the same credential in ${entry.nodeIds.length} nodes`,
          serverName: entry.serverName,
          serverUrl: entry.serverUrl,
          credential: entry.credential,
          nodeIds: entry.nodeIds,
          nodeNames: entry.nodeNames,
        });
      }
    }
  });

  return warnings;
}

/**
 * Mask credential for display (show first/last 4 chars)
 */
function maskCredential(credential: string): string {
  if (credential.length <= 8) {
    return '****';
  }

  const first = credential.substring(0, 4);
  const last = credential.substring(credential.length - 4);
  const middle = '*'.repeat(Math.min(credential.length - 8, 12));

  return `${first}${middle}${last}`;
}
