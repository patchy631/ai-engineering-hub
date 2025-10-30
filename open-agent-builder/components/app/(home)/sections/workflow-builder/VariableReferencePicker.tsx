"use client";

import { useState } from "react";
import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { Node } from "@xyflow/react";

interface VariableReferencePickerProps {
  nodes: Node[];
  currentNodeId: string;
  onSelect: (reference: string) => void;
}

export default function VariableReferencePicker({ nodes, currentNodeId, onSelect }: VariableReferencePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ top: 0, right: 0 });
  const buttonRef = React.useRef<HTMLButtonElement>(null);

  // Get nodes that come before current node
  const availableNodes = nodes.filter(n => n.id !== currentNodeId);

  // Get input variables from Start node
  const startNode = nodes.find(n => (n.data as any)?.nodeType === 'start');
  const inputVariables = (startNode?.data as any)?.inputVariables || [];

  // Build variable list with schema fields - using simple notation
  const nodeVariables = availableNodes.flatMap(n => {
    const nodeData = n.data as any;

    // Skip Start node - we'll add its input variables separately
    if (nodeData.nodeType === 'start') {
      return [];
    }

    // Convert node ID to simple variable name (replace hyphens with underscores)
    const nodeVarName = n.id.replace(/-/g, '_');

    const baseVar = {
      name: nodeData.nodeName || n.id,
      path: nodeVarName, // Simple notation!
      description: `Output from ${nodeData.nodeName || n.id}`,
      nodeType: nodeData.nodeType,
    } as any;

    const vars = [baseVar];

    // If node has JSON output schema, add individual field references
    if (nodeData.jsonOutputSchema) {
      try {
        const schema = JSON.parse(nodeData.jsonOutputSchema);
        if (schema.properties) {
          Object.keys(schema.properties).forEach(propName => {
            const propSchema = schema.properties[propName];
            const propType = propSchema.type || 'any';

            vars.push({
              name: `${nodeData.nodeName || n.id}.${propName}`,
              path: `${nodeVarName}.${propName}`, // Simple notation!
              description: propSchema.description || `${propName} field from ${nodeData.nodeName || n.id}`,
              nodeType: nodeData.nodeType,
              propertyType: propType,
              isField: true,
            } as any);

            // If property is an object, add nested fields
            if (propSchema.properties) {
              Object.keys(propSchema.properties).forEach(nestedProp => {
                vars.push({
                  name: `${nodeData.nodeName || n.id}.${propName}.${nestedProp}`,
                  path: `${nodeVarName}.${propName}.${nestedProp}`,
                  description: `${nestedProp} in ${propName}`,
                  nodeType: nodeData.nodeType,
                  isField: true,
                  isNested: true,
                } as any);
              });
            }
          });
        }
      } catch (e) {
        // Invalid JSON, skip
      }
    }

    return vars;
  });

  // Build input variables from Start node
  const startNodeInputs = inputVariables.map((v: any) => ({
    name: v.name,
    path: `input.${v.name}`, // Reference input variables as input.variableName
    description: v.description || `Input: ${v.name}`,
    type: v.type,
    isInputVariable: true,
  }));

  const variables = [
    {
      category: "Input Variables",
      items: startNodeInputs,
    },
    {
      category: "Workflow",
      items: [
        { name: "input (full object)", path: "input", description: "All workflow inputs as object" },
        { name: "lastOutput", path: "lastOutput", description: "Output from previous node" },
      ],
    },
    {
      category: "Previous Nodes",
      items: nodeVariables,
    },
  ].filter(group => group.items.length > 0); // Remove empty groups

  const handleOpen = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setButtonPosition({
        top: rect.bottom + 8,
        right: window.innerWidth - rect.right,
      });
    }
    setIsOpen(!isOpen);
  };

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={handleOpen}
        className="px-12 py-6 bg-heat-4 hover:bg-heat-8 border border-heat-100 rounded-6 text-body-small text-heat-100 transition-colors flex items-center gap-6"
      >
        <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
        </svg>
        Insert Variable
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop to close on click outside */}
            <div
              className="fixed inset-0 z-[9998]"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="fixed w-400 max-w-[calc(100vw-40px)] bg-accent-white border border-border-faint rounded-12 shadow-2xl z-[9999] overflow-hidden"
              style={{
                top: `${buttonPosition.top}px`,
                right: `${buttonPosition.right}px`,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-12 border-b border-border-faint">
                <h4 className="text-label-small text-accent-black">Available Variables</h4>
              </div>

            <div className="max-h-320 overflow-y-auto">
              {variables.map((group, groupIndex) => (
                <div key={groupIndex}>
                  <div className="px-12 py-8 bg-background-base">
                    <p className="text-body-small text-black-alpha-48 font-medium">
                      {group.category}
                    </p>
                  </div>

                  {group.items.map((item: any, itemIndex) => (
                    <button
                      key={itemIndex}
                      onClick={() => {
                        onSelect(item.path);
                        setIsOpen(false);
                      }}
                      className={`w-full px-12 py-10 text-left hover:bg-heat-4 transition-colors border-b border-border-faint last:border-0 ${
                        item.isField ? 'pl-24 bg-background-base' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between gap-8">
                        <div className="flex-1 min-w-0">
                          {item.isNested && (
                            <span className="text-body-small text-heat-100 mr-6">↳↳</span>
                          )}
                          {item.isField && !item.isNested && (
                            <span className="text-body-small text-heat-100 mr-6">↳</span>
                          )}
                          <p className={`text-body-small font-medium break-all ${
                            item.isField || item.isInputVariable || item.isNested ? 'text-heat-100' : 'text-accent-black'
                          }`}>
                            {item.name}
                          </p>
                          <p className="text-body-small text-black-alpha-48 mt-2 font-mono text-[10px]">
                            {`{{${item.path}}}`}
                          </p>
                          {item.description && (
                            <p className="text-body-small text-black-alpha-48 mt-4 truncate">
                              {item.description}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col gap-4 items-end">
                          {item.propertyType && (
                            <span className="px-6 py-2 bg-black-alpha-4 text-black-alpha-64 rounded-4 text-[10px] font-medium flex-shrink-0">
                              {item.propertyType}
                            </span>
                          )}
                          {(item.nodeType || item.type) && (
                            <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-4 text-body-small font-medium flex-shrink-0">
                              {item.nodeType || item.type}
                            </span>
                          )}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              ))}
            </div>

              <div className="p-12 bg-background-base border-t border-border-faint">
                <p className="text-body-small text-black-alpha-48">
                  Click a variable to insert its reference
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
