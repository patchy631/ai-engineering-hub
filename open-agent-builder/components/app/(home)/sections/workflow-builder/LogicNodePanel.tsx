"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import type { Node } from "@xyflow/react";

interface LogicNodePanelProps {
  node: Node | null;
  nodes: Node[];
  onClose: () => void;
  onDelete: (nodeId: string) => void;
  onUpdate: (nodeId: string, data: any) => void;
}

export default function LogicNodePanel({ node, nodes, onClose, onDelete, onUpdate }: LogicNodePanelProps) {
  const nodeData = node?.data as any;
  const nodeType = nodeData?.nodeType?.toLowerCase() || '';
  const [name, setName] = useState(nodeData?.name || nodeData?.nodeName || "Logic");
  const conditionTextareaRef = useRef<HTMLTextAreaElement>(null);
  const whileConditionTextareaRef = useRef<HTMLTextAreaElement>(null);
  const approvalMessageTextareaRef = useRef<HTMLTextAreaElement>(null);

  // If/Else state
  const [condition, setCondition] = useState(nodeData?.condition || "input.score > 70");

  // While state
  const [whileCondition, setWhileCondition] = useState(nodeData?.whileCondition || "iteration < 10");
  const [maxIterations, setMaxIterations] = useState(nodeData?.maxIterations || "100");

  // User Approval state
  const [approvalMessage, setApprovalMessage] = useState(nodeData?.approvalMessage || "Please review and approve this step");
  const [timeoutMinutes, setTimeoutMinutes] = useState(nodeData?.timeoutMinutes || "30");

  // Build available variables for conditions
  const getAvailableVariables = () => {
    const startNode = nodes.find(n => (n.data as any)?.nodeType === 'start');
    const inputVariables = (startNode?.data as any)?.inputVariables || [];

    const previousNodes = nodes.filter(n => n.id !== node?.id && (n.data as any)?.nodeType !== 'note' && (n.data as any)?.nodeType !== 'start');

    return {
      inputVars: inputVariables.map((v: any) => ({
        name: v.name,
        path: `input.${v.name}`,
        description: v.description,
        type: v.type,
      })),
      nodeOutputs: previousNodes.map(n => ({
        name: (n.data as any)?.nodeName || n.id,
        path: n.id.replace(/-/g, '_'),
        description: `Output from ${(n.data as any)?.nodeName || n.id}`,
      })),
      special: [
        { name: 'lastOutput', path: 'lastOutput', description: 'Output from previous node' },
        { name: 'iteration', path: 'iteration', description: 'Current iteration count (while loops only)' },
      ]
    };
  };

  const insertVariable = (varPath: string, targetType: 'ifElse' | 'while' | 'approval') => {
    let textarea: HTMLTextAreaElement | null = null;
    let currentValue = '';
    let setter: (value: string) => void;

    switch (targetType) {
      case 'ifElse':
        textarea = conditionTextareaRef.current;
        currentValue = condition;
        setter = setCondition;
        break;
      case 'while':
        textarea = whileConditionTextareaRef.current;
        currentValue = whileCondition;
        setter = setWhileCondition;
        break;
      case 'approval':
        textarea = approvalMessageTextareaRef.current;
        currentValue = approvalMessage;
        setter = setApprovalMessage;
        break;
    }

    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newValue = currentValue.substring(0, start) + varPath + currentValue.substring(end);

    setter(newValue);

    // Restore cursor position
    setTimeout(() => {
      textarea!.focus();
      textarea!.setSelectionRange(start + varPath.length, start + varPath.length);
    }, 0);
  };

  // Auto-save changes
  useEffect(() => {
    if (!node?.id) return;

    const timeoutId = setTimeout(() => {
      onUpdate(node.id, {
        name,
        nodeName: name,
        condition,
        whileCondition,
        maxIterations,
        approvalMessage,
        timeoutMinutes,
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [name, condition, whileCondition, maxIterations, approvalMessage, timeoutMinutes]);

  const availableVars = getAvailableVariables();

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
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="text-label-large text-accent-black font-medium bg-transparent border-none outline-none focus:outline-none hover:bg-black-alpha-4 px-2 -ml-2 rounded-4 transition-colors"
                placeholder="Enter node name..."
              />
              <div className="flex items-center gap-8">
                <button
                  onClick={() => onDelete(node?.id || '')}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                  title="Delete node"
                >
                  <svg className="w-16 h-16 text-black-alpha-48 group-hover:text-black-alpha-64" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
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
            <p className="text-sm text-black-alpha-48">
              {nodeType.includes('if') ? 'Create conditions to branch your workflow' :
               nodeType.includes('while') ? 'Loop while a condition is true' :
               nodeType.includes('approval') ? 'Pause for a human to approve or reject a step' :
               'Configure logic flow'}
            </p>
          </div>

          {/* Form Fields */}
          <div className="p-16 space-y-16">
            {/* If/Else Configuration */}
            {nodeType.includes('if') && (
              <>
                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Condition
                  </label>
                  <textarea
                    ref={conditionTextareaRef}
                    value={condition}
                    onChange={(e) => setCondition(e.target.value)}
                    rows={3}
                    placeholder="e.g., input.score > 70"
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-8">
                    JavaScript expression that returns true/false
                  </p>
                </div>

                {/* Quick Variable Selector */}
                <div className="p-16 bg-heat-4 rounded-12 border border-heat-100">
                  <h3 className="text-label-small text-accent-black mb-12 flex items-center gap-6">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                    Click to Insert Variable
                  </h3>

                  {/* Input Variables */}
                  {availableVars.inputVars.length > 0 && (
                    <div className="mb-12">
                      <p className="text-xs text-heat-100 font-medium mb-6">Input Variables:</p>
                      <div className="flex flex-wrap gap-6">
                        {availableVars.inputVars.map((v: any, idx: number) => (
                          <button
                            key={idx}
                            onClick={() => insertVariable(v.path, 'ifElse')}
                            className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                            title={v.description}
                          >
                            {v.path}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Previous Node Outputs */}
                  {availableVars.nodeOutputs.length > 0 && (
                    <div className="mb-12">
                      <p className="text-xs text-heat-100 font-medium mb-6">Previous Nodes:</p>
                      <div className="flex flex-wrap gap-6">
                        {availableVars.nodeOutputs.map((v: any, idx: number) => (
                          <button
                            key={idx}
                            onClick={() => insertVariable(v.path, 'ifElse')}
                            className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                            title={v.description}
                          >
                            {v.path}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Special Variables */}
                  <div>
                    <p className="text-xs text-heat-100 font-medium mb-6">Special:</p>
                    <div className="flex flex-wrap gap-6">
                      {availableVars.special.filter(v => v.name !== 'iteration').map((v: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => insertVariable(v.path, 'ifElse')}
                          className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                          title={v.description}
                        >
                          {v.path}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Common Condition Examples */}
                <div className="p-16 bg-background-base rounded-12 border border-border-faint">
                  <h3 className="text-label-small text-accent-black mb-12">Common Patterns:</h3>
                  <div className="grid grid-cols-2 gap-8">
                    <button
                      onClick={() => setCondition('input.score > 70')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">input.score &gt; 70</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Number check</p>
                    </button>
                    <button
                      onClick={() => setCondition('input.status === "approved"')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">input.status === "approved"</p>
                      <p className="text-xs text-black-alpha-48 mt-2">String equals</p>
                    </button>
                    <button
                      onClick={() => setCondition('lastOutput && lastOutput.length > 0')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">lastOutput.length &gt; 0</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Array not empty</p>
                    </button>
                    <button
                      onClick={() => setCondition('lastOutput.data && lastOutput.data.price')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">lastOutput.data.price</p>
                      <p className="text-xs text-black-alpha-48 mt-2">JSON nested</p>
                    </button>
                    <button
                      onClick={() => setCondition('input.age >= 18 && input.age <= 65')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">age &gt;= 18 && age &lt;= 65</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Range check</p>
                    </button>
                    <button
                      onClick={() => setCondition('lastOutput.tags && lastOutput.tags.includes("urgent")')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">tags.includes("urgent")</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Array contains</p>
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* While Configuration */}
            {nodeType.includes('while') && (
              <>
                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Loop Condition
                  </label>
                  <textarea
                    ref={whileConditionTextareaRef}
                    value={whileCondition}
                    onChange={(e) => setWhileCondition(e.target.value)}
                    rows={3}
                    placeholder="e.g., iteration < 10"
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-8">
                    JavaScript expression that returns true/false
                  </p>
                </div>

                {/* Quick Variable Selector */}
                <div className="p-16 bg-heat-4 rounded-12 border border-heat-100">
                  <h3 className="text-label-small text-accent-black mb-12 flex items-center gap-6">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                    Click to Insert Variable
                  </h3>

                  {/* Input Variables */}
                  {availableVars.inputVars.length > 0 && (
                    <div className="mb-12">
                      <p className="text-xs text-heat-100 font-medium mb-6">Input Variables:</p>
                      <div className="flex flex-wrap gap-6">
                        {availableVars.inputVars.map((v: any, idx: number) => (
                          <button
                            key={idx}
                            onClick={() => insertVariable(v.path, 'while')}
                            className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                            title={v.description}
                          >
                            {v.path}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Previous Node Outputs */}
                  {availableVars.nodeOutputs.length > 0 && (
                    <div className="mb-12">
                      <p className="text-xs text-heat-100 font-medium mb-6">Previous Nodes:</p>
                      <div className="flex flex-wrap gap-6">
                        {availableVars.nodeOutputs.map((v: any, idx: number) => (
                          <button
                            key={idx}
                            onClick={() => insertVariable(v.path, 'while')}
                            className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                            title={v.description}
                          >
                            {v.path}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Special Variables */}
                  <div>
                    <p className="text-xs text-heat-100 font-medium mb-6">Special:</p>
                    <div className="flex flex-wrap gap-6">
                      {availableVars.special.map((v: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => insertVariable(v.path, 'while')}
                          className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                          title={v.description}
                        >
                          {v.path}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Common Loop Examples */}
                <div className="p-16 bg-background-base rounded-12 border border-border-faint">
                  <h3 className="text-label-small text-accent-black mb-12">Common Patterns:</h3>
                  <div className="grid grid-cols-2 gap-8">
                    <button
                      onClick={() => setWhileCondition('iteration < 10')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">iteration &lt; 10</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Fixed iterations</p>
                    </button>
                    <button
                      onClick={() => setWhileCondition('iteration < lastOutput.totalCount')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">iteration &lt; totalCount</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Array processing</p>
                    </button>
                    <button
                      onClick={() => setWhileCondition('lastOutput.hasMore === true')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">lastOutput.hasMore</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Has more pages</p>
                    </button>
                    <button
                      onClick={() => setWhileCondition('lastOutput.score < 90 && iteration < 5')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">score &lt; 90 (max 5)</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Retry until good</p>
                    </button>
                    <button
                      onClick={() => setWhileCondition('lastOutput.queue && lastOutput.queue.length > 0')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">queue.length &gt; 0</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Process queue</p>
                    </button>
                    <button
                      onClick={() => setWhileCondition('lastOutput.data.items[iteration]')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">data.items[iteration]</p>
                      <p className="text-xs text-black-alpha-48 mt-2">JSON array access</p>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Max Iterations
                  </label>
                  <input
                    type="number"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(e.target.value)}
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-8">
                    Safety limit to prevent infinite loops
                  </p>
                </div>

                <div className="p-16 bg-heat-4 rounded-12 border border-heat-100">
                  <p className="text-body-small text-accent-black">
                    <strong>Loop Setup:</strong> Connect loop body nodes using the "continue" handle. The workflow will repeat until the condition is false or max iterations reached.
                  </p>
                </div>
              </>
            )}

            {/* User Approval Configuration */}
            {nodeType.includes('approval') && (
              <>
                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Approval Message
                  </label>
                  <textarea
                    ref={approvalMessageTextareaRef}
                    value={approvalMessage}
                    onChange={(e) => setApprovalMessage(e.target.value)}
                    rows={4}
                    placeholder="e.g., Please review and approve: ${lastOutput.summary}"
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors resize-none"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-8">
                    Use ${'{variableName}'} to insert dynamic values from your workflow
                  </p>
                </div>

                {/* Quick Variable Selector for Approval Message */}
                <div className="p-16 bg-heat-4 rounded-12 border border-heat-100">
                  <h3 className="text-label-small text-accent-black mb-12 flex items-center gap-6">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                    Click to Insert Variable
                  </h3>

                  {/* Input Variables */}
                  {availableVars.inputVars.length > 0 && (
                    <div className="mb-12">
                      <p className="text-xs text-heat-100 font-medium mb-6">Input Variables:</p>
                      <div className="flex flex-wrap gap-6">
                        {availableVars.inputVars.map((v: any, idx: number) => (
                          <button
                            key={idx}
                            onClick={() => insertVariable('${' + v.path + '}', 'approval')}
                            className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                            title={v.description}
                          >
                            ${'{' + v.path + '}'}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Previous Node Outputs */}
                  {availableVars.nodeOutputs.length > 0 && (
                    <div className="mb-12">
                      <p className="text-xs text-heat-100 font-medium mb-6">Previous Nodes:</p>
                      <div className="flex flex-wrap gap-6">
                        {availableVars.nodeOutputs.map((v: any, idx: number) => (
                          <button
                            key={idx}
                            onClick={() => insertVariable('${' + v.path + '}', 'approval')}
                            className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                            title={v.description}
                          >
                            ${'{' + v.path + '}'}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Special Variables */}
                  <div>
                    <p className="text-xs text-heat-100 font-medium mb-6">Special:</p>
                    <div className="flex flex-wrap gap-6">
                      {availableVars.special.filter(v => v.name !== 'iteration').map((v: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => insertVariable('${' + v.path + '}', 'approval')}
                          className="px-10 py-6 bg-heat-8 hover:bg-heat-12 text-accent-black rounded-6 text-xs font-mono transition-colors"
                          title={v.description}
                        >
                          ${'{' + v.path + '}'}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Common Message Patterns */}
                <div className="p-16 bg-background-base rounded-12 border border-border-faint">
                  <h3 className="text-label-small text-accent-black mb-12">Common Message Patterns:</h3>
                  <div className="grid grid-cols-1 gap-8">
                    <button
                      onClick={() => setApprovalMessage('Please review and approve: ${lastOutput}')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">Please review and approve: ${'{lastOutput}'}</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Simple approval with data</p>
                    </button>
                    <button
                      onClick={() => setApprovalMessage('Transaction for ${input.amount} requires approval')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">Transaction for ${'{input.amount}'} requires approval</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Financial approval</p>
                    </button>
                    <button
                      onClick={() => setApprovalMessage('Review ${input.user}\'s request: ${lastOutput.summary}')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">Review ${'{input.user}'}'s request: ${'{lastOutput.summary}'}</p>
                      <p className="text-xs text-black-alpha-48 mt-2">User action approval</p>
                    </button>
                    <button
                      onClick={() => setApprovalMessage('Approve deployment to ${input.environment}?\n\nChanges:\n${lastOutput.changes}')}
                      className="text-left px-12 py-8 bg-accent-white hover:bg-heat-4 border border-border-faint rounded-6 transition-colors"
                    >
                      <p className="text-xs font-mono text-heat-100">Multi-line deployment approval</p>
                      <p className="text-xs text-black-alpha-48 mt-2">Detailed approval with formatting</p>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Timeout (minutes)
                  </label>
                  <input
                    type="number"
                    value={timeoutMinutes}
                    onChange={(e) => setTimeoutMinutes(e.target.value)}
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-8">
                    How long to wait for approval before timing out
                  </p>
                </div>

                <div className="p-16 bg-heat-4 rounded-12 border border-heat-100">
                  <h3 className="text-label-small text-accent-black mb-8">How it works</h3>
                  <p className="text-body-small text-heat-100 mb-12">
                    The workflow will pause at this node and notify the user with your approval message. Execution continues down the "Approve" branch when approved, or the "Reject" branch when rejected or timed out.
                  </p>
                  <div className="flex gap-8 text-xs">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-green-500"></div>
                      <span className="text-black-alpha-64">Approve branch</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-red-500"></div>
                      <span className="text-black-alpha-64">Reject branch</span>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Universal Output Selector */}
            <div className="pt-16 border-t border-border-faint">
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
