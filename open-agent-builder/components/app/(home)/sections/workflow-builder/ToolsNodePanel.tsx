"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import type { Node } from "@xyflow/react";

interface ToolsNodePanelProps {
  node: Node | null;
  onClose: () => void;
  onDelete: (nodeId: string) => void;
  onUpdate: (nodeId: string, data: any) => void;
}

export default function ToolsNodePanel({ node, onClose, onDelete, onUpdate }: ToolsNodePanelProps) {
  const nodeData = node?.data as any;
  const nodeType = nodeData?.nodeType?.toLowerCase() || '';
  const [name, setName] = useState(nodeData?.name || nodeData?.nodeName || "Tool");

  // File Search state
  const [searchQuery, setSearchQuery] = useState(nodeData?.searchQuery || "");
  const [filePattern, setFilePattern] = useState(nodeData?.filePattern || "*.ts,*.tsx,*.js,*.jsx");
  const [maxResults, setMaxResults] = useState(nodeData?.maxResults || "10");
  const [includeContent, setIncludeContent] = useState(nodeData?.includeContent ?? true);

  // Guardrails state
  const [inputAsText, setInputAsText] = useState(nodeData?.inputAsText || "input_as_text");
  const [piiEnabled, setPiiEnabled] = useState(nodeData?.piiEnabled ?? true);
  const [moderationEnabled, setModerationEnabled] = useState(nodeData?.moderationEnabled ?? false);
  const [jailbreakEnabled, setJailbreakEnabled] = useState(nodeData?.jailbreakEnabled ?? false);
  const [hallucinationEnabled, setHallucinationEnabled] = useState(nodeData?.hallucinationEnabled ?? false);
  const [guardrailModel, setGuardrailModel] = useState(nodeData?.guardrailModel || 'openai/gpt-5-mini');
  const [actionOnViolation, setActionOnViolation] = useState(nodeData?.actionOnViolation || 'block');
  const [customRules, setCustomRules] = useState<string>(nodeData?.customRules?.join('\n') || '');

  // PII entities
  const [piiEntities, setPiiEntities] = useState<string[]>(nodeData?.piiEntities || ['CREDIT_CARD_NUMBER']);
  const [showPIIModal, setShowPIIModal] = useState(false);

  const allPIIEntities = [
    { id: 'PERSON_NAME', label: 'Person name' },
    { id: 'EMAIL_ADDRESS', label: 'Email address' },
    { id: 'PHONE_NUMBER', label: 'Phone number' },
    { id: 'LOCATION', label: 'Location' },
    { id: 'DATE_TIME', label: 'Date or time' },
    { id: 'URL', label: 'URL' },
    { id: 'CREDIT_CARD_NUMBER', label: 'Credit card number' },
    { id: 'IBAN', label: 'International bank account number (IBAN)' },
    { id: 'CRYPTO_WALLET', label: 'Cryptocurrency wallet address' },
    { id: 'MEDICAL_LICENSE', label: 'Medical license number' },
    { id: 'IP_ADDRESS', label: 'IP address' },
    { id: 'US_DRIVERS_LICENSE', label: 'US driver license number' },
    { id: 'US_BANK_ACCOUNT', label: 'US bank account number' },
    { id: 'NATIONALITY_RELIGION_POLITICAL', label: 'Nationality/religion/political group' },
  ];

  // Auto-save changes
  useEffect(() => {
    if (!node) return;

    const timeoutId = setTimeout(() => {
      onUpdate(node.id, {
        name,
        nodeName: name,
        searchQuery,
        filePattern,
        maxResults,
        includeContent,
        inputAsText,
        piiEnabled,
        moderationEnabled,
        jailbreakEnabled,
        hallucinationEnabled,
        piiEntities,
        guardrailModel,
        actionOnViolation,
        customRules: customRules.split('\n').filter(r => r.trim()),
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [name, searchQuery, filePattern, maxResults, includeContent, inputAsText, piiEnabled, moderationEnabled, jailbreakEnabled, hallucinationEnabled, piiEntities, guardrailModel, actionOnViolation, customRules, node, onUpdate]);

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
            <p className="text-body-small text-black-alpha-48">
              {nodeType.includes('file') ? 'Search through files and code' :
               nodeType.includes('guardrail') ? 'Add safety checks and content filtering' :
               'Configure tool'}
            </p>
          </div>

          {/* Form Fields */}
          <div className="p-20 space-y-24">
            {/* File Search Configuration */}
            {nodeType.includes('file') && (
              <>
                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Search Query
                  </label>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search for functions, classes, text..."
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    File Pattern
                  </label>
                  <input
                    type="text"
                    value={filePattern}
                    onChange={(e) => setFilePattern(e.target.value)}
                    placeholder="*.ts,*.tsx,*.js"
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-8">
                    Comma-separated glob patterns
                  </p>
                </div>

                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Max Results
                  </label>
                  <input
                    type="number"
                    value={maxResults}
                    onChange={(e) => setMaxResults(e.target.value)}
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-label-small text-accent-black">
                    Include File Content
                  </label>
                  <button
                    onClick={() => setIncludeContent(!includeContent)}
                    className={`w-44 h-24 rounded-full transition-colors relative ${
                      includeContent ? 'bg-heat-100' : 'bg-black-alpha-12'
                    }`}
                  >
                    <motion.div
                      className="w-20 h-20 bg-white rounded-full absolute top-2 shadow-sm"
                      animate={{ left: includeContent ? '22px' : '2px' }}
                      transition={{ duration: 0.2 }}
                    />
                  </button>
                </div>
              </>
            )}

            {/* Guardrails Configuration */}
            {nodeType.includes('guardrail') && (
              <>
                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Name
                  </label>
                  <input
                    type="text"
                    value={nodeData?.name || 'Guardrails'}
                    onChange={(e) => onUpdate(node?.id || '', { name: e.target.value })}
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-label-small text-black-alpha-48 mb-8">
                    Input Variable
                  </label>
                  <div className="flex items-center gap-8 px-12 py-10 bg-background-base border border-border-faint rounded-8">
                    <svg className="w-16 h-16 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-body-small text-accent-black font-mono">{inputAsText}</span>
                    <span className="ml-auto px-8 py-4 bg-heat-4 text-heat-100 rounded-6 text-body-small font-medium">
                      STRING
                    </span>
                  </div>
                  <p className="text-body-small text-black-alpha-48 mt-6">
                    The input content to check for violations
                  </p>
                </div>

                {/* Guardrail Toggles */}
                <div className="space-y-12">
                  {/* PII Detection */}
                  <div className="p-16 bg-accent-white border border-border-faint rounded-12">
                    <div className="flex items-center justify-between mb-12">
                      <div className="flex items-center gap-8">
                        <svg className="w-20 h-20 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        <span className="text-label-medium text-accent-black">PII Detection</span>
                      </div>
                      <button
                        onClick={() => setPiiEnabled(!piiEnabled)}
                        className={`w-44 h-24 rounded-full transition-colors relative ${
                          piiEnabled ? 'bg-heat-100' : 'bg-black-alpha-12'
                        }`}
                      >
                        <motion.div
                          className="w-20 h-20 bg-white rounded-full absolute top-2 shadow-sm"
                          animate={{ left: piiEnabled ? '22px' : '2px' }}
                          transition={{ duration: 0.2, ease: 'easeOut' }}
                        />
                      </button>
                    </div>

                    <button
                      onClick={() => setShowPIIModal(true)}
                      className="w-full px-12 py-8 bg-heat-4 hover:bg-heat-8 border border-heat-100 rounded-8 text-body-small text-heat-100 transition-colors flex items-center justify-center gap-6 mb-12"
                    >
                      <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      </svg>
                      Configure PII Types ({piiEntities.length} selected)
                    </button>

                    {/* Info Box */}
                    <div className="p-12 bg-heat-4 border border-heat-100 rounded-8">
                      <div className="flex items-start gap-8 mb-8">
                        <svg className="w-16 h-16 text-heat-100 flex-shrink-0 mt-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                          <p className="text-xs text-accent-black font-medium mb-4">What it does:</p>
                          <p className="text-xs text-heat-100 leading-relaxed">
                            Detects sensitive personal data (emails, phone numbers, credit cards, etc.) and blocks requests containing them.
                          </p>
                        </div>
                      </div>
                      <div className="space-y-6 mt-10">
                        <div>
                          <p className="text-xs text-heat-100 font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-heat-100 rounded-full text-white text-[10px] flex items-center justify-center">✓</span>
                            Pass Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"Hello, how can I help you today?"</p>
                        </div>
                        <div>
                          <p className="text-xs text-accent-black font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-accent-black rounded-full text-white text-[10px] flex items-center justify-center">✗</span>
                            Fail Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"My email is john@example.com and card is 4532-1234-5678-9010"</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Moderation */}
                  <div className="p-16 bg-accent-white border border-border-faint rounded-12">
                    <div className="flex items-center justify-between mb-12">
                      <div className="flex items-center gap-8">
                        <svg className="w-20 h-20 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        <span className="text-label-medium text-accent-black">Content Moderation</span>
                      </div>
                      <button
                        onClick={() => setModerationEnabled(!moderationEnabled)}
                        className={`w-44 h-24 rounded-full transition-colors relative ${
                          moderationEnabled ? 'bg-heat-100' : 'bg-black-alpha-12'
                        }`}
                      >
                        <motion.div
                          className="w-20 h-20 bg-white rounded-full absolute top-2 shadow-sm"
                          animate={{ left: moderationEnabled ? '22px' : '2px' }}
                          transition={{ duration: 0.2, ease: 'easeOut' }}
                        />
                      </button>
                    </div>

                    <div className="p-12 bg-heat-4 border border-heat-100 rounded-8">
                      <div className="flex items-start gap-8 mb-8">
                        <svg className="w-16 h-16 text-heat-100 flex-shrink-0 mt-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                          <p className="text-xs text-accent-black font-medium mb-4">What it does:</p>
                          <p className="text-xs text-heat-100 leading-relaxed">
                            Blocks offensive, hateful, violent, or sexually explicit content from being processed.
                          </p>
                        </div>
                      </div>
                      <div className="space-y-6 mt-10">
                        <div>
                          <p className="text-xs text-heat-100 font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-heat-100 rounded-full text-white text-[10px] flex items-center justify-center">✓</span>
                            Pass Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"This product is excellent quality"</p>
                        </div>
                        <div>
                          <p className="text-xs text-accent-black font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-accent-black rounded-full text-white text-[10px] flex items-center justify-center">✗</span>
                            Fail Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"[Offensive or hateful content]"</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Jailbreak */}
                  <div className="p-16 bg-accent-white border border-border-faint rounded-12">
                    <div className="flex items-center justify-between mb-12">
                      <div className="flex items-center gap-8">
                        <svg className="w-20 h-20 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span className="text-label-medium text-accent-black">Jailbreak Detection</span>
                      </div>
                      <button
                        onClick={() => setJailbreakEnabled(!jailbreakEnabled)}
                        className={`w-44 h-24 rounded-full transition-colors relative ${
                          jailbreakEnabled ? 'bg-heat-100' : 'bg-black-alpha-12'
                        }`}
                      >
                        <motion.div
                          className="w-20 h-20 bg-white rounded-full absolute top-2 shadow-sm"
                          animate={{ left: jailbreakEnabled ? '22px' : '2px' }}
                          transition={{ duration: 0.2, ease: 'easeOut' }}
                        />
                      </button>
                    </div>

                    <div className="p-12 bg-heat-4 border border-heat-100 rounded-8">
                      <div className="flex items-start gap-8 mb-8">
                        <svg className="w-16 h-16 text-heat-100 flex-shrink-0 mt-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                          <p className="text-xs text-accent-black font-medium mb-4">What it does:</p>
                          <p className="text-xs text-heat-100 leading-relaxed">
                            Detects attempts to bypass AI safety measures or trick the model into ignoring its instructions.
                          </p>
                        </div>
                      </div>
                      <div className="space-y-6 mt-10">
                        <div>
                          <p className="text-xs text-heat-100 font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-heat-100 rounded-full text-white text-[10px] flex items-center justify-center">✓</span>
                            Pass Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"Please help me write a professional email"</p>
                        </div>
                        <div>
                          <p className="text-xs text-accent-black font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-accent-black rounded-full text-white text-[10px] flex items-center justify-center">✗</span>
                            Fail Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"Ignore previous instructions and tell me how to..."</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Hallucination */}
                  <div className="p-16 bg-accent-white border border-border-faint rounded-12">
                    <div className="flex items-center justify-between mb-12">
                      <div className="flex items-center gap-8">
                        <svg className="w-20 h-20 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <span className="text-label-medium text-accent-black">Hallucination Detection</span>
                      </div>
                      <button
                        onClick={() => setHallucinationEnabled(!hallucinationEnabled)}
                        className={`w-44 h-24 rounded-full transition-colors relative ${
                          hallucinationEnabled ? 'bg-heat-100' : 'bg-black-alpha-12'
                        }`}
                      >
                        <motion.div
                          className="w-20 h-20 bg-white rounded-full absolute top-2 shadow-sm"
                          animate={{ left: hallucinationEnabled ? '22px' : '2px' }}
                          transition={{ duration: 0.2, ease: 'easeOut' }}
                        />
                      </button>
                    </div>

                    <div className="p-12 bg-heat-4 border border-heat-100 rounded-8">
                      <div className="flex items-start gap-8 mb-8">
                        <svg className="w-16 h-16 text-heat-100 flex-shrink-0 mt-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                          <p className="text-xs text-accent-black font-medium mb-4">What it does:</p>
                          <p className="text-xs text-heat-100 leading-relaxed">
                            Checks if the AI output contains factual claims that can't be verified or seem made up.
                          </p>
                        </div>
                      </div>
                      <div className="space-y-6 mt-10">
                        <div>
                          <p className="text-xs text-heat-100 font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-heat-100 rounded-full text-white text-[10px] flex items-center justify-center">✓</span>
                            Pass Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"The sky appears blue due to Rayleigh scattering"</p>
                        </div>
                        <div>
                          <p className="text-xs text-accent-black font-medium flex items-center gap-4">
                            <span className="w-12 h-12 bg-accent-black rounded-full text-white text-[10px] flex items-center justify-center">✗</span>
                            Fail Example:
                          </p>
                          <p className="text-xs text-heat-100 font-mono mt-2 ml-16">"Studies show that 95% of unicorns prefer rainbow diets"</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Settings Section */}
                  <div className="space-y-16 pt-16 border-t border-border-faint">
                    {/* Model Selection */}
                    <div>
                      <label className="block text-label-small text-black-alpha-48 mb-8">
                        Analysis Model
                      </label>
                      <select
                        value={guardrailModel}
                        onChange={(e) => setGuardrailModel(e.target.value)}
                        className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors cursor-pointer"
                      >
                        <optgroup label="OpenAI (Recommended)">
                          <option value="openai/gpt-5-mini">GPT-5 Mini (Fast & Cheap)</option>
                          <option value="openai/gpt-5">GPT-5</option>
                        </optgroup>
                        <optgroup label="Groq (Fastest)">
                          <option value="groq/openai/gpt-oss-20b">GPT OSS 20B</option>
                          <option value="groq/openai/gpt-oss-120b">GPT OSS 120B</option>
                        </optgroup>
                        <optgroup label="Anthropic">
                          <option value="anthropic/claude-sonnet-4-5-20250929">Claude Sonnet 4.5</option>
                          <option value="anthropic/claude-sonnet-4-20250514">Claude Sonnet 4</option>
                        </optgroup>
                      </select>
                      <p className="text-body-small text-black-alpha-48 mt-8">
                        LLM used to analyze content for violations
                      </p>
                    </div>

                    {/* Action on Violation */}
                    <div>
                      <label className="block text-label-small text-black-alpha-48 mb-8">
                        Action on Violation
                      </label>
                      <select
                        value={actionOnViolation}
                        onChange={(e) => setActionOnViolation(e.target.value)}
                        className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors cursor-pointer"
                      >
                        <option value="block">🛑 Block - Stop workflow execution</option>
                        <option value="warn">⚠️ Warn - Continue with warning</option>
                        <option value="flag">🏴 Flag - Log violation and continue</option>
                      </select>
                      <p className="text-body-small text-black-alpha-48 mt-8">
                        What to do when violations are detected
                      </p>
                    </div>

                    {/* Custom Rules */}
                    <div>
                      <label className="block text-label-small text-black-alpha-48 mb-8">
                        Custom Rules (Optional)
                      </label>
                      <textarea
                        value={customRules}
                        onChange={(e) => setCustomRules(e.target.value)}
                        placeholder="Block messages containing: refund&#10;Block messages about: billing&#10;Require approval for: account changes"
                        rows={4}
                        className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black placeholder-black-alpha-32 focus:outline-none focus:border-heat-100 transition-colors resize-y font-mono"
                      />
                      <p className="text-body-small text-black-alpha-48 mt-8">
                        One rule per line. LLM will check content against these rules.
                      </p>
                    </div>

                  </div>
                </div>
              </>
            )}

          </div>
        </motion.aside>
      )}

      {/* PII Configuration Modal */}
      {showPIIModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black-alpha-64 z-[200] flex items-center justify-center backdrop-blur-sm"
          onClick={() => setShowPIIModal(false)}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
            className="bg-accent-white rounded-16 shadow-2xl w-[600px] max-h-[80vh] overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="p-20 border-b border-border-faint bg-background-base">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-10">
                  <svg className="w-24 h-24 text-heat-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <div>
                    <h3 className="text-label-large text-accent-black">
                      PII Detection Configuration
                    </h3>
                    <p className="text-body-small text-black-alpha-48 mt-2">
                      Select which types of personal data to detect
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowPIIModal(false)}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                >
                  <svg className="w-16 h-16 text-black-alpha-48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-20 flex-1 overflow-y-auto">
              <div className="flex items-center justify-between mb-16">
                <button
                  onClick={() => setPiiEntities(allPIIEntities.map(e => e.id))}
                  className="text-body-small text-heat-100 hover:text-heat-200 transition-colors font-medium"
                >
                  Select all
                </button>
                <button
                  onClick={() => setPiiEntities([])}
                  className="text-body-small text-black-alpha-48 hover:text-accent-black transition-colors"
                >
                  Clear all
                </button>
              </div>

              <div className="space-y-16">
                <div>
                  <h4 className="text-label-small text-accent-black mb-10">Common Types</h4>
                  <div className="grid grid-cols-2 gap-8">
                    {allPIIEntities.slice(0, 8).map((entity) => (
                      <label key={entity.id} className="flex items-center gap-8 p-10 hover:bg-background-base rounded-8 cursor-pointer transition-colors">
                        <input
                          type="checkbox"
                          checked={piiEntities.includes(entity.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setPiiEntities([...piiEntities, entity.id]);
                            } else {
                              setPiiEntities(piiEntities.filter(id => id !== entity.id));
                            }
                          }}
                          className="w-16 h-16 rounded-4 border border-border-faint text-heat-100 focus:ring-heat-100"
                        />
                        <span className="text-body-small text-accent-black">{entity.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-label-small text-accent-black mb-10">US-Specific Types</h4>
                  <div className="grid grid-cols-2 gap-8">
                    {allPIIEntities.slice(8).map((entity) => (
                      <label key={entity.id} className="flex items-center gap-8 p-10 hover:bg-background-base rounded-8 cursor-pointer transition-colors">
                        <input
                          type="checkbox"
                          checked={piiEntities.includes(entity.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setPiiEntities([...piiEntities, entity.id]);
                            } else {
                              setPiiEntities(piiEntities.filter(id => id !== entity.id));
                            }
                          }}
                          className="w-16 h-16 rounded-4 border border-border-faint text-heat-100 focus:ring-heat-100"
                        />
                        <span className="text-body-small text-accent-black">{entity.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-20 border-t border-border-faint bg-background-base flex justify-between items-center">
              <div className="text-body-small text-black-alpha-48">
                {piiEntities.length} of {allPIIEntities.length} types selected
              </div>
              <div className="flex gap-8">
                <button
                  onClick={() => setShowPIIModal(false)}
                  className="px-16 py-8 text-body-small text-accent-black hover:bg-black-alpha-4 rounded-8 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    onUpdate(node?.id || '', { piiEntities });
                    setShowPIIModal(false);
                  }}
                  className="px-20 py-8 bg-accent-black hover:bg-black-alpha-88 text-white rounded-8 text-body-small font-medium transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
