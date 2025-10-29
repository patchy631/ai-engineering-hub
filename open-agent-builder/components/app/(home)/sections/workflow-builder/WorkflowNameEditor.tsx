"use client";

import { useState, useEffect, ReactNode } from "react";
import { Workflow } from "@/lib/workflow/types";

interface WorkflowNameEditorProps {
  workflow: Workflow | null;
  onUpdate: (updates: Partial<Workflow>) => void;
  renameTrigger?: number;
  rightAccessory?: ReactNode;
}

export default function WorkflowNameEditor({ workflow, onUpdate, renameTrigger = 0, rightAccessory }: WorkflowNameEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(workflow?.name || "New Workflow");

  useEffect(() => {
    if (workflow) {
      setName(workflow.name);
    }
  }, [workflow]);

  useEffect(() => {
    if (renameTrigger > 0) {
      setIsEditing(true);
    }
  }, [renameTrigger]);

  const handleSave = () => {
    if (name.trim()) {
      onUpdate({ name: name.trim() });
      setIsEditing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setName(workflow?.name || "New Workflow");
      setIsEditing(false);
    }
  };

  if (!workflow) return null;

  return (
    <div className="fixed top-20 left-240 z-[60]">
      <div className="flex items-center gap-12">
        {isEditing ? (
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            autoFocus
            className="px-16 py-8 bg-accent-white border border-heat-100 rounded-8 text-body-medium text-accent-black focus:outline-none shadow-lg min-w-200"
          />
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="px-16 py-8 bg-accent-white hover:bg-accent-white border border-border-faint hover:border-heat-100 rounded-8 text-body-medium text-accent-black transition-colors flex items-center gap-8"
          >
            <span>{name}</span>
            <svg className="w-14 h-14 text-black-alpha-48 group-hover:text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </button>
        )}
        {rightAccessory ? (
          <div className="flex items-center gap-8">
            {rightAccessory}
          </div>
        ) : null}
      </div>
    </div>
  );
}
