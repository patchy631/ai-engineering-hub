"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface Argument {
  name: string;
  type: "string" | "number" | "boolean" | "object" | "array";
  required: boolean;
  defaultValue?: string;
  reference?: string; // e.g., "state.variables.node_1.price"
}

interface NodeArgumentsPanelProps {
  nodeId: string;
  currentArgs: Argument[];
  onUpdate: (args: Argument[]) => void;
}

export default function NodeArgumentsPanel({ nodeId, currentArgs, onUpdate }: NodeArgumentsPanelProps) {
  const [arguments_, setArguments] = useState<Argument[]>(currentArgs || []);
  const [showAddArg, setShowAddArg] = useState(false);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onUpdate(arguments_);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [arguments_, onUpdate]);

  const addArgument = () => {
    setArguments([
      ...arguments_,
      {
        name: `arg${arguments_.length + 1}`,
        type: "string",
        required: false,
      },
    ]);
    setShowAddArg(false);
  };

  const updateArgument = (index: number, updates: Partial<Argument>) => {
    setArguments(
      arguments_.map((arg, i) => (i === index ? { ...arg, ...updates } : arg))
    );
  };

  const removeArgument = (index: number) => {
    setArguments(arguments_.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-16">
      <div className="flex items-center justify-between">
        <h3 className="text-label-small text-black-alpha-48">
          Arguments
        </h3>
        <button
          onClick={() => setShowAddArg(true)}
          className="px-10 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-6 text-body-small text-accent-black transition-colors flex items-center gap-6"
        >
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Argument
        </button>
      </div>

      {arguments_.length === 0 ? (
        <div className="p-16 bg-background-base rounded-8 border border-border-faint text-center">
          <p className="text-body-small text-black-alpha-48">
            No arguments defined. Click "Add Argument" to get started.
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {arguments_.map((arg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-12 bg-background-base rounded-8 border border-border-faint"
            >
              <div className="flex items-start gap-8 mb-12">
                <div className="flex-1 grid grid-cols-2 gap-8">
                  {/* Argument Name */}
                  <input
                    type="text"
                    value={arg.name}
                    onChange={(e) => updateArgument(index, { name: e.target.value })}
                    placeholder="argumentName"
                    className="px-10 py-6 bg-white border border-border-faint rounded-6 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                  />

                  {/* Argument Type */}
                  <select
                    value={arg.type}
                    onChange={(e) => updateArgument(index, { type: e.target.value as any })}
                    className="px-10 py-6 bg-white border border-border-faint rounded-6 text-body-small text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  >
                    <option value="string">String</option>
                    <option value="number">Number</option>
                    <option value="boolean">Boolean</option>
                    <option value="object">Object</option>
                    <option value="array">Array</option>
                  </select>
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => removeArgument(index)}
                  className="w-24 h-24 rounded-4 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                >
                  <svg className="w-12 h-12 text-black-alpha-48 group-hover:text-accent-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Value Source */}
              <div className="space-y-8">
                <label className="block text-body-small text-black-alpha-48">
                  Value Source (Optional)
                </label>
                <input
                  type="text"
                  value={arg.reference || ''}
                  onChange={(e) => updateArgument(index, { reference: e.target.value })}
                  placeholder="state.variables.node_1.price or 'default value'"
                  className="w-full px-10 py-6 bg-white border border-border-faint rounded-6 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                />
                <p className="text-body-small text-black-alpha-32">
                  Reference previous node output or set a default value
                </p>
              </div>

              {/* Required Toggle */}
              <div className="flex items-center justify-between mt-12 pt-12 border-t border-border-faint">
                <span className="text-body-small text-black-alpha-48">Required</span>
                <button
                  onClick={() => updateArgument(index, { required: !arg.required })}
                  className={`w-36 h-20 rounded-full transition-colors relative ${
                    arg.required ? 'bg-heat-100' : 'bg-black-alpha-12'
                  }`}
                >
                  <motion.div
                    className="w-16 h-16 bg-white rounded-full absolute top-2 shadow-sm"
                    animate={{ left: arg.required ? '18px' : '2px' }}
                    transition={{ duration: 0.2 }}
                  />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {showAddArg && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-12 bg-heat-4 rounded-8 border border-heat-100"
        >
          <p className="text-body-small text-accent-black mb-12">
            Add a new argument to define what this node receives
          </p>
          <button
            onClick={addArgument}
            className="w-full px-12 py-8 bg-heat-100 hover:bg-heat-200 text-white rounded-6 text-body-small font-medium transition-colors"
          >
            Create Argument
          </button>
        </motion.div>
      )}

      {/* Quick Reference Guide */}
      <details className="group">
        <summary className="cursor-pointer list-none p-12 bg-heat-4 rounded-8 border border-heat-100 text-body-small text-accent-black hover:bg-heat-8 transition-colors">
          📖 Variable Reference Guide
        </summary>
        <div className="mt-8 p-12 bg-heat-4 rounded-8 border border-heat-100 space-y-6 text-body-small text-accent-black font-mono">
          <div>
            <strong>Workflow Input:</strong>
            <code className="block mt-4 text-heat-100">state.variables.input</code>
          </div>
          <div>
            <strong>Previous Node Output:</strong>
            <code className="block mt-4 text-heat-100">state.variables.lastOutput</code>
          </div>
          <div>
            <strong>Specific Node Output:</strong>
            <code className="block mt-4 text-heat-100">state.variables.node_1.price</code>
            <code className="block mt-2 text-heat-100">state.variables.agent_extract.data</code>
          </div>
          <div>
            <strong>Custom Variables:</strong>
            <code className="block mt-4 text-heat-100">state.variables.myCustomVar</code>
          </div>
        </div>
      </details>
    </div>
  );
}
