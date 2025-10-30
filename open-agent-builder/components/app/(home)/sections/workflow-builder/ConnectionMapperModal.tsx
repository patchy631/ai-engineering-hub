"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import type { Node } from "@xyflow/react";

interface ConnectionMapperModalProps {
  sourceNode: Node | null;
  targetNode: Node | null;
  isOpen: boolean;
  onClose: () => void;
  onConnect: (mapping: Record<string, string>) => void;
}

export default function ConnectionMapperModal({
  sourceNode,
  targetNode,
  isOpen,
  onClose,
  onConnect,
}: ConnectionMapperModalProps) {
  const [mapping, setMapping] = useState<Record<string, string>>({});

  if (!sourceNode || !targetNode) return null;

  const sourceData = sourceNode.data as any;
  const targetData = targetNode.data as any;

  // Get output keys from source node
  const getOutputKeys = (node: Node): string[] => {
    const data = node.data as any;
    const keys: string[] = [];

    // Check if there's an outputSchema defined
    if (data.outputSchema && Array.isArray(data.outputSchema)) {
      keys.push(...data.outputSchema.map((field: any) => field.name));
    }

    // Check if JSON output with schema
    if (data.jsonOutputSchema) {
      try {
        const schema = JSON.parse(data.jsonOutputSchema);
        if (schema.properties) {
          keys.push(...Object.keys(schema.properties));
        }
      } catch (e) {
        // Invalid JSON
      }
    }

    // Add default keys based on node type
    const nodeType = data.nodeType;
    if (nodeType === 'mcp' || nodeType === 'firecrawl') {
      const outputField = data.outputField || 'full';
      if (outputField === 'markdown') keys.push('markdown');
      else if (outputField === 'html') keys.push('html');
      else if (outputField === 'metadata') keys.push('metadata', 'metadata.title', 'metadata.description');
      else if (outputField === 'results') keys.push('results[]', 'results[0]');
      else if (outputField === 'urls') keys.push('urls[]');
      else if (outputField === 'json') keys.push('json');
      else keys.push('*');
    }

    // If no specific keys, add common ones
    if (keys.length === 0) {
      keys.push('message', 'data', 'result');
    }

    return keys;
  };

  // Get input keys from target node (from arguments)
  const getInputKeys = (node: Node): string[] => {
    const data = node.data as any;

    if (data.arguments && Array.isArray(data.arguments)) {
      return data.arguments.map((arg: any) => arg.name);
    }

    return ['input'];
  };

  const sourceKeys = getOutputKeys(sourceNode);
  const targetKeys = getInputKeys(targetNode);

  const handleConnect = () => {
    onConnect(mapping);
    onClose();
  };

  const handleQuickConnect = () => {
    // Auto-map matching field names
    const autoMapping: Record<string, string> = {};

    targetKeys.forEach(targetKey => {
      // Try to find exact match
      const exactMatch = sourceKeys.find(sk => sk === targetKey);
      if (exactMatch) {
        autoMapping[targetKey] = exactMatch;
        return;
      }

      // Try partial match
      const partialMatch = sourceKeys.find(sk =>
        sk.toLowerCase().includes(targetKey.toLowerCase()) ||
        targetKey.toLowerCase().includes(sk.toLowerCase())
      );
      if (partialMatch) {
        autoMapping[targetKey] = partialMatch;
      }
    });

    setMapping(autoMapping);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black-alpha-48 z-[200] flex items-center justify-center p-20"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-accent-white rounded-16 shadow-2xl max-w-600 w-full max-h-[80vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="p-24 border-b border-border-faint">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-title-h3 text-accent-black">Map Connection</h2>
                  <p className="text-body-small text-black-alpha-48 mt-4">
                    {sourceData.nodeName} → {targetData.nodeName}
                  </p>
                </div>
                <button
                  onClick={onClose}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                >
                  <svg className="w-16 h-16 text-black-alpha-48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-24 space-y-20">
              {/* Quick Auto-Map */}
              <button
                onClick={handleQuickConnect}
                className="w-full px-16 py-10 bg-heat-4 hover:bg-heat-8 border border-heat-100 rounded-8 text-body-medium text-heat-100 transition-colors flex items-center justify-center gap-8"
              >
                <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Auto-Map Fields
              </button>

              {/* Mapping Grid */}
              <div className="space-y-12">
                <div className="grid grid-cols-2 gap-12 pb-12 border-b border-border-faint">
                  <p className="text-label-small text-black-alpha-48">From ({sourceData.nodeName})</p>
                  <p className="text-label-small text-black-alpha-48">To ({targetData.nodeName})</p>
                </div>

                {targetKeys.map((targetKey) => (
                  <div key={targetKey} className="grid grid-cols-2 gap-12 items-center">
                    <select
                      value={mapping[targetKey] || ''}
                      onChange={(e) => setMapping({ ...mapping, [targetKey]: e.target.value })}
                      className="px-12 py-8 bg-background-base border border-border-faint rounded-6 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                    >
                      <option value="">-- Select source --</option>
                      <option value="__full__">Full Output</option>
                      {sourceKeys.map((sourceKey) => (
                        <option key={sourceKey} value={sourceKey}>
                          {sourceKey}
                        </option>
                      ))}
                    </select>

                    <div className="flex items-center gap-8">
                      <svg className="w-12 h-12 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      <code className="text-body-small text-accent-black font-mono">{targetKey}</code>
                    </div>
                  </div>
                ))}
              </div>

              {/* Preview */}
              {Object.keys(mapping).length > 0 && (
                <div className="p-16 bg-blue-50 rounded-12 border border-blue-200">
                  <h3 className="text-label-small text-blue-900 mb-8 font-medium">Connection Preview</h3>
                  <div className="space-y-4 text-body-small text-blue-800 font-mono">
                    {Object.entries(mapping).map(([target, source]) => (
                      <div key={target}>
                        {target} = {source === '__full__' ? 'entire output' : source}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-24 border-t border-border-faint flex items-center justify-between">
              <button
                onClick={() => {
                  setMapping({});
                  onConnect({});
                }}
                className="px-20 py-10 text-body-medium text-black-alpha-48 hover:text-accent-black transition-colors"
              >
                Skip Mapping
              </button>
              <button
                onClick={handleConnect}
                className="px-24 py-10 bg-heat-100 hover:bg-heat-200 text-white rounded-8 transition-all active:scale-[0.98] text-body-medium font-medium"
              >
                Connect
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
