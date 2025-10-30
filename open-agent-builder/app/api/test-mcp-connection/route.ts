import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * Test MCP Server Connection
 * Discovers available tools by calling the MCP server's tools/list endpoint
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url, authToken, headers: customHeaders } = body;

    if (!url) {
      return NextResponse.json(
        { error: 'URL is required' },
        { status: 400 }
      );
    }

    console.log('Testing MCP connection to:', url);

    // Substitute environment variables in URL
    let resolvedUrl = url;
    const envVarMatch = url.match(/\{([A-Z_]+)\}/g);
    if (envVarMatch) {
      envVarMatch.forEach((match: string) => {
        const envVar = match.slice(1, -1); // Remove { and }
        const envValue = process.env[envVar];
        if (envValue) {
          resolvedUrl = resolvedUrl.replace(match, envValue);
        }
      });
    }

    // Build headers (some MCP servers require accepting both JSON and SSE)
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
    };

    // Add custom headers if provided (e.g., Context7's CONTEXT7_API_KEY)
    if (customHeaders) {
      Object.keys(customHeaders).forEach((key) => {
        // Resolve environment variables in header values
        let headerValue = customHeaders[key];
        if (typeof headerValue === 'string') {
          if (headerValue.startsWith('${') && headerValue.endsWith('}')) {
            const envVar = headerValue.slice(2, -1);
            headerValue = process.env[envVar] || headerValue;
          } else if (headerValue.match(/\{([A-Z_]+)\}/)) {
            // Handle format like {API_KEY}
            const envVar = headerValue.replace(/\{|\}/g, '');
            headerValue = process.env[envVar] || headerValue;
          }
        }
        headers[key] = headerValue;
      });
    }

    // Add Bearer token if provided (legacy support)
    if (authToken && !customHeaders) {
      // Handle environment variable substitution for access tokens
      let resolvedToken = authToken;
      if (authToken.startsWith('${') && authToken.endsWith('}')) {
        const envVar = authToken.slice(2, -1);
        resolvedToken = process.env[envVar] || authToken;
      }
      headers['Authorization'] = `Bearer ${resolvedToken}`;
    }

    // Call MCP server to list tools
    const mcpRequest = {
      jsonrpc: '2.0',
      method: 'tools/list',
      params: {},
      id: Date.now(),
    };

    console.log('Making request to:', resolvedUrl);
    console.log('Request:', mcpRequest);

    const response = await fetch(resolvedUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(mcpRequest),
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('MCP connection failed:', response.status, errorText);

      let errorMessage = `HTTP ${response.status}`;
      if (response.status === 404) {
        errorMessage = 'MCP server not found - check URL';
      } else if (response.status === 401 || response.status === 403) {
        errorMessage = 'Authentication failed - check access token';
      } else if (response.status === 500) {
        errorMessage = 'Server error - MCP server may be down';
      }

      return NextResponse.json({
        success: false,
        error: errorMessage,
        details: errorText.substring(0, 500),
        statusCode: response.status,
        testedUrl: resolvedUrl, // Show resolved URL for debugging
      }, { status: 200 }); // Return 200 so frontend can show user-friendly error
    }

    // Parse response: some servers reply with SSE (text/event-stream)
    const contentType = response.headers.get('content-type') || '';
    let result: any;
    if (contentType.includes('text/event-stream')) {
      const text = await response.text();
      // Try to find the last JSON chunk after a 'data:' prefix
      // Example chunk: "event: message\ndata: { ... }\n\n"
      const dataMatches = Array.from(text.matchAll(/\ndata:\s*(\{[\s\S]*?\})\s*(?:\n|$)/g));
      const last = dataMatches.length > 0 ? dataMatches[dataMatches.length - 1][1] : null;
      if (!last) {
        console.error('Failed to parse SSE response as JSON:', text.slice(0, 300));
        return NextResponse.json({
          success: false,
          error: 'Invalid SSE response from MCP server',
          details: text.slice(0, 500),
          testedUrl: resolvedUrl,
        }, { status: 200 });
      }
      try {
        result = JSON.parse(last);
      } catch (e) {
        console.error('SSE JSON parse error:', e);
        return NextResponse.json({
          success: false,
          error: 'Invalid JSON in SSE response',
          details: last.slice(0, 500),
          testedUrl: resolvedUrl,
        }, { status: 200 });
      }
    } else {
      // Regular JSON response
      result = await response.json();
    }
    console.log('MCP response:', result);

    // Check for JSON-RPC error
    if (result.error) {
      console.error('MCP server returned error:', result.error);
      return NextResponse.json({
        success: false,
        error: 'MCP server error',
        details: result.error.message || JSON.stringify(result.error),
        testedUrl: resolvedUrl,
      }, { status: 200 });
    }

    // Extract tools from the response
    const tools = result.result?.tools || result.tools || [];

    if (!Array.isArray(tools)) {
      console.error('Invalid tools response:', result);
      return NextResponse.json({
        success: false,
        error: 'Invalid response from MCP server',
        details: `Expected tools array, got: ${JSON.stringify(result).substring(0, 200)}`,
        testedUrl: resolvedUrl,
      }, { status: 200 });
    }

    if (tools.length === 0) {
      return NextResponse.json({
        success: false,
        error: 'No tools found',
        details: 'MCP server returned empty tools list',
        testedUrl: resolvedUrl,
      }, { status: 200 });
    }

    // Extract tool names
    const toolNames = tools.map((tool: any) => tool.name || tool);

    return NextResponse.json({
      success: true,
      tools: toolNames,
      toolsDetailed: tools,
      serverInfo: {
        name: result.result?.name || 'Unknown',
        version: result.result?.version || 'Unknown',
      },
    });

  } catch (error) {
    console.error('MCP connection test error:', error);
    return NextResponse.json({
      success: false,
      error: 'Connection test failed',
      details: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 200 });
  }
}
