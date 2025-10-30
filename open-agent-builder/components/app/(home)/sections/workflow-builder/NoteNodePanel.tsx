"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import type { Node } from "@xyflow/react";

interface NoteNodePanelProps {
  node: Node | null;
  onClose: () => void;
  onDelete: (nodeId: string) => void;
  onUpdate: (nodeId: string, data: any) => void;
}

export default function NoteNodePanel({ node, onClose, onDelete, onUpdate }: NoteNodePanelProps) {
  const nodeData = node?.data as any;
  const [noteText, setNoteText] = useState(nodeData?.noteText || "Add your notes here...");

  // Auto-save changes
  useEffect(() => {
    if (!node?.id) return;

    const timeoutId = setTimeout(() => {
      onUpdate(node.id, {
        noteText,
        nodeName: noteText.slice(0, 30) + (noteText.length > 30 ? '...' : ''), // Update node label
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [noteText]);


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
          <div className="p-20 border-b border-border-faint bg-heat-4">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-8">
                <svg className="w-20 h-20 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                <h2 className="text-title-h3 text-accent-black">Sticky Note</h2>
              </div>
              <div className="flex items-center gap-8">
                <button
                  onClick={() => onDelete(node?.id || '')}
                  className="w-32 h-32 rounded-6 hover:bg-heat-8 transition-colors flex items-center justify-center group"
                  title="Delete note"
                >
                  <svg className="w-16 h-16 text-heat-100 group-hover:text-accent-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
                <button
                  onClick={onClose}
                  className="w-32 h-32 rounded-6 hover:bg-heat-8 transition-colors flex items-center justify-center"
                >
                  <svg className="w-16 h-16 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <p className="text-body-small text-heat-100">
              Visual-only sticky note for documentation
            </p>
          </div>

          {/* Form Fields */}
          <div className="p-20">
            {/* Sticky Note */}
            <div>
              <label className="block text-sm font-medium text-accent-black mb-8 flex items-center gap-8">
                <svg className="w-16 h-16 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Note Content
              </label>
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                rows={10}
                placeholder="Add documentation, comments, or reminders..."
                className="w-full px-14 py-10 bg-heat-4 border border-heat-100 rounded-10 text-sm text-accent-black placeholder-black-alpha-48 placeholder:opacity-50 focus:outline-none focus:border-heat-100 transition-colors resize-y font-sans"
                style={{ minHeight: '200px' }}
              />
              <div className="mt-12 p-12 bg-heat-4 border border-heat-100 rounded-8">
                <p className="text-xs text-heat-100 leading-relaxed">
                  <strong>Sticky notes are visual-only.</strong> They don't execute or connect to other nodes.
                  Use them to document your workflow, explain logic, or leave reminders.
                </p>
              </div>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
