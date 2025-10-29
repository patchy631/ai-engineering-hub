import { NextResponse } from 'next/server';
import { officialMCPServers, getEnabledMCPServers, getMCPServerById } from '@/lib/mcp/mcp-registry';

export const dynamic = 'force-dynamic';

/**
 * GET /api/mcp/registry
 * List all MCP servers from registry
 */
export async function GET() {
  try {
    // Get servers from code-defined configuration
    const servers = getEnabledMCPServers();

    return NextResponse.json({
      success: true,
      servers,
      source: 'config',
    });
  } catch (error) {
    console.error('Failed to get MCP registry:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to load MCP registry' },
      { status: 500 }
    );
  }
}

