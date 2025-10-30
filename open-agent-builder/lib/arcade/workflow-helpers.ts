/**
 * Arcade.dev Workflow Helpers
 * Easy-to-use functions for adding Arcade tools to workflows
 */

import { WorkflowNode } from '../workflow/types';
import { getArcadeMCPConfig, generateArcadeInstructions, ARCADE_TOOLS } from './tools';

/**
 * Create an agent node that uses an Arcade.dev tool
 *
 * Example usage:
 * ```ts
 * const googleDocNode = createArcadeAgentNode({
 *   id: 'create-doc',
 *   toolId: 'google-docs-create',
 *   position: { x: 500, y: 200 },
 *   params: {
 *     title: 'Executive Summary - {{input.query}}',
 *     text_content: '{{lastOutput}}',
 *     user_id: '{{input.user_id}}'
 *   }
 * });
 * ```
 */
export function createArcadeAgentNode(config: {
  id: string;
  toolId: keyof typeof ARCADE_TOOLS;
  position: { x: number; y: number };
  params: Record<string, string>;
  model?: string;
}): WorkflowNode {
  const arcadeConfig = getArcadeMCPConfig(config.toolId);
  const instructions = generateArcadeInstructions(config.toolId, config.params);

  return {
    id: config.id,
    type: 'agent',
    position: config.position,
    data: {
      label: arcadeConfig.name,
      nodeType: 'agent',
      nodeName: arcadeConfig.name,
      instructions,
      model: config.model || 'anthropic/claude-sonnet-4-20250514',
      outputFormat: 'Text',
      tools: [arcadeConfig.mcpServer.id],
      mcpTools: [
        {
          name: arcadeConfig.mcpServer.name,
          url: arcadeConfig.mcpServer.url,
          accessToken: arcadeConfig.mcpServer.accessToken,
        },
      ],
    },
  };
}

/**
 * Quick presets for common Arcade tool combinations
 */
export const ArcadePresets = {
  /**
   * Create a Google Doc from text
   */
  googleDoc: (id: string, position: { x: number; y: number }) =>
    createArcadeAgentNode({
      id,
      toolId: 'google-docs-create',
      position,
      params: {
        title: 'Document - {{input.query}}',
        text_content: '{{lastOutput}}',
        user_id: '{{input.user_id}}',
      },
    }),

  /**
   * Create a Google Sheet from data
   */
  googleSheet: (id: string, position: { x: number; y: number }) =>
    createArcadeAgentNode({
      id,
      toolId: 'google-sheets-create',
      position,
      params: {
        title: 'Data - {{input.query}}',
        data: '{{lastOutput}}',
        user_id: '{{input.user_id}}',
      },
    }),

  /**
   * Send a Slack message
   */
  slackMessage: (id: string, position: { x: number; y: number }, channel: string = 'general') =>
    createArcadeAgentNode({
      id,
      toolId: 'slack-send',
      position,
      params: {
        channel,
        message: '{{lastOutput}}',
        user_id: '{{input.user_id}}',
      },
    }),

  /**
   * Send an email via Gmail
   */
  gmail: (id: string, position: { x: number; y: number }) =>
    createArcadeAgentNode({
      id,
      toolId: 'gmail-send',
      position,
      params: {
        to: '{{input.email}}',
        subject: 'Report: {{input.query}}',
        body: '{{lastOutput}}',
        user_id: '{{input.user_id}}',
      },
    }),

  /**
   * Create a Notion page
   */
  notionPage: (id: string, position: { x: number; y: number }) =>
    createArcadeAgentNode({
      id,
      toolId: 'notion-create-page',
      position,
      params: {
        title: '{{input.query}}',
        content: '{{lastOutput}}',
        user_id: '{{input.user_id}}',
      },
    }),
};

/**
 * Get a list of all available Arcade tools for display in UI
 */
export function listArcadeTools() {
  return Object.entries(ARCADE_TOOLS).map(([key, tool]) => ({
    id: key,
    name: tool.name,
    description: tool.description,
    category: tool.category,
    toolName: tool.toolName,
    inputs: tool.inputs,
  }));
}
