"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { toast } from "sonner";

interface ConnectorsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

interface MCPTemplate {
  id: string;
  name: string;
  description: string;
  url: string;
  authType: 'none' | 'api-key' | 'oauth';
  apiKeyPlaceholder?: string;
  tools: string[];
  category: 'web' | 'ai' | 'data' | 'custom';
}

const MCP_TEMPLATES: MCPTemplate[] = [
  {
    id: 'browserbase',
    name: 'Browserbase',
    description: 'Browser automation and web scraping',
    url: 'https://mcp.browserbase.com',
    authType: 'api-key',
    apiKeyPlaceholder: 'BROWSERBASE_API_KEY',
    tools: ['browser_navigate', 'browser_click', 'browser_scrape'],
    category: 'web',
  },
];

export default function ConnectorsPanel({ isOpen, onClose }: ConnectorsPanelProps) {
  const [activeTab, setActiveTab] = useState<'mcp' | 'llm'>('mcp');
  const [mcpTab, setMcpTab] = useState<'templates' | 'custom'>('templates');
  const [connectedMCPs, setConnectedMCPs] = useState<any[]>([]);

  // Custom MCP form
  const [customName, setCustomName] = useState('');
  const [customUrl, setCustomUrl] = useState('');
  const [customAuthType, setCustomAuthType] = useState('none');
  const [customApiKey, setCustomApiKey] = useState('');

  const handleConnectTemplate = (template: MCPTemplate) => {
    if (template.authType === 'api-key') {
      // Show API key input
      const apiKey = prompt(`Enter your ${template.apiKeyPlaceholder}:`);
      if (!apiKey) return;

      const url = template.url.replace(`{${template.apiKeyPlaceholder}}`, apiKey);
      const newMCP = {
        id: `${template.id}_${Date.now()}`,
        name: template.name,
        url,
        authType: 'api-key',
        accessToken: apiKey,
        tools: template.tools,
        category: template.category,
      };

      setConnectedMCPs([...connectedMCPs, newMCP]);
      toast.success(`Connected to ${template.name}`);
    } else {
      const newMCP = {
        id: `${template.id}_${Date.now()}`,
        name: template.name,
        url: template.url,
        authType: 'none',
        tools: template.tools,
        category: template.category,
      };

      setConnectedMCPs([...connectedMCPs, newMCP]);
      toast.success(`Connected to ${template.name}`);
    }
  };

  const handleConnectCustom = () => {
    if (!customName || !customUrl) {
      toast.error('Please fill in name and URL');
      return;
    }

    const newMCP = {
      id: `custom_${Date.now()}`,
      name: customName,
      url: customUrl,
      authType: customAuthType,
      accessToken: customAuthType !== 'none' ? customApiKey : undefined,
      tools: [],
      category: 'custom' as const,
    };

    setConnectedMCPs([...connectedMCPs, newMCP]);
    toast.success(`Connected to ${customName}`);

    // Reset form
    setCustomName('');
    setCustomUrl('');
    setCustomAuthType('none');
    setCustomApiKey('');
  };

  const handleDisconnect = (id: string) => {
    setConnectedMCPs(connectedMCPs.filter(m => m.id !== id));
    toast.success('MCP disconnected');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black-alpha-48 z-[100]"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed right-0 top-0 h-screen w-full max-w-600 bg-accent-white border-l border-border-faint shadow-2xl z-[101] flex flex-col"
          >
            {/* Header */}
            <div className="p-20 border-b border-border-faint">
              <div className="flex items-center justify-between mb-12">
                <h2 className="text-title-h3 text-accent-black">Connectors & Config</h2>
                <button
                  onClick={onClose}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                >
                  <svg className="w-16 h-16 text-black-alpha-48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Main Tabs */}
              <div className="flex gap-8">
                <button
                  onClick={() => setActiveTab('mcp')}
                  className={`px-16 py-8 rounded-8 text-body-medium font-medium transition-all ${
                    activeTab === 'mcp'
                      ? 'bg-heat-100 text-white'
                      : 'bg-background-base text-black-alpha-64 hover:bg-black-alpha-4'
                  }`}
                >
                  <div className="flex items-center gap-8">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    MCP Servers
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('llm')}
                  className={`px-16 py-8 rounded-8 text-body-medium font-medium transition-all ${
                    activeTab === 'llm'
                      ? 'bg-heat-100 text-white'
                      : 'bg-background-base text-black-alpha-64 hover:bg-black-alpha-4'
                  }`}
                >
                  <div className="flex items-center gap-8">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    LLM Config
                  </div>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {activeTab === 'mcp' ? (
                <div>
                  {/* MCP Sub-tabs */}
                  <div className="p-20 border-b border-border-faint">
                    <div className="flex gap-8">
                      <button
                        onClick={() => setMcpTab('templates')}
                        className={`flex-1 px-12 py-8 rounded-8 text-body-small transition-colors ${
                          mcpTab === 'templates'
                            ? 'bg-heat-4 text-heat-100 border border-heat-100'
                            : 'bg-background-base text-black-alpha-64 hover:bg-black-alpha-4'
                        }`}
                      >
                        Pre-configured
                      </button>
                      <button
                        onClick={() => setMcpTab('custom')}
                        className={`flex-1 px-12 py-8 rounded-8 text-body-small transition-colors ${
                          mcpTab === 'custom'
                            ? 'bg-heat-4 text-heat-100 border border-heat-100'
                            : 'bg-background-base text-black-alpha-64 hover:bg-black-alpha-4'
                        }`}
                      >
                        Custom Remote
                      </button>
                    </div>
                  </div>

                  {mcpTab === 'templates' ? (
                    <div className="p-20 space-y-16">
                      <div>
                        <h3 className="text-label-medium text-accent-black mb-12">MCP Templates</h3>
                        <div className="space-y-12">
                          {MCP_TEMPLATES.map((template) => (
                            <div key={template.id} className="p-16 bg-background-base rounded-12 border border-border-faint">
                              <div className="flex items-start justify-between mb-12">
                                <div className="flex-1">
                                  <div className="flex items-center gap-8 mb-6">
                                    <h4 className="text-label-medium text-accent-black font-medium">{template.name}</h4>
                                    <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-4 text-body-small">
                                      {template.category}
                                    </span>
                                  </div>
                                  <p className="text-body-small text-black-alpha-64 mb-8">{template.description}</p>
                                  <p className="text-body-small text-black-alpha-48 font-mono text-xs truncate">
                                    {template.tools.length} tools available
                                  </p>
                                </div>
                                <button
                                  onClick={() => handleConnectTemplate(template)}
                                  className="px-16 py-8 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-body-small font-medium transition-all active:scale-[0.98]"
                                >
                                  Connect
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-20 space-y-20">
                      <div>
                        <h3 className="text-label-medium text-accent-black mb-12">Add Custom MCP Server</h3>

                        <div className="space-y-16">
                          <div>
                            <label className="block text-label-small text-black-alpha-48 mb-8">Name</label>
                            <input
                              type="text"
                              value={customName}
                              onChange={(e) => setCustomName(e.target.value)}
                              placeholder="My Custom MCP"
                              className="w-full px-12 py-10 bg-accent-white border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                            />
                          </div>

                          <div>
                            <label className="block text-label-small text-black-alpha-48 mb-8">URL</label>
                            <input
                              type="text"
                              value={customUrl}
                              onChange={(e) => setCustomUrl(e.target.value)}
                              placeholder="https://mcp.example.com"
                              className="w-full px-12 py-10 bg-accent-white border border-border-faint rounded-8 text-body-medium text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                            />
                          </div>

                          <div>
                            <label className="block text-label-small text-black-alpha-48 mb-8">Authentication</label>
                            <select
                              value={customAuthType}
                              onChange={(e) => setCustomAuthType(e.target.value)}
                              className="w-full px-12 py-10 bg-accent-white border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:border-heat-100 transition-colors"
                            >
                              <option value="none">None</option>
                              <option value="api-key">API Key</option>
                              <option value="oauth">OAuth</option>
                            </select>
                          </div>

                          {customAuthType !== 'none' && (
                            <div>
                              <label className="block text-label-small text-black-alpha-48 mb-8">
                                {customAuthType === 'api-key' ? 'API Key' : 'OAuth Token'}
                              </label>
                              <input
                                type="password"
                                value={customApiKey}
                                onChange={(e) => setCustomApiKey(e.target.value)}
                                placeholder="Enter your key or ${ENV_VAR}"
                                className="w-full px-12 py-10 bg-accent-white border border-border-faint rounded-8 text-body-medium text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors"
                              />
                            </div>
                          )}

                          <button
                            onClick={handleConnectCustom}
                            className="w-full px-20 py-12 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-body-medium font-medium transition-all active:scale-[0.98]"
                          >
                            Add Custom MCP
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Connected MCPs */}
                  {connectedMCPs.length > 0 && (
                    <div className="p-20 border-t border-border-faint">
                      <h3 className="text-label-medium text-accent-black mb-12">Connected MCPs ({connectedMCPs.length})</h3>
                      <div className="space-y-12">
                        {connectedMCPs.map((mcp) => (
                          <div key={mcp.id} className="p-12 bg-accent-white rounded-8 border border-border-faint">
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <p className="text-body-small text-accent-black font-medium">{mcp.name}</p>
                                <p className="text-body-small text-black-alpha-48 font-mono text-xs truncate">{mcp.url}</p>
                              </div>
                              <button
                                onClick={() => handleDisconnect(mcp.id)}
                                className="px-12 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint hover:border-border-faint rounded-6 text-body-small text-accent-black transition-colors"
                              >
                                Disconnect
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-20">
                  <h3 className="text-label-medium text-accent-black mb-16">LLM Configuration</h3>
                  <div className="p-16 bg-accent-white rounded-12 border border-border-faint text-center">
                    <p className="text-body-medium text-black-alpha-48">
                      LLM configuration coming soon...
                    </p>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
