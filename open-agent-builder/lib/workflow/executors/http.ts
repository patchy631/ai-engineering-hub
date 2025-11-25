import { WorkflowNode, WorkflowState } from '../types';
import { substituteVariables } from '../variable-substitution';

/**
 * Execute HTTP Request Node
 */
export async function executeHTTPNode(
  node: WorkflowNode,
  state: WorkflowState
): Promise<any> {
  const { data } = node;
  const nodeData = data as any;

  try {
    // Substitute variables in URL
    const url = substituteVariables(nodeData.httpUrl || '', state);
    const method = nodeData.httpMethod || 'GET';

    // Build headers
    const headers: Record<string, string> = {};

    if (nodeData.httpHeaders && Array.isArray(nodeData.httpHeaders)) {
      nodeData.httpHeaders.forEach((h: any) => {
        if (h.key && h.value) {
          headers[h.key] = substituteVariables(h.value, state);
        }
      });
    }

    // Add authentication
    if (nodeData.httpAuthType === 'bearer' && nodeData.httpAuthToken) {
      headers['Authorization'] = `Bearer ${nodeData.httpAuthToken}`;
    } else if (nodeData.httpAuthType === 'api-key' && nodeData.httpAuthToken) {
      headers['X-API-Key'] = nodeData.httpAuthToken;
    } else if (nodeData.httpAuthType === 'basic' && nodeData.httpAuthToken) {
      headers['Authorization'] = `Basic ${btoa(nodeData.httpAuthToken)}`;
    }

    // Build request body
    let body: string | undefined = undefined;
    if ((method === 'POST' || method === 'PUT' || method === 'PATCH') && nodeData.httpBody) {
      body = substituteVariables(nodeData.httpBody, state);
    }

    console.log('HTTP Request:', { method, url, headers, body });

    // Make the request
    const response = await fetch(url, {
      method,
      headers,
      body,
    });

    const responseData = await response.json().catch(() => response.text());

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries()),
      data: responseData,
      url,
      method,
    };
  } catch (error) {
    console.error('HTTP request error:', error);
    throw new Error(`HTTP request failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
