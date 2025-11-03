/**
 * Example Templates Index
 *
 * This file exports all example templates organized by complexity level.
 * Each example demonstrates specific features and use cases.
 */

import { simpleAgent } from './01-simple-agent';

export const exampleTemplates = {
  'example-01-simple-agent': simpleAgent,
};

export const exampleTemplatesList = [
  {
    id: 'example-01-simple-agent',
    name: 'Example 1: Simple Agent',
    description: 'A basic workflow with one agent that answers questions',
    difficulty: 'beginner',
    estimatedTime: '1-2 minutes',
  },
];
