/**
 * Arcade.dev MCP Tools Registry
 * Centralized configuration for all Arcade.dev integrations
 */

export interface ArcadeTool {
  id: string;
  name: string;
  toolName: string;
  version: string;
  description: string;
  category: 'google' | 'microsoft' | 'slack' | 'notion' | 'other';
  inputs: {
    name: string;
    type: string;
    required: boolean;
    description: string;
  }[];
}

/**
 * Registry of available Arcade.dev tools
 * Add new tools here to make them available in workflows
 */
export const ARCADE_TOOLS: Record<string, ArcadeTool> = {
  'google-docs-create': {
    id: 'google-docs-create',
    name: 'Create Google Doc',
    toolName: 'GoogleDocs.CreateDocumentFromText',
    version: '4.3.1',
    description: 'Create a new Google Doc from text content',
    category: 'google',
    inputs: [
      {
        name: 'title',
        type: 'string',
        required: true,
        description: 'Document title',
      },
      {
        name: 'text_content',
        type: 'string',
        required: true,
        description: 'Text content for the document',
      },
      {
        name: 'user_id',
        type: 'string',
        required: false,
        description: 'User ID for authorization',
      },
    ],
  },
  'google-sheets-create': {
    id: 'google-sheets-create',
    name: 'Create Google Sheet',
    toolName: 'GoogleSheets.CreateSpreadsheet',
    version: '4.3.1',
    description: 'Create a new Google Sheet with data',
    category: 'google',
    inputs: [
      {
        name: 'title',
        type: 'string',
        required: true,
        description: 'Spreadsheet title',
      },
      {
        name: 'data',
        type: 'array',
        required: true,
        description: 'Array of rows (each row is an array of values)',
      },
      {
        name: 'user_id',
        type: 'string',
        required: false,
        description: 'User ID for authorization',
      },
    ],
  },
  'google-slides-create': {
    id: 'google-slides-create',
    name: 'Create Google Slides',
    toolName: 'GoogleSlides.CreatePresentation',
    version: '4.3.1',
    description: 'Create a new Google Slides presentation',
    category: 'google',
    inputs: [
      {
        name: 'title',
        type: 'string',
        required: true,
        description: 'Presentation title',
      },
      {
        name: 'slides',
        type: 'array',
        required: true,
        description: 'Array of slide objects with title and content',
      },
      {
        name: 'user_id',
        type: 'string',
        required: false,
        description: 'User ID for authorization',
      },
    ],
  },
  'gmail-send': {
    id: 'gmail-send',
    name: 'Send Gmail',
    toolName: 'Gmail.SendEmail',
    version: '4.3.1',
    description: 'Send an email via Gmail',
    category: 'google',
    inputs: [
      {
        name: 'to',
        type: 'string',
        required: true,
        description: 'Recipient email address',
      },
      {
        name: 'subject',
        type: 'string',
        required: true,
        description: 'Email subject',
      },
      {
        name: 'body',
        type: 'string',
        required: true,
        description: 'Email body',
      },
      {
        name: 'user_id',
        type: 'string',
        required: false,
        description: 'User ID for authorization',
      },
    ],
  },
  'slack-send': {
    id: 'slack-send',
    name: 'Send Slack Message',
    toolName: 'Slack.SendMessage',
    version: '4.3.1',
    description: 'Send a message to a Slack channel',
    category: 'slack',
    inputs: [
      {
        name: 'channel',
        type: 'string',
        required: true,
        description: 'Channel name or ID',
      },
      {
        name: 'message',
        type: 'string',
        required: true,
        description: 'Message text',
      },
      {
        name: 'user_id',
        type: 'string',
        required: false,
        description: 'User ID for authorization',
      },
    ],
  },
  'notion-create-page': {
    id: 'notion-create-page',
    name: 'Create Notion Page',
    toolName: 'Notion.CreatePage',
    version: '4.3.1',
    description: 'Create a new page in Notion',
    category: 'notion',
    inputs: [
      {
        name: 'title',
        type: 'string',
        required: true,
        description: 'Page title',
      },
      {
        name: 'content',
        type: 'string',
        required: true,
        description: 'Page content (markdown supported)',
      },
      {
        name: 'parent_page_id',
        type: 'string',
        required: false,
        description: 'Parent page ID (optional)',
      },
      {
        name: 'user_id',
        type: 'string',
        required: false,
        description: 'User ID for authorization',
      },
    ],
  },
};

/**
 * Helper function to get Arcade MCP tool configuration for a workflow node
 */
export function getArcadeMCPConfig(toolId: string) {
  const tool = ARCADE_TOOLS[toolId];
  if (!tool) {
    throw new Error(`Arcade tool "${toolId}" not found in registry`);
  }

  return {
    toolId: tool.id,
    toolName: `${tool.toolName}@${tool.version}`,
    name: tool.name,
    description: tool.description,
    mcpServer: {
      id: `arcade-${tool.category}`,
      name: `Arcade.dev (${tool.category})`,
      label: `Arcade.dev (${tool.category})`,
      url: 'https://api.arcade.dev/v1',
      description: tool.description,
      authType: 'api-key',
      accessToken: '${ARCADE_API_KEY}',
      connected: false,
      tools: [tool.toolName],
    },
  };
}

/**
 * Helper function to generate agent instructions for an Arcade tool
 */
export function generateArcadeInstructions(
  toolId: string,
  params: Record<string, string>
): string {
  const tool = ARCADE_TOOLS[toolId];
  if (!tool) {
    throw new Error(`Arcade tool "${toolId}" not found in registry`);
  }

  const paramsList = tool.inputs
    .map((input) => {
      const value = params[input.name] || `{{${input.name}}}`;
      return `- ${input.name}: ${value}`;
    })
    .join('\n');

  return `You are an integration agent. Use the Arcade.dev ${tool.toolName} tool to ${tool.description.toLowerCase()}.

Use the ${tool.toolName} tool with the following parameters:
${paramsList}

Execute the tool and return the result, including any URLs or IDs from the response.`;
}

/**
 * Get all tools by category
 */
export function getToolsByCategory(category: string): ArcadeTool[] {
  return Object.values(ARCADE_TOOLS).filter((tool) => tool.category === category);
}

/**
 * Get all available categories
 */
export function getToolCategories(): string[] {
  return Array.from(new Set(Object.values(ARCADE_TOOLS).map((tool) => tool.category)));
}
