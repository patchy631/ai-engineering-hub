"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface OutputField {
  name: string;
  type: "string" | "number" | "boolean" | "object" | "array";
  description?: string;
}

interface OutputSchemaPanelProps {
  nodeId: string;
  currentSchema: OutputField[];
  onUpdate: (schema: OutputField[]) => void;
}

export default function OutputSchemaPanel({ nodeId, currentSchema, onUpdate }: OutputSchemaPanelProps) {
  const [schema, setSchema] = useState<OutputField[]>(currentSchema || []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onUpdate(schema);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [schema, onUpdate]);

  const addField = () => {
    setSchema([
      ...schema,
      {
        name: `field${schema.length + 1}`,
        type: "string",
      },
    ]);
  };

  const updateField = (index: number, updates: Partial<OutputField>) => {
    setSchema(
      schema.map((field, i) => (i === index ? { ...field, ...updates } : field))
    );
  };

  const removeField = (index: number) => {
    setSchema(schema.filter((_, i) => i !== index));
  };

  const generateTypeScriptInterface = () => {
    if (schema.length === 0) return 'interface Output {\n  // No fields defined\n}';

    const fields = schema.map(f => {
      const typeStr = f.type === 'array' ? 'any[]' : f.type;
      const desc = f.description ? `  // ${f.description}\n` : '';
      return `${desc}  ${f.name}: ${typeStr};`;
    }).join('\n');

    return `interface ${nodeId.replace(/-/g, '_')}_Output {\n${fields}\n}`;
  };

  return (
    <div className="space-y-16">
      <div className="flex items-center justify-between">
        <h3 className="text-label-small text-black-alpha-48">
          Output Schema
        </h3>
        <button
          onClick={addField}
          className="px-10 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-6 text-body-small text-accent-black transition-colors flex items-center gap-6"
        >
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Field
        </button>
      </div>

      {schema.length === 0 ? (
        <div className="p-16 bg-background-base rounded-8 border border-border-faint text-center">
          <p className="text-body-small text-black-alpha-48">
            Define the shape of this node's output
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {schema.map((field, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-12 bg-background-base rounded-8 border border-border-faint space-y-8"
            >
              <div className="flex items-start gap-8">
                <div className="flex-1 grid grid-cols-2 gap-8">
                  {/* Field Name */}
                  <input
                    type="text"
                    value={field.name}
                    onChange={(e) => updateField(index, { name: e.target.value })}
                    placeholder="fieldName"
                    className="px-10 py-6 bg-white border border-border-faint rounded-6 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                  />

                  {/* Field Type */}
                  <select
                    value={field.type}
                    onChange={(e) => updateField(index, { type: e.target.value as any })}
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
                  onClick={() => removeField(index)}
                  className="w-24 h-24 rounded-4 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                >
                  <svg className="w-12 h-12 text-black-alpha-48 group-hover:text-accent-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Field Description */}
              <input
                type="text"
                value={field.description || ''}
                onChange={(e) => updateField(index, { description: e.target.value })}
                placeholder="Field description (optional)"
                className="w-full px-10 py-6 bg-white border border-border-faint rounded-6 text-body-small text-black-alpha-48 focus:outline-none focus:border-heat-100 transition-colors"
              />
            </motion.div>
          ))}
        </div>
      )}

      {/* TypeScript Preview */}
      {schema.length > 0 && (
        <div>
          <label className="block text-label-small text-black-alpha-48 mb-8">
            TypeScript Interface
          </label>
          <div className="p-12 bg-gray-900 rounded-8 border border-border-faint">
            <pre className="text-body-small text-heat-100 font-mono whitespace-pre-wrap">
              {generateTypeScriptInterface()}
            </pre>
          </div>
          <p className="text-body-small text-black-alpha-48 mt-8">
            Access fields: <code className="font-mono text-heat-100">state.variables.{nodeId}.fieldName</code>
          </p>
        </div>
      )}
    </div>
  );
}
