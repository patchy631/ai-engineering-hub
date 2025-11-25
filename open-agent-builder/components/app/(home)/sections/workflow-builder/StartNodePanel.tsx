"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import type { Node } from "@xyflow/react";

interface InputVariable {
  name: string;
  type: "string" | "number" | "boolean" | "url" | "object";
  required: boolean;
  defaultValue?: string;
  description?: string;
}

interface StartNodePanelProps {
  node: Node | null;
  onClose: () => void;
  onUpdate: (nodeId: string, data: any) => void;
}

export default function StartNodePanel({ node, onClose, onUpdate }: StartNodePanelProps) {
  const nodeData = node?.data as any;
  const [inputVariables, setInputVariables] = useState<InputVariable[]>(
    nodeData?.inputVariables || [
      {
        name: "input_as_text",
        type: "string",
        required: false,
        defaultValue: "",
        description: "",
      }
    ]
  );

  // Auto-save changes
  useEffect(() => {
    if (!node) return;

    const timeoutId = setTimeout(() => {
      onUpdate(node.id, {
        inputVariables,
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [inputVariables, node, onUpdate]);

  const addVariable = () => {
    setInputVariables([
      ...inputVariables,
      {
        name: `input${inputVariables.length + 1}`,
        type: "string",
        required: false,
        description: "",
      },
    ]);
  };

  const updateVariable = (index: number, updates: Partial<InputVariable>) => {
    setInputVariables(
      inputVariables.map((v, i) => (i === index ? { ...v, ...updates } : v))
    );
  };

  const removeVariable = (index: number) => {
    setInputVariables(inputVariables.filter((_, i) => i !== index));
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
              <h2 className="text-xl font-semibold text-accent-black">Start</h2>
              <button
                onClick={onClose}
                className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
              >
                <svg className="w-18 h-18 text-black-alpha-48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-black-alpha-48">
              Define the workflow inputs
            </p>
          </div>

          {/* Content */}
          <div className="p-20 space-y-20">
            {/* Input Variables List */}
            <div>
              <div className="flex items-center justify-between mb-12">
                <h3 className="text-sm font-medium text-accent-black">
                  Input variables
                </h3>
                <button
                  onClick={addVariable}
                  className="px-12 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-8 text-xs text-accent-black transition-colors flex items-center gap-6"
                >
                  <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add Variable
                </button>
              </div>
              <div className="space-y-12">
                {inputVariables.length === 0 ? (
                  <div className="p-20 bg-accent-white border border-border-faint border-dashed rounded-12 text-center">
                    <svg className="w-32 h-32 mx-auto mb-12 text-black-alpha-32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-sm text-black-alpha-48 mb-12">No input variables defined</p>
                    <button
                      onClick={addVariable}
                      className="px-16 py-8 bg-accent-black hover:bg-black-alpha-88 text-white rounded-8 text-sm font-medium transition-colors"
                    >
                      Add First Variable
                    </button>
                  </div>
                ) : (
                  inputVariables.map((variable, index) => (
                    <div key={index} className="p-16 bg-background-base rounded-12 border border-border-faint">
                      <div className="space-y-12">
                      {/* Name */}
                      <div>
                        <label className="block text-xs text-black-alpha-48 mb-6">Variable Name</label>
                        <input
                          type="text"
                          value={variable.name}
                          onChange={(e) => updateVariable(index, { name: e.target.value })}
                          className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black font-mono focus:outline-none focus:border-heat-100"
                          placeholder="variable_name"
                        />
                      </div>

                      {/* Type */}
                      <div>
                        <label className="block text-xs text-black-alpha-48 mb-6">Type</label>
                        <select
                          value={variable.type}
                          onChange={(e) => updateVariable(index, { type: e.target.value as any })}
                          className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black focus:outline-none focus:border-heat-100"
                        >
                          <option value="string">String</option>
                          <option value="number">Number</option>
                          <option value="boolean">Boolean</option>
                          <option value="url">URL</option>
                          <option value="object">Object</option>
                        </select>
                      </div>

                      {/* Description */}
                      <div>
                        <label className="block text-xs text-black-alpha-48 mb-6">Description</label>
                        <input
                          type="text"
                          value={variable.description || ''}
                          onChange={(e) => updateVariable(index, { description: e.target.value })}
                          className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black focus:outline-none focus:border-heat-100"
                          placeholder="Describe this input..."
                        />
                      </div>

                      {/* Default Value */}
                      <div>
                        <label className="block text-xs text-black-alpha-48 mb-6">Default Value</label>
                        <input
                          type="text"
                          value={variable.defaultValue || ''}
                          onChange={(e) => updateVariable(index, { defaultValue: e.target.value })}
                          className="w-full px-12 py-8 bg-accent-white border border-border-faint rounded-8 text-sm text-accent-black focus:outline-none focus:border-heat-100"
                          placeholder="Default value..."
                        />
                      </div>

                      {/* Required Toggle & Delete */}
                      <div className="flex items-center justify-between pt-8">
                        <label className="flex items-center gap-8 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={variable.required}
                            onChange={(e) => updateVariable(index, { required: e.target.checked })}
                            className="w-16 h-16 rounded-4 border border-border-faint text-heat-100 focus:ring-heat-100"
                          />
                          <span className="text-xs text-accent-black">Required</span>
                        </label>
                        <button
                          onClick={() => removeVariable(index)}
                          className="px-12 py-6 text-xs text-accent-black hover:bg-black-alpha-4 rounded-6 transition-colors flex items-center gap-6"
                        >
                          <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          Remove
                        </button>
                      </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Help Text */}
            <div className="p-16 bg-heat-4 border border-heat-100 rounded-12">
              <h4 className="text-sm font-medium text-accent-black mb-8">Input Variables</h4>
              <p className="text-xs text-heat-100 leading-relaxed">
                Input variables define the data your workflow accepts when it starts.
                These will be shown as form fields when running the workflow.
              </p>
              <p className="text-xs text-heat-100 leading-relaxed mt-8">
                Use <code className="px-4 py-2 bg-heat-8 rounded text-accent-black">{`{{variable_name}}`}</code> in any node to reference these values.
              </p>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
