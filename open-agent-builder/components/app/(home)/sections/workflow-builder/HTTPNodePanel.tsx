"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import type { Node } from "@xyflow/react";
import VariableReferencePicker from "./VariableReferencePicker";

interface HTTPNodePanelProps {
  node: Node | null;
  nodes?: Node[];
  onClose: () => void;
  onDelete: (nodeId: string) => void;
  onUpdate: (nodeId: string, data: any) => void;
}

interface Header {
  key: string;
  value: string;
}

export default function HTTPNodePanel({ node, nodes, onClose, onDelete, onUpdate }: HTTPNodePanelProps) {
  const nodeData = node?.data as any;

  const [url, setUrl] = useState(nodeData?.httpUrl || "https://api.example.com/endpoint");
  const [method, setMethod] = useState(nodeData?.httpMethod || "GET");
  const [headers, setHeaders] = useState<Header[]>(nodeData?.httpHeaders || [
    { key: "Content-Type", value: "application/json" }
  ]);
  const [body, setBody] = useState(nodeData?.httpBody || "");
  const [authType, setAuthType] = useState(nodeData?.httpAuthType || "none");
  const [authToken, setAuthToken] = useState(nodeData?.httpAuthToken || "");
  const [showAuthToken, setShowAuthToken] = useState(false);

  // Auto-save
  useEffect(() => {
    if (!node) return;

    const timeoutId = setTimeout(() => {
      onUpdate(node.id, {
        httpUrl: url,
        httpMethod: method,
        httpHeaders: headers,
        httpBody: body,
        httpAuthType: authType,
        httpAuthToken: authToken,
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [url, method, headers, body, authType, authToken, node, onUpdate]);

  const addHeader = () => {
    setHeaders([...headers, { key: "", value: "" }]);
  };

  const updateHeader = (index: number, field: 'key' | 'value', value: string) => {
    setHeaders(headers.map((h, i) => i === index ? { ...h, [field]: value } : h));
  };

  const removeHeader = (index: number) => {
    setHeaders(headers.filter((_, i) => i !== index));
  };

  const insertQuickHeader = (key: string, value: string) => {
    const existing = headers.findIndex(h => h.key === key);
    if (existing >= 0) {
      updateHeader(existing, 'value', value);
    } else {
      setHeaders([...headers, { key, value }]);
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
          <div className="p-16 border-b border-border-faint">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-title-h4 text-accent-black">HTTP Request</h3>
              <div className="flex items-center gap-8">
                <button
                  onClick={() => onDelete(node?.id || '')}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                  title="Delete node"
                >
                  <svg className="w-16 h-16 text-black-alpha-48 group-hover:text-accent-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
              Call any HTTP/REST API
            </p>
          </div>

          {/* Form */}
          <div className="p-16 space-y-16">
            {/* Method and URL */}
            <div>
              <label className="block text-label-small text-black-alpha-48 mb-8">
                Request
              </label>
              <div className="flex gap-8">
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="px-12 py-8 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-medium focus:outline-none focus:border-heat-100 transition-colors"
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="PATCH">PATCH</option>
                  <option value="DELETE">DELETE</option>
                </select>

                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://api.example.com/endpoint"
                    className="w-full px-12 py-8 pr-150 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                  />
                  {nodes && (
                    <div className="absolute right-8 top-1/2 -translate-y-1/2">
                      <VariableReferencePicker
                        nodes={nodes}
                        currentNodeId={node.id}
                        onSelect={(ref) => setUrl(url + `{{${ref}}}`)}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Authentication */}
            <div>
              <label className="block text-label-small text-black-alpha-48 mb-8">
                Authentication
              </label>
              <select
                value={authType}
                onChange={(e) => setAuthType(e.target.value)}
                className="w-full px-12 py-8 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black focus:outline-none focus:border-heat-100 transition-colors mb-12"
              >
                <option value="none">None</option>
                <option value="bearer">Bearer Token</option>
                <option value="basic">Basic Auth</option>
                <option value="api-key">API Key (Header)</option>
              </select>

              {authType !== 'none' && (
                <div className="relative">
                  <input
                    type={showAuthToken ? "text" : "password"}
                    value={authToken}
                    onChange={(e) => setAuthToken(e.target.value)}
                    placeholder={authType === 'bearer' ? 'Bearer token...' : 'API key or credentials...'}
                    className="w-full px-12 py-8 pr-40 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                  />
                  <button
                    onClick={() => setShowAuthToken(!showAuthToken)}
                    className="absolute right-12 top-1/2 -translate-y-1/2 text-black-alpha-48 hover:text-accent-black transition-colors"
                  >
                    {showAuthToken ? (
                      <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Headers */}
            <div>
              <div className="flex items-center justify-between mb-8">
                <label className="block text-label-small text-black-alpha-48">
                  Headers
                </label>
                <div className="flex gap-6">
                  <button
                    onClick={() => insertQuickHeader('Content-Type', 'application/json')}
                    className="px-8 py-4 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-4 text-body-small text-accent-black transition-colors"
                  >
                    + JSON
                  </button>
                  <button
                    onClick={addHeader}
                    className="px-8 py-4 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-4 text-body-small text-accent-black transition-colors"
                  >
                    + Header
                  </button>
                </div>
              </div>

              <div className="space-y-8">
                {headers.map((header, index) => (
                  <div key={index} className="flex gap-8">
                    <input
                      type="text"
                      value={header.key}
                      onChange={(e) => updateHeader(index, 'key', e.target.value)}
                      placeholder="Header-Name"
                      className="flex-1 px-10 py-6 bg-background-base border border-border-faint rounded-6 text-body-small text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                    />
                    <input
                      type="text"
                      value={header.value}
                      onChange={(e) => updateHeader(index, 'value', e.target.value)}
                      placeholder="value"
                      className="flex-1 px-10 py-6 bg-background-base border border-border-faint rounded-6 text-body-small text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                    />
                    <button
                      onClick={() => removeHeader(index)}
                      className="w-24 h-24 rounded-4 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                    >
                      <svg className="w-12 h-12 text-black-alpha-48 group-hover:text-accent-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Body (for POST/PUT/PATCH) */}
            {(method === 'POST' || method === 'PUT' || method === 'PATCH') && (
              <div>
                <div className="flex items-center justify-between mb-8">
                  <label className="block text-label-small text-black-alpha-48">
                    Request Body
                  </label>
                  {nodes && (
                    <VariableReferencePicker
                      nodes={nodes}
                      currentNodeId={node.id}
                      onSelect={(ref) => setBody(body + `{{${ref}}}`)}
                    />
                  )}
                </div>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={8}
                  placeholder='{"key": "value"}'
                  className="w-full px-12 py-10 bg-gray-900 text-heat-100 border border-border-faint rounded-8 text-body-small font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
                />
                <div className="flex gap-8 mt-8">
                  <button
                    onClick={() => setBody('{{state.variables.lastOutput}}')}
                    className="px-10 py-6 bg-heat-4 hover:bg-heat-8 border border-heat-100 rounded-6 text-body-small text-accent-black transition-colors"
                  >
                    Use Previous Output
                  </button>
                  <button
                    onClick={() => setBody(JSON.stringify({ data: "{{state.variables.lastOutput}}" }, null, 2))}
                    className="px-10 py-6 bg-heat-4 hover:bg-heat-8 border border-heat-100 rounded-6 text-body-small text-accent-black transition-colors"
                  >
                    Wrap in JSON
                  </button>
                </div>
              </div>
            )}

            {/* Quick Examples */}
            <details className="group">
              <summary className="cursor-pointer text-body-small text-heat-100 hover:text-heat-200 transition-colors">
                Show API examples
              </summary>
              <div className="mt-12 space-y-8">
                <button
                  onClick={() => {
                    setUrl('https://api.slack.com/api/chat.postMessage');
                    setMethod('POST');
                    insertQuickHeader('Authorization', 'Bearer xoxb-your-token');
                    setBody('{\n  "channel": "C123456",\n  "text": "{{state.variables.lastOutput}}"\n}');
                  }}
                  className="w-full p-10 bg-heat-4 hover:bg-heat-8 rounded-6 text-left border border-heat-100 transition-colors"
                >
                  <p className="text-body-small text-accent-black font-medium">Slack Message</p>
                  <p className="text-body-small text-heat-100 mt-4">Post to Slack channel</p>
                </button>

                <button
                  onClick={() => {
                    setUrl('https://api.notion.com/v1/pages');
                    setMethod('POST');
                    insertQuickHeader('Authorization', 'Bearer secret_...');
                    insertQuickHeader('Notion-Version', '2022-06-28');
                    setBody('{\n  "parent": { "database_id": "..." },\n  "properties": {}\n}');
                  }}
                  className="w-full p-10 bg-heat-4 hover:bg-heat-8 rounded-6 text-left border border-heat-100 transition-colors"
                >
                  <p className="text-body-small text-accent-black font-medium">Notion Page</p>
                  <p className="text-body-small text-heat-100 mt-4">Create Notion page</p>
                </button>

                <button
                  onClick={() => {
                    setUrl('https://hooks.zapier.com/hooks/catch/...');
                    setMethod('POST');
                    setBody('{{state.variables.lastOutput}}');
                  }}
                  className="w-full p-10 bg-heat-4 hover:bg-heat-8 rounded-6 text-left border border-heat-100 transition-colors"
                >
                  <p className="text-body-small text-accent-black font-medium">Zapier Webhook</p>
                  <p className="text-body-small text-heat-100 mt-4">Trigger Zapier automation</p>
                </button>
              </div>
            </details>

            {/* Universal Output Selector */}
            <div className="pt-16 border-t border-border-faint">
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
