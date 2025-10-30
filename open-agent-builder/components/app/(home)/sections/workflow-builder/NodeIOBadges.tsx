"use client";

import type { Node } from "@xyflow/react";

interface NodeIOBadgesProps {
  node: Node;
}

export default function NodeIOBadges({ node }: NodeIOBadgesProps) {
  const nodeData = node.data as any;
  const nodeType = nodeData.nodeType;

  // Get output info (just show output, not input)
  const getOutputInfo = (): string | null => {
    if (nodeType === 'end') return null;
    if (nodeType === 'note') return null;
    if (nodeType === 'start') return null;

    // Check output mapping
    if (nodeData.outputMapping) {
      if (nodeData.outputMapping.outputAs === 'field') {
        return nodeData.outputMapping.fieldName;
      }
      if (nodeData.outputMapping.outputAs === 'custom') {
        return 'custom';
      }
    }

    // Check specific field outputs
    if (nodeData.outputField && nodeData.outputField !== 'full') {
      return nodeData.outputField;
    }

    // Check for JSON schema
    if (nodeData.jsonOutputSchema) {
      try {
        const schema = JSON.parse(nodeData.jsonOutputSchema);
        if (schema.properties) {
          const fields = Object.keys(schema.properties);
          if (fields.length === 1) {
            return fields[0];
          }
          if (fields.length === 2) {
            return fields.join(', ');
          }
          return `${fields.length} fields`;
        }
      } catch (e) {
        // Invalid schema
      }
    }

    return null; // Don't show badge if no specific output
  };

  const outputInfo = getOutputInfo();

  if (!outputInfo) return null;

  return (
    <div className="absolute -bottom-3 right-2 pointer-events-none">
      {/* Subtle Output Indicator */}
      <div className="px-4 py-1 bg-black-alpha-4 text-black-alpha-48 text-[9px] font-mono rounded-full border border-border-faint whitespace-nowrap">
        → {outputInfo}
      </div>
    </div>
  );
}
