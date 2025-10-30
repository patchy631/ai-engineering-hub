import { ARCADE_TOOLS, ArcadeTool } from './tools';
import Arcade from '@arcadeai/arcadejs';

/**
 * Convert Arcade tools to OpenAI function calling format
 */
export function arcadeToolToOpenAIFunction(arcadeTool: ArcadeTool) {
  const properties: Record<string, any> = {};
  const required: string[] = [];

  arcadeTool.inputs.forEach((input) => {
    properties[input.name] = {
      type: input.type === 'array' ? 'array' : 'string',
      description: input.description,
    };

    if (input.required && input.name !== 'user_id') {
      required.push(input.name);
    }
  });

  return {
    type: 'function' as const,
    function: {
      name: `arcade_${arcadeTool.id}`,
      description: arcadeTool.description,
      parameters: {
        type: 'object',
        properties,
        required,
      },
    },
  };
}

/**
 * Get all Arcade tools in OpenAI function format
 */
export function getAllArcadeToolsForOpenAI() {
  return Object.values(ARCADE_TOOLS).map(arcadeToolToOpenAIFunction);
}

/**
 * Execute an Arcade tool that was called by OpenAI
 */
export async function executeArcadeToolCall(
  toolName: string, // e.g., "arcade_google-docs-create"
  args: any,
  userId: string = 'workflow-builder'
): Promise<{
  success: boolean;
  result?: any;
  needsAuth?: boolean;
  authUrl?: string;
  authId?: string;
  error?: string;
}> {
  try {
    // Extract the tool ID from the function name (remove "arcade_" prefix)
    const toolId = toolName.replace('arcade_', '');
    const arcadeTool = ARCADE_TOOLS[toolId];

    if (!arcadeTool) {
      return {
        success: false,
        error: `Arcade tool not found: ${toolId}`,
      };
    }

    const ARCADE_API_KEY = process.env.ARCADE_API_KEY;
    if (!ARCADE_API_KEY) {
      return {
        success: false,
        error: 'ARCADE_API_KEY not configured',
      };
    }

    const fullToolName = `${arcadeTool.toolName}@${arcadeTool.version}`;

    console.log('🎮 Executing Arcade Tool:', fullToolName, 'Args:', args);

    // Initialize Arcade client
    const client = new Arcade({ apiKey: ARCADE_API_KEY });

    // Step 1: Check/request authorization
    const auth = await client.tools.authorize({
      tool_name: fullToolName,
      user_id: userId,
    });

    if (auth.status !== 'completed') {
      console.log('⚠️ Authorization required:', auth.url);
      return {
        success: false,
        needsAuth: true,
        authUrl: auth.url,
        authId: auth.id,
      };
    }

    console.log('✅ Authorization successful, executing tool...');

    // Step 2: Execute the tool
    const result = await client.tools.execute({
      tool_name: fullToolName,
      input: args,
      user_id: userId,
    });

    console.log('🎯 Arcade Result:', JSON.stringify(result, null, 2).substring(0, 500));

    return {
      success: true,
      result: result.output?.value || result.output || result,
    };
  } catch (error: any) {
    console.error('❌ Arcade tool execution error:', error);
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
}

/**
 * Check if a tool name is an Arcade tool
 */
export function isArcadeTool(toolName: string): boolean {
  return toolName.startsWith('arcade_');
}

/**
 * Get selected Arcade tools in OpenAI format by IDs
 */
export function getSelectedArcadeTools(toolIds: string[]) {
  return toolIds
    .map((id) => ARCADE_TOOLS[id])
    .filter(Boolean)
    .map(arcadeToolToOpenAIFunction);
}
