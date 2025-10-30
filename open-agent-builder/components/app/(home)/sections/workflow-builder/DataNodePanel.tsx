"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import type { Node } from "@xyflow/react";
import { toast } from "sonner";
import VariableReferencePicker from "./VariableReferencePicker";

interface DataNodePanelProps {
  node: Node | null;
  nodes: Node[];
  onClose: () => void;
  onDelete: (nodeId: string) => void;
  onUpdate: (nodeId: string, data: any) => void;
}

export default function DataNodePanel({
  node,
  nodes,
  onClose,
  onDelete,
  onUpdate,
}: DataNodePanelProps) {
  const nodeData = node?.data as any;
  const nodeType = nodeData?.nodeType?.toLowerCase() || "";

  // Transform state
  const [transformScript, setTransformScript] = useState(
    nodeData?.transformScript ||
      `// Transform the input data using TypeScript
// Available variables: input, lastOutput, state

// Example: Extract and transform data
const result = {
    processed: true,
    timestamp: input.timestamp || "",
    data: input
};

return result;`,
  );

  // Set State variables
  const [stateKey, setStateKey] = useState(nodeData?.stateKey || "myVariable");
  const [stateValue, setStateValue] = useState(nodeData?.stateValue || "value");
  const [valueType, setValueType] = useState<
    "string" | "number" | "boolean" | "json" | "expression"
  >(nodeData?.valueType || "string");

  // Auto-save changes
  useEffect(() => {
    if (!node?.id) return;

    const timeoutId = setTimeout(() => {
      onUpdate(node.id, {
        transformScript,
        stateKey,
        stateValue,
        valueType,
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [
    transformScript,
    stateKey,
    stateValue,
    valueType,
  ]);


  const renderValueInput = () => {
    switch (valueType) {
      case "boolean":
        return (
          <select
            value={stateValue}
            onChange={(e) => setStateValue(e.target.value)}
            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
          >
            <option value="true">true</option>
            <option value="false">false</option>
          </select>
        );
      case "number":
        return (
          <input
            type="text"
            value={stateValue}
            onChange={(e) => setStateValue(e.target.value)}
            placeholder="42 or {{lastOutput.count}}"
            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
          />
        );
      case "json":
        return (
          <textarea
            value={stateValue}
            onChange={(e) => setStateValue(e.target.value)}
            rows={4}
            placeholder='{"key": "value"} or {{lastOutput}}'
            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
          />
        );
      case "expression":
        return (
          <textarea
            value={stateValue}
            onChange={(e) => setStateValue(e.target.value)}
            rows={3}
            placeholder="input.price * 1.1"
            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
          />
        );
      default:
        return (
          <input
            type="text"
            value={stateValue}
            onChange={(e) => setStateValue(e.target.value)}
            placeholder="Hello {{input.name}}"
            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
          />
        );
    }
  };

  return (
    <AnimatePresence>
      {node && (
        <motion.aside
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 400, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed right-20 top-80 h-[calc(100vh-100px)] w-[calc(100vw-240px)] max-w-480 bg-accent-white border border-border-faint shadow-lg overflow-y-auto z-50 rounded-16"
        >
          {/* Header */}
          <div className="p-20 border-b border-border-faint">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-label-large text-accent-black font-medium">
                {nodeData?.nodeName || "Data"}
              </h2>
              <div className="flex items-center gap-8">
                <button
                  onClick={() => onDelete(node?.id || "")}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                  title="Delete node"
                >
                  <svg
                    className="w-16 h-16 text-black-alpha-48 group-hover:text-black-alpha-64"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
                <button
                  onClick={onClose}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                >
                  <svg
                    className="w-16 h-16 text-black-alpha-48"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
            <p className="text-body-small text-black-alpha-48">
              {nodeType.includes("transform")
                ? "Transform data using JavaScript"
                : nodeType.includes("state")
                  ? "Set workflow state variables"
                  : "Configure data operation"}
            </p>
          </div>

          {/* Form Fields */}
          <div className="p-20 space-y-24">
            {/* Transform Node - Code Editor */}
            {nodeType.includes("transform") && (
              <>
                <div>
                  <h3 className="text-sm font-medium text-accent-black mb-12">
                    Transform Code (TypeScript)
                  </h3>
                  <p className="text-sm text-black-alpha-48 mb-16">
                    Write TypeScript code to transform data. Runs securely in E2B sandbox.
                  </p>

                  {/* Code Editor */}
                  <div className="mb-16">
                    <div className="flex items-center justify-between mb-8">
                      <label className="block text-sm text-accent-black">
                        TypeScript Code
                      </label>
                      <VariableReferencePicker
                        nodes={nodes}
                        currentNodeId={node?.id || ''}
                        onSelect={(varPath) => {
                          setTransformScript(prev => prev + `\n// Access: ${varPath}\n`);
                        }}
                      />
                    </div>
                    <textarea
                      value={transformScript}
                      onChange={(e) => setTransformScript(e.target.value)}
                      rows={20}
                      className="w-full px-12 py-10 bg-[#1e1e1e] text-[#d4d4d4] border border-border-faint rounded-8 text-sm font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
                      placeholder="// Transform the input data using TypeScript"
                      spellCheck={false}
                    />
                    <div className="mt-8 text-xs text-black-alpha-48 space-y-4">
                      <p>Available variables:</p>
                      <ul className="list-disc list-inside space-y-2 ml-8">
                        <li><code className="px-4 py-1 bg-background-base rounded text-heat-100 font-mono">input</code> - Current input data</li>
                        <li><code className="px-4 py-1 bg-background-base rounded text-heat-100 font-mono">lastOutput</code> - Output from previous node</li>
                        <li><code className="px-4 py-1 bg-background-base rounded text-heat-100 font-mono">state</code> - Workflow state with variables</li>
                      </ul>
                      <p className="mt-8">Your function should return an object with the transformed data.</p>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Set State Node - Separate from Transform */}
            {nodeType.includes("state") && !nodeType.includes("transform") && (
              <>
                <div>
                  <h3 className="text-sm font-medium text-accent-black mb-12">
                    Set global variables
                  </h3>
                  <p className="text-sm text-black-alpha-48 mb-16">
                    Assign values to workflow's state variables
                  </p>

                  {/* State Assignments */}
                  <div className="space-y-12">
                    <div className="p-12 bg-background-base rounded-10 border border-border-faint">
                      <div className="space-y-12">
                        {/* Variable Name */}
                        <div>
                          <label className="block text-sm text-accent-black mb-6">
                            Variable Name
                          </label>
                          <input
                            type="text"
                            value={stateKey}
                            onChange={(e) => setStateKey(e.target.value)}
                            placeholder="myVariable"
                            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black font-mono focus:outline-none focus:border-heat-100"
                          />
                          <p className="text-xs text-black-alpha-48 mt-4">
                            Access later with <code className="px-4 py-1 bg-background-base rounded text-heat-100 font-mono text-xs">{`{{state.${stateKey}}}`}</code>
                          </p>
                        </div>

                        {/* Value Type */}
                        <div>
                          <label className="block text-sm text-accent-black mb-6">
                            Value Type
                          </label>
                          <select
                            value={valueType}
                            onChange={(e) => setValueType(e.target.value as any)}
                            className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black focus:outline-none focus:border-heat-100 transition-colors appearance-none cursor-pointer"
                          >
                            <option value="string">String</option>
                            <option value="number">Number</option>
                            <option value="boolean">Boolean</option>
                            <option value="json">JSON Object</option>
                            <option value="expression">JavaScript Expression</option>
                          </select>
                        </div>

                        {/* Value Input */}
                        <div>
                          <div className="flex items-center justify-between mb-6">
                            <label className="block text-sm text-accent-black">
                              Value
                            </label>
                            <VariableReferencePicker
                              nodes={nodes}
                              currentNodeId={node?.id || ''}
                              onSelect={(varPath) => setStateValue(prev => prev + `{{${varPath}}}`)}
                            />
                          </div>
                          {renderValueInput()}
                          <p className="text-xs text-black-alpha-48 mt-4">
                            {valueType === 'string' && 'Use {{variables}} to reference other data'}
                            {valueType === 'number' && 'Can use {{lastOutput.price}} to reference numbers'}
                            {valueType === 'boolean' && 'true or false'}
                            {valueType === 'json' && 'Valid JSON object or array'}
                            {valueType === 'expression' && 'JavaScript expression like: input.x + lastOutput.y'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Add Assignment Button */}
                    <button
                      onClick={() => {
                        toast.info('Multiple state assignments coming soon!', {
                          description: 'Currently you can set one variable per node. Add another Set State node for more variables.'
                        });
                      }}
                      className="px-12 py-8 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-8 text-sm text-accent-black transition-colors flex items-center gap-6"
                    >
                      <svg
                        className="w-14 h-14"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 4v16m8-8H4"
                        />
                      </svg>
                      Add
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
