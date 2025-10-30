import 'server-only';
import { WorkflowNode, WorkflowState } from '../types';
import { substituteVariables } from '../variable-substitution';
import Arcade from '@arcadeai/arcadejs';

/**
 * Execute Arcade Node - Uses Arcade SDK for tool execution
 * Server-side only - called from API routes
 * Handles authorization and tool execution for Arcade.dev integrations
 */
export async function executeArcadeNode(
  node: WorkflowNode,
  state: WorkflowState,
  apiKey?: string
): Promise<any> {
  const { data } = node;

  try {
    // Get Arcade configuration
    const arcadeTool = (data as any).arcadeTool; // e.g., "GoogleDocs.CreateDocumentFromText@4.3.1"
    // Support both arcadeInput (templates) and arcadeParams (UI panel)
    const arcadeInput = (data as any).arcadeInput || (data as any).arcadeParams || {};
    const arcadeUserId = (data as any).arcadeUserId || 'workflow-builder';

    if (!arcadeTool) {
      throw new Error('Arcade tool not configured. Please open the node settings and select a tool from the Arcade.dev catalog.');
    }

    // Substitute variables in the input
    const substitutedInput: any = {};
    for (const [key, value] of Object.entries(arcadeInput)) {
      if (typeof value === 'string') {
        substitutedInput[key] = substituteVariables(value, state);
      } else {
        substitutedInput[key] = value;
      }
    }

    console.log('📝 Arcade Input (after substitution):', JSON.stringify(substitutedInput, null, 2));

    const arcadeApiKey = apiKey ?? process.env.ARCADE_API_KEY;

    if (!arcadeApiKey) {
      throw new Error('ARCADE_API_KEY not configured in .env.local');
    }

    console.log('🎮 Arcade Node Execution:', { tool: arcadeTool, userId: arcadeUserId });

    // Initialize Arcade client
    const client = new Arcade({ apiKey: arcadeApiKey });

    // Step 1: Authorize the tool
    const auth = await client.tools.authorize({
      tool_name: arcadeTool,
      user_id: arcadeUserId,
    });

    console.log('🔐 Arcade Auth Status:', auth.status);

    if (!auth?.id) {
      throw new Error('Authorization failed: missing authorization id from Arcade');
    }

    // Check if authorization is completed
    if (auth.status === 'failed') {
      throw new Error(`Authorization failed for ${arcadeTool}`);
    }

    if (auth.status !== 'completed') {
      console.log('⚠️ Authorization required:', auth.url);

      return {
        __arcadePendingAuth: true,
        authUrl: auth.url,
        authId: auth.id,
        toolName: arcadeTool,
        userId: arcadeUserId,
        message: `Authorization required for ${arcadeTool}`,
        pendingInput: substitutedInput,
      };
    }

    console.log('✅ Authorization successful!');

    // Step 2: Execute the tool
    const result = await client.tools.execute({
      tool_name: arcadeTool,
      input: substitutedInput,
      user_id: arcadeUserId,
    });

    console.log('🎯 Arcade Result:', JSON.stringify(result, null, 2).substring(0, 500));

    // Extract the output value
    const output = result.output?.value || result.output || result;

    return {
      success: true,
      result: output,
      fullResult: result,
      toolUsed: arcadeTool,
      userId: arcadeUserId,
      __variableUpdates: { lastOutput: output }, // Return as separate field for reducer
    };

  } catch (error: any) {
    console.error('❌ Arcade execution error:', error);
    throw new Error(`Arcade execution failed: ${error.message || 'Unknown error'}`);
  }
}
