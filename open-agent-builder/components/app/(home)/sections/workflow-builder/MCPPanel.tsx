"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { Globe, Brain, Database, Package, Loader2, ChevronDown } from "lucide-react";
import type { Node } from "@xyflow/react";
import { toast } from "sonner";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useUser } from "@clerk/nextjs";

interface MCPPanelProps {
  node: Node | null;
  onClose: () => void;
  onUpdate: (nodeId: string, data: any) => void;
  mode?: 'configure' | 'add-to-agent';
  onAddToAgent?: (mcpConfig: any) => void;
  onOpenSettings?: () => void;
}

export default function MCPPanel({
  node,
  onClose,
  onUpdate,
  mode = 'configure',
  onAddToAgent,
  onOpenSettings
}: MCPPanelProps) {
  const { user } = useUser();
  const nodeData = node?.data as any;

  // Fetch enabled MCP servers from central registry
  const mcpServers = useQuery(api.mcpServers.getEnabledMCPs,
    user?.id ? { userId: user.id } : "skip"
  );

  // Store only the selected server ID
  const [selectedServerId, setSelectedServerId] = useState<string | null>(() => {
    return nodeData?.mcpServerId || null;
  });

  const [showDetails, setShowDetails] = useState(false);
  const selectedServer = mcpServers?.find(s => s._id === selectedServerId);

  // Auto-save selected server ID (only in configure mode)
  useEffect(() => {
    if (!node || mode === 'add-to-agent') return;

    const timeoutId = setTimeout(() => {
      try {
        onUpdate(node.id, {
          mcpServerId: selectedServerId,
        });
      } catch (error) {
        console.error('Error saving MCP server selection:', error);
        toast.error('Failed to save MCP server selection', {
          description: error instanceof Error ? error.message : 'Unable to save changes',
        });
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [selectedServerId, node, onUpdate, mode]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'web': return <Globe className="w-16 h-16" />;
      case 'ai': return <Brain className="w-16 h-16" />;
      case 'data': return <Database className="w-16 h-16" />;
      default: return <Package className="w-16 h-16" />;
    }
  };

  return (
    <AnimatePresence>
      {(node || mode === 'add-to-agent') && (
        <motion.aside
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 400, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed right-20 top-80 bottom-20 w-[calc(100vw-240px)] max-w-520 bg-accent-white border border-border-faint shadow-lg overflow-y-auto z-50 rounded-16 flex flex-col"
        >
          {/* Header */}
          <div className="p-20 border-b border-border-faint">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-semibold text-accent-black">
                {mode === 'add-to-agent' ? 'Add MCP to Agent' : 'Tools Node'}
              </h2>
              <button
                onClick={onClose}
                className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
              >
                <svg className="w-16 h-16 text-black-alpha-48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-black-alpha-48">
              Select tools from an MCP server to invoke them in your agent
            </p>
          </div>

          {/* Configuration */}
          <div className="p-20 space-y-20">
            {/* Server Selector */}
            <div>
              <label className="block text-sm font-medium text-black-alpha-48 mb-8">
                MCP Servers
              </label>

              {!mcpServers || mcpServers.length === 0 ? (
                <div className="p-16 bg-background-base rounded-12 border border-border-faint text-center">
                  <p className="text-body-small text-black-alpha-48 mb-12">
                    No servers available in your MCP registry
                  </p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onOpenSettings) {
                        onOpenSettings();
                      }
                      setTimeout(() => {
                        onClose();
                      }, 200); // Slight delay ensures settings modal opens
                    }}
                    className="px-16 py-8 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-xs font-medium transition-all"
                  >
                    Go to Settings
                  </button>
                </div>
              ) : (
                <div className="space-y-8">
                  <select
                    value={selectedServerId || ""}
                    onChange={(e) => {
                      const serverId = e.target.value || null;
                      setSelectedServerId(serverId);

                      // In add-to-agent mode, call the callback
                      if (mode === 'add-to-agent' && onAddToAgent && serverId) {
                        const server = mcpServers.find(s => s._id === serverId);
                        if (server) {
                          onAddToAgent({
                            mcpServerId: server._id,
                            name: server.name,
                            tools: server.tools || [],
                          });
                          toast.success(`Added ${server.name} to agent`);
                          setTimeout(() => onClose(), 1000);
                        }
                      }
                    }}
                    className="w-full px-14 py-10 bg-background-base border border-border-faint rounded-10 text-sm text-accent-black focus:outline-none focus:border-heat-100 transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">Select an MCP server...</option>
                    {mcpServers.map((server) => {
                      // const isFirecrawl = server.name === 'Firecrawl' && server.isOfficial;
                      return (
                        <option key={server._id} value={server._id}>
                          {server.name} {/* {isFirecrawl && '(API Key Required)'} */} {server.tools && `(${server.tools.length} tools)`}
                        </option>
                      );
                    })}
                  </select>

                  {selectedServer && (
                    <div className="mt-12">
                      {/* Server Info Card */}
                      <div className="p-16 bg-background-base rounded-12 border border-border-faint">
                        <div className="flex items-start gap-12">
                          <div className={`text-heat-100`}>
                            {getCategoryIcon(selectedServer.category)}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-8 mb-4">
                              <h4 className="text-sm font-medium text-accent-black">
                                {selectedServer.name}
                              </h4>
                              {/* {selectedServer.name === 'Firecrawl' && selectedServer.isOfficial && (
                                <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-6 text-xs border border-heat-100 font-medium">
                                  API Key Required
                                </span>
                              )} */}
                            </div>
                            {selectedServer.description && (
                              <p className="text-xs text-black-alpha-48 mb-8">
                                {selectedServer.description}
                              </p>
                            )}
                            {/* {selectedServer.name === 'Firecrawl' && selectedServer.isOfficial && (
                              <a
                                href="https://www.firecrawl.dev/app/api-keys"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-heat-100 hover:text-heat-200 underline block mb-8"
                              >
                                Get API key here →
                              </a>
                            )} */}
                            <div className="flex items-center gap-12 text-xs">
                              <span className="text-black-alpha-48">
                                Category: {selectedServer.category}
                              </span>
                              {selectedServer.connectionStatus === 'connected' && (
                                <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-6 border border-heat-100">
                                  Connected
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Show/Hide Tools Button */}
                        {selectedServer.tools && selectedServer.tools.length > 0 && (
                          <div className="mt-12">
                            <button
                              onClick={() => setShowDetails(!showDetails)}
                              className="flex items-center gap-8 text-xs text-heat-100 hover:text-heat-200 font-medium"
                            >
                              <ChevronDown className={`w-14 h-14 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
                              {showDetails ? 'Hide' : 'Show'} Available Tools ({selectedServer.tools.length})
                            </button>

                            {/* Tools List */}
                            <AnimatePresence>
                              {showDetails && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: 'auto', opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  className="mt-8"
                                >
                                  <div className="space-y-6">
                                    {selectedServer.tools.map((tool: string) => (
                                      <div key={tool} className="p-8 bg-accent-white rounded-6 border border-border-faint">
                                        <code className="text-xs font-mono text-heat-100">
                                          {tool}
                                        </code>
                                      </div>
                                    ))}
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Add New Server Link */}
            <div className="pt-16 border-t border-border-faint">
              <p className="text-xs text-black-alpha-48 mb-8">
                Need to add a new MCP server?
              </p>
              <button
                onClick={() => {
                  onClose();
                  onOpenSettings?.();
                }}
                className="text-xs text-heat-100 hover:text-heat-200 font-medium"
              >
                Go to Settings → MCP Registry
              </button>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}