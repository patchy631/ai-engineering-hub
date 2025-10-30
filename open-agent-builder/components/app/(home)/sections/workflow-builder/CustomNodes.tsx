"use client";

import * as React from "react";
import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";
import type { ReactNode } from "react";

// Custom node component with handles for connections
export function CustomNode({ data, selected }: NodeProps) {
  const nodeType = data.nodeType;
  const isRunning = data.isRunning;
  const executionStatus = data.executionStatus;

  // Note node state - MUST be declared before any conditional returns
  // This ensures hooks are called in the same order every render
  const noteText = String((data as any).noteText || 'Double-click to edit note');
  const [isEditing, setIsEditing] = React.useState(false);
  const [editText, setEditText] = React.useState<string>(noteText);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  // Determine border and background based on state
  const getBorderStyle = () => {
    // Note nodes have no border
    if (nodeType === 'note') return 'none';
    if (isRunning) return '1px solid #FA5D19';
    if (executionStatus === 'completed') return '1px solid #9ca3af';
    if (executionStatus === 'failed') return '1px solid #eb3424';
    if (selected) return '1px solid #FA5D19';
    return '1px solid #e5e7eb';
  };

  const getBackgroundColor = () => {
    // Note nodes get yellow/gold background
    if (nodeType === 'note') return '#ca8a04';
    // All nodes have white background
    return 'white';
  };

  const getOutlineStyle = () => {
    if (isRunning) return '2px solid rgba(250, 93, 25, 0.32)';
    if (selected) return '2px solid rgba(24, 24, 27, 0.18)';
    return '2px solid transparent';
  };

  // Note nodes have different styling
  const isNoteNode = nodeType === 'note';

  // Determine text color based on background
  const getTextColor = () => {
    if (isNoteNode) return '#854d0e'; // Dark yellow text for note nodes
    if (nodeType === 'if-else' || nodeType === 'while') {
      return '#18181b'; // Dark text for orange background nodes
    }
    return '#18181b'; // Default dark text
  };

  // Update editText when noteText changes (for different notes)
  React.useEffect(() => {
    if (isNoteNode) {
      setEditText(noteText);
    }
  }, [noteText, isNoteNode]);

  // Note nodes are visual-only sticky notes with inline editing
  if (isNoteNode) {

    React.useEffect(() => {
      if (isEditing && textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.select();
      }
    }, [isEditing]);

    const handleSave = () => {
      setIsEditing(false);
      // Update the node data
      if ((data as any).onUpdate) {
        (data as any).onUpdate({ noteText: editText });
      }
    };

    return (
      <div
        className="relative"
        onDoubleClick={(e) => {
          e.stopPropagation();
          setIsEditing(true);
        }}
        style={{
          padding: '10px',
          fontSize: '11px',
          backgroundColor: '#fef9c3', // Light yellow
          border: selected ? '2px solid #eab308' : 'none',
          outline: selected ? '2px solid rgba(234, 179, 8, 0.2)' : 'none',
          outlineOffset: 0,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          transition: 'all 0.2s ease-out',
          borderRadius: '6px',
          minWidth: '140px',
          maxWidth: '200px',
          width: 'fit-content',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          color: '#854d0e',
          lineHeight: '1.4',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          cursor: isEditing ? 'text' : 'move',
        }}
      >
        {/* Sticky note "tape" effect */}
        <div
          style={{
            position: 'absolute',
            top: '-6px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '30px',
            height: '12px',
            backgroundColor: 'rgba(234, 179, 8, 0.3)',
            borderRadius: '2px',
          }}
        />

        {isEditing ? (
          <textarea
            ref={textareaRef}
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onBlur={handleSave}
            onKeyDown={(e) => {
              if (e.key === 'Escape') {
                setEditText(noteText);
                setIsEditing(false);
              }
              // Save on Ctrl/Cmd+Enter
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                handleSave();
              }
              // Don't propagate to prevent ReactFlow shortcuts
              e.stopPropagation();
            }}
            className="nodrag"
            style={{
              width: '100%',
              minHeight: '40px',
              padding: '0',
              border: 'none',
              outline: 'none',
              backgroundColor: 'transparent',
              fontSize: '11px',
              fontFamily: 'ui-sans-serif, system-ui, sans-serif',
              color: '#854d0e',
              lineHeight: '1.4',
              resize: 'vertical',
            }}
          />
        ) : (
          <div
            style={{
              minHeight: '20px',
              cursor: 'move',
            }}
          >
            {noteText || 'Double-click to edit note'}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className="relative"
      style={{
        padding: '10px 16px',
        fontSize: '13px',
        backgroundColor: getBackgroundColor(),
        border: getBorderStyle(),
        outline: getOutlineStyle(),
        outlineOffset: 0,
        boxShadow: 'none',
        transition: 'outline 0.2s ease-out, border 0.2s ease-out',
        borderRadius: '16px',
        minWidth: '140px',
        maxWidth: '240px',
        width: 'fit-content',
      }}
    >
      {/* Input handle (left) - all nodes except 'start' and 'note' */}
      {nodeType !== 'start' && nodeType !== 'note' && (
        <Handle
          type="target"
          position={Position.Left}
          id="input"
          style={{
            width: 10,
            height: 10,
            background: '#9ca3af',
            border: '2px solid white',
            left: -5,
            top: '50%',
            transform: 'translateY(-50%)',
          }}
        />
      )}

      {/* Render the label (icon + text) */}
      <div style={{ whiteSpace: 'nowrap', color: getTextColor() }}>
        {data.label as ReactNode}
      </div>

      {/* Output handles - special cases for branching nodes */}
      {nodeType === 'if-else' ? (
        <>
          {/* If branch (left bottom) */}
          <Handle
            type="source"
            position={Position.Right}
            id="if"
            style={{
              width: 10,
              height: 10,
              background: '#FA5D19',
              border: '2px solid white',
              right: -5,
              top: '35%',
              transform: 'translateY(-50%)',
            }}
          />
          {/* Else branch (right bottom) */}
          <Handle
            type="source"
            position={Position.Right}
            id="else"
            style={{
              width: 10,
              height: 10,
              background: '#18181b',
              border: '2px solid white',
              right: -5,
              top: '65%',
              transform: 'translateY(-50%)',
            }}
          />
          {/* Branch labels */}
          <div style={{
            position: 'absolute',
            top: '35%',
            right: -50,
            transform: 'translateY(-50%)',
            fontSize: '10px',
            color: '#FA5D19',
            fontWeight: 600,
          }}>If</div>
          <div style={{
            position: 'absolute',
            top: '65%',
            right: -55,
            transform: 'translateY(-50%)',
            fontSize: '10px',
            color: '#18181b',
            fontWeight: 600,
          }}>Else</div>
        </>
      ) : nodeType === 'user-approval' ? (
        <>
          {/* Approve branch (left bottom) */}
          <Handle
            type="source"
            position={Position.Right}
            id="approve"
            style={{
              width: 10,
              height: 10,
              background: '#10b981',
              border: '2px solid white',
              right: -5,
              top: '35%',
              transform: 'translateY(-50%)',
            }}
          />
          {/* Reject branch (right bottom) */}
          <Handle
            type="source"
            position={Position.Right}
            id="reject"
            style={{
              width: 10,
              height: 10,
              background: '#ef4444',
              border: '2px solid white',
              right: -5,
              top: '65%',
              transform: 'translateY(-50%)',
            }}
          />
          {/* Branch labels */}
          <div style={{
            position: 'absolute',
            top: '35%',
            right: -70,
            transform: 'translateY(-50%)',
            fontSize: '10px',
            color: '#10b981',
            fontWeight: 600,
          }}>Approve</div>
          <div style={{
            position: 'absolute',
            top: '65%',
            right: -60,
            transform: 'translateY(-50%)',
            fontSize: '10px',
            color: '#ef4444',
            fontWeight: 600,
          }}>Reject</div>
        </>
      ) : nodeType === 'while' ? (
        <>
          {/* Continue branch (top) */}
          <Handle
            type="source"
            position={Position.Right}
            id="continue"
            style={{
              width: 10,
              height: 10,
              background: '#FA5D19',
              border: '2px solid white',
              right: -5,
              top: '35%',
              transform: 'translateY(-50%)',
            }}
          />
          {/* Break branch (bottom) */}
          <Handle
            type="source"
            position={Position.Right}
            id="break"
            style={{
              width: 10,
              height: 10,
              background: '#18181b',
              border: '2px solid white',
              right: -5,
              top: '65%',
              transform: 'translateY(-50%)',
            }}
          />
          {/* Branch labels */}
          <div style={{
            position: 'absolute',
            top: '35%',
            right: -70,
            transform: 'translateY(-50%)',
            fontSize: '10px',
            color: '#FA5D19',
            fontWeight: 600,
          }}>Continue</div>
          <div style={{
            position: 'absolute',
            top: '65%',
            right: -55,
            transform: 'translateY(-50%)',
            fontSize: '10px',
            color: '#18181b',
            fontWeight: 600,
          }}>Break</div>
        </>
      ) : nodeType !== 'end' && nodeType !== 'note' ? (
        <Handle
          type="source"
          position={Position.Right}
          id="output"
          style={{
            width: 10,
            height: 10,
            background: '#9ca3af',
            border: '2px solid white',
            right: -5,
            top: '50%',
            transform: 'translateY(-50%)',
          }}
        />
      ) : null}
    </div>
  );
}

// Create all node types by reusing the same component
export const nodeTypes = {
  start: CustomNode,
  agent: CustomNode,
  mcp: CustomNode,
  extract: CustomNode,
  end: CustomNode,
  note: CustomNode,
  logic: CustomNode,
  data: CustomNode,
  http: CustomNode,
  transform: CustomNode,
  'if-else': CustomNode,
  'while': CustomNode,
  'user-approval': CustomNode,
  'set-state': CustomNode,
};
