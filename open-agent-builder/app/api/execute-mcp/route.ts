import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * Generic MCP Server Execution API
 * Supports calling any remote MCP server
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { serverUrl, serverName, tool, params, authToken } = body;

    console.log(`Executing MCP server: ${serverName}, tool: ${tool}`);
    console.log('Params:', params);

    // Generic MCP server execution
    return await executeGenericMCP(serverUrl, tool, params, authToken);

  } catch (error) {
    console.error('MCP execution error:', error);
    return NextResponse.json(
      {
        error: 'MCP execution failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        details: error instanceof Error ? error.stack : undefined,
      },
      { status: 500 }
    );
  }
}


/**
 * Execute generic MCP server
 */
async function executeGenericMCP(serverUrl: string, tool: string, params: any, authToken?: string) {
  // Generic MCP execution using JSON-RPC protocol
  const mcpRequest = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: tool,
      arguments: params,
    },
    id: Date.now(),
  };

  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
    };

    // Handle different authentication methods
    if (authToken) {
      // For Supabase and other OAuth providers, use Bearer token
      if (serverUrl.includes('supabase.com')) {
        headers['Authorization'] = `Bearer ${authToken}`;
      } else {
        // For other MCP servers, try Bearer first
        headers['Authorization'] = `Bearer ${authToken}`;
      }
    }

    console.log(`Making MCP request to: ${serverUrl}`);
    console.log('Headers:', headers);
    console.log('Request body:', JSON.stringify(mcpRequest, null, 2));

    const response = await fetch(serverUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(mcpRequest),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`MCP server error ${response.status}:`, errorText);
      
      if (response.status === 401) {
        throw new Error(`Authentication failed (401): ${errorText}. Please check your access token for the MCP server.`);
      } else if (response.status === 403) {
        throw new Error(`Access forbidden (403): ${errorText}. You may not have permission to use this MCP server.`);
      } else {
        throw new Error(`MCP server returned ${response.status}: ${errorText}`);
      }
    }

    const result = await response.json();
    console.log('MCP response:', result);

    return NextResponse.json({
      success: true,
      tool,
      result: result.result || result,
    });
  } catch (error) {
    console.error('MCP execution error:', error);
    throw new Error(`Failed to call MCP server: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
