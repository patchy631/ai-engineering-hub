import type { WorkflowNode, WorkflowEdge } from './types';

/**
 * Clean up invalid edges that point to non-existent nodes
 * This handles corrupted workflow data where edges reference deleted nodes
 */
export function cleanupInvalidEdges(
  nodes: WorkflowNode[],
  edges: WorkflowEdge[]
): { nodes: WorkflowNode[]; edges: WorkflowEdge[]; removedCount: number } {
  const validNodeIds = new Set(nodes.map(n => n.id));
  const validEdges: WorkflowEdge[] = [];
  let removedCount = 0;

  for (const edge of edges) {
    // Check if both source and target nodes exist
    const sourceExists = validNodeIds.has(edge.source);
    const targetExists = validNodeIds.has(edge.target);

    if (!sourceExists || !targetExists) {
      console.warn(`🧹 Removing invalid edge ${edge.id}: source=${edge.source} (exists: ${sourceExists}), target=${edge.target} (exists: ${targetExists})`);
      removedCount++;
      continue;
    }

    validEdges.push(edge);
  }

  if (removedCount > 0) {
    console.log(`✅ Cleaned up ${removedCount} invalid edge(s) from workflow`);
  }

  return {
    nodes,
    edges: validEdges,
    removedCount,
  };
}
