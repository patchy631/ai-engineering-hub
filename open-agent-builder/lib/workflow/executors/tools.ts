import 'server-only';
import { WorkflowNode, WorkflowState } from '../types';

/**
 * Execute Tools Nodes - File Search, Guardrails
 * Server-side only - called from API routes
 */
export async function executeToolsNode(
  node: WorkflowNode,
  state: WorkflowState
): Promise<any> {
  const { type, data } = node;
  const nodeType = (data as any).nodeType || type;

  if (nodeType.includes('file') || nodeType === 'file-search') {
    return await executeFileSearch(data, state);
  }

  if (nodeType.includes('guardrail')) {
    return await executeGuardrails(data, state);
  }

  throw new Error(`Unknown tools node type: ${nodeType}`);
}

async function executeFileSearch(data: any, state: WorkflowState): Promise<any> {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 800));

  // Mock file search results
  const mockFiles = [
    {
      path: 'src/components/Button.tsx',
      matches: 3,
      content: includeContent(data) ? 'export default function Button() { ... }' : undefined,
    },
    {
      path: 'src/utils/helpers.ts',
      matches: 2,
      content: includeContent(data) ? 'export function formatData() { ... }' : undefined,
    },
    {
      path: 'app/page.tsx',
      matches: 1,
      content: includeContent(data) ? 'export default function Home() { ... }' : undefined,
    },
  ];

  const maxResults = parseInt(data.maxResults || '10');
  const results = mockFiles.slice(0, maxResults);

  return {
    query: data.searchQuery || '',
    pattern: data.filePattern || '*.ts,*.tsx',
    results,
    totalMatches: results.length,
    filesSearched: 156,
  };
}

function includeContent(data: any): boolean {
  return data.includeContent !== false;
}

async function executeGuardrails(data: any, state: WorkflowState): Promise<any> {
  const inputText = state.variables['lastOutput'] || state.variables['input'] || '';
  const textToCheck = typeof inputText === 'string' ? inputText : JSON.stringify(inputText);

  // Check which guardrails are enabled
  const enabledChecks: string[] = [];
  if (data.piiEnabled) enabledChecks.push('PII');
  if (data.moderationEnabled) enabledChecks.push('Moderation');
  if (data.jailbreakEnabled) enabledChecks.push('Jailbreak');
  if (data.hallucinationEnabled) enabledChecks.push('Hallucination');

  console.log('🛡️ Guardrails check:', enabledChecks.join(', '));
  console.log('📝 Checking text:', textToCheck.substring(0, 100));

  // Server-side implementation: basic checks
  // TODO: Integrate with actual content moderation APIs
  const badWords = ['hack', 'exploit', 'attack', 'spam'];
  const lowerText = textToCheck.toLowerCase();
  const hasBadWord = badWords.some(word => lowerText.includes(word));

  if (hasBadWord && data.actionOnViolation === 'block') {
    throw new Error(`Guardrail violation: Potentially harmful content detected`);
  }

  return {
    passed: !hasBadWord,
    checks_run: enabledChecks,
    violations: hasBadWord ? ['Harmful content detected'] : [],
    message: hasBadWord ? 'Content flagged' : `All guardrails passed (${enabledChecks.length} checks)`,
  };
}

/**
 * TODO: Real implementation
 *
 * For file-search:
 * - Use ripgrep or similar fast search
 * - Support glob patterns
 * - Index codebase for faster searching
 * - Return file paths and line numbers
 *
 * For guardrails:
 * - Integrate with content moderation APIs
 * - Use regex patterns for PII detection
 * - Custom rule engine for business logic
 * - Rate limiting and abuse prevention
 */
