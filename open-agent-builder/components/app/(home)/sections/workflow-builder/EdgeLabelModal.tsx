"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import type { Edge } from "@xyflow/react";

interface EdgeLabelModalProps {
  edge: Edge | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (edgeId: string, label: string) => void;
}

export default function EdgeLabelModal({ edge, isOpen, onClose, onSave }: EdgeLabelModalProps) {
  const [label, setLabel] = useState(edge?.label as string || '');
  const [labelType, setLabelType] = useState<'custom' | 'true' | 'false' | 'none'>(
    edge?.label === 'true' ? 'true' :
    edge?.label === 'false' ? 'false' :
    edge?.label ? 'custom' : 'none'
  );

  const handleSave = () => {
    if (!edge) return;

    let finalLabel = '';
    if (labelType === 'true') finalLabel = 'true';
    else if (labelType === 'false') finalLabel = 'false';
    else if (labelType === 'custom') finalLabel = label;

    onSave(edge.id, finalLabel);
    onClose();
  };

  if (!edge) return null;

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
            className="bg-accent-white rounded-16 shadow-2xl max-w-400 w-full"
          >
            {/* Header */}
            <div className="p-20 border-b border-border-faint">
              <h2 className="text-title-h4 text-accent-black">Edit Connection</h2>
              <p className="text-body-small text-black-alpha-48 mt-4">
                Add a label to this connection
              </p>
            </div>

            {/* Content */}
            <div className="p-20 space-y-16">
              {/* Label Type */}
              <div>
                <label className="block text-label-small text-black-alpha-48 mb-8">
                  Label Type
                </label>
                <div className="space-y-8">
                  <button
                    onClick={() => setLabelType('none')}
                    className={`w-full p-12 rounded-8 border-2 transition-all text-left ${
                      labelType === 'none'
                        ? 'border-heat-100 bg-heat-4'
                        : 'border-border-faint bg-background-base hover:border-border-light'
                    }`}
                  >
                    <p className="text-body-small text-accent-black font-medium">No Label</p>
                    <p className="text-body-small text-black-alpha-48 mt-4">Standard connection</p>
                  </button>

                  <button
                    onClick={() => setLabelType('true')}
                    className={`w-full p-12 rounded-8 border-2 transition-all text-left ${
                      labelType === 'true'
                        ? 'border-heat-100 bg-heat-4'
                        : 'border-border-faint bg-background-base hover:border-border-light'
                    }`}
                  >
                    <p className="text-body-small text-accent-black font-medium">True Branch</p>
                    <p className="text-body-small text-black-alpha-48 mt-4">For If/Else true condition</p>
                  </button>

                  <button
                    onClick={() => setLabelType('false')}
                    className={`w-full p-12 rounded-8 border-2 transition-all text-left ${
                      labelType === 'false'
                        ? 'border-heat-100 bg-heat-4'
                        : 'border-border-faint bg-background-base hover:border-border-light'
                    }`}
                  >
                    <p className="text-body-small text-accent-black font-medium">False Branch</p>
                    <p className="text-body-small text-black-alpha-48 mt-4">For If/Else false condition</p>
                  </button>

                  <button
                    onClick={() => setLabelType('custom')}
                    className={`w-full p-12 rounded-8 border-2 transition-all text-left ${
                      labelType === 'custom'
                        ? 'border-heat-100 bg-heat-4'
                        : 'border-border-faint bg-background-base hover:border-border-light'
                    }`}
                  >
                    <p className="text-body-small text-accent-black font-medium">Custom Label</p>
                    <p className="text-body-small text-black-alpha-48 mt-4">Your own text</p>
                  </button>
                </div>
              </div>

              {/* Custom Label Input */}
              {labelType === 'custom' && (
                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Label Text
                  </label>
                  <input
                    type="text"
                    value={label}
                    onChange={(e) => setLabel(e.target.value)}
                    placeholder="Enter label text"
                    className="w-full px-12 py-8 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  />
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-20 border-t border-border-faint flex items-center justify-end gap-12">
              <button
                onClick={onClose}
                className="px-20 py-10 text-body-medium text-black-alpha-48 hover:text-accent-black transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-24 py-10 bg-heat-100 hover:bg-heat-200 text-white rounded-8 transition-all active:scale-[0.98] text-body-medium font-medium"
              >
                Save
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
