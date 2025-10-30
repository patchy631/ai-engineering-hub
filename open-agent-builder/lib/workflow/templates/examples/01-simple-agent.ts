import { Workflow } from '../../types';

/**
 * Example 1: Simple Agent
 *
 * This is the most basic workflow possible - just a single agent that responds to a question.
 *
 * Flow: Start -> Agent -> End
 *
 * Use case: Basic Q&A, simple text generation, single-turn conversations
 */
export const simpleAgent: Workflow = {
  id: 'example-01-simple-agent',
  name: 'Example 1: Simple Agent',
  description: 'A basic workflow with one agent that answers questions',
  category: 'examples',
  tags: ['example', 'beginner', 'basic'],
  estimatedTime: '1-2 minutes',
  difficulty: 'beginner',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  nodes: [
    {
      id: 'start',
      type: 'start',
      position: { x: 100, y: 200 },
      data: {
        label: 'Start',
        nodeType: 'start',
        nodeName: 'Start',
        inputVariables: [
          {
            name: 'question',
            type: 'string',
            required: true,
            description: 'Your question for the AI agent',
            defaultValue: 'What are the key benefits of using AI agents in workflow automation?',
          },
        ],
      },
    },
    {
      id: 'agent',
      type: 'agent',
      position: { x: 350, y: 200 },
      data: {
        label: 'Answer Question',
        nodeType: 'agent',
        nodeName: 'Answer Question',
        instructions: `You are a helpful AI assistant. Please provide a clear, concise answer to the following question:

{{input.question}}

Provide a well-structured response that is informative and easy to understand.`,
        model: 'anthropic/claude-sonnet-4-20250514',
        outputFormat: 'Text',
      },
    },
    {
      id: 'end',
      type: 'end',
      position: { x: 600, y: 200 },
      data: {
        label: 'End',
        nodeType: 'end',
        nodeName: 'End',
      },
    },
  ],
  edges: [
    { id: 'e1', source: 'start', target: 'agent' },
    { id: 'e2', source: 'agent', target: 'end' },
  ],
};
