"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { ChevronDown } from "lucide-react";
import VariableReferencePicker from "./VariableReferencePicker";
import { toast } from "sonner";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useUser } from "@clerk/nextjs";
import { Id } from "@/convex/_generated/dataModel";
// import FirecrawlLogo from "@/components/icons/FirecrawlLogo";

interface NodePanelProps {
  nodeData: {
    id: string;
    label: string;
    type: string;
  } | null;
  nodes?: any[]; // All nodes for variable reference
  onClose: () => void;
  onAddMCP: () => void;
  onDelete: (nodeId: string) => void;
  onUpdate: (nodeId: string, data: any) => void;
  onOpenSettings?: () => void; // To open Settings panel for MCP configuration
}

export default function NodePanel({
  nodeData,
  nodes,
  onClose,
  onAddMCP,
  onDelete,
  onUpdate,
  onOpenSettings,
}: NodePanelProps) {
  const { user } = useUser();

  // MCP states - now store only server IDs, not full configs
  const [showMCPSelector, setShowMCPSelector] = useState(false);
  const [expandedMcpId, setExpandedMcpId] = useState<string | null>(null);
  const [currentMCPServerIds, setCurrentMCPServerIds] = useState<string[]>([]);
  const [showModelsDropdown, setShowModelsDropdown] = useState(false);

  // Fetch enabled MCP servers from central registry
  const mcpServers = useQuery(api.mcpServers.getEnabledMCPs,
    user?.id ? { userId: user.id } : "skip"
  );

  // Fetch user's LLM API keys to determine available models
  const userLLMKeys = useQuery(api.userLLMKeys.getUserLLMKeys,
    user?.id ? { userId: user.id } : "skip"
  );

  // Get available models based on active API keys
  const getAvailableModels = () => {
    if (!userLLMKeys) return [];

    const models: { provider: string; models: Array<{ id: string; name: string }> }[] = [];

    // Check for active keys and add corresponding models
    const activeKeys = userLLMKeys.filter(key => key.isActive);

    activeKeys.forEach(key => {
      if (key.provider === 'anthropic') {
        models.push({
          provider: 'Anthropic',
          models: [
            { id: 'anthropic/claude-sonnet-4-5-20250929', name: 'Claude Sonnet 4.5' },
            { id: 'anthropic/claude-haiku-4-5-20251001', name: 'Claude Haiku 4.5' },
          ]
        });
      } else if (key.provider === 'openai') {
        models.push({
          provider: 'OpenAI',
          models: [
            { id: 'openai/gpt-4o', name: 'GPT-5' },
            { id: 'openai/gpt-4o-mini', name: 'GPT-5 Mini' },
          ]
        });
      } else if (key.provider === 'groq') {
        models.push({
          provider: 'Groq',
          models: [
            { id: 'groq/openai/gpt-oss-120b', name: 'GPT OSS 120B' },
          ]
        });
      }
    });

    return models;
  };

  // Helper to update JSON schema from fields array
  const updateSchemaFromFields = (
    fields: Array<{ name: string; type: string; required: boolean }>,
  ) => {
    const properties: any = {};
    const required: string[] = [];

    fields.forEach((field) => {
      if (field.name) {
        properties[field.name] = { type: field.type };
        if (field.required) {
          required.push(field.name);
        }
      }
    });

    const schema: any = {
      type: "object",
      properties,
    };

    if (required.length > 0) {
      schema.required = required;
    }

    setJsonOutputSchema(JSON.stringify(schema, null, 2));
  };

  // Track current node's MCP server IDs
  useEffect(() => {
    if (nodeData && nodes) {
      const actualNode = nodes.find((n) => n.id === nodeData.id);
      if (actualNode) {
        const data = actualNode.data as any;

        // If we already have server IDs, use them
        if (data.mcpServerIds && Array.isArray(data.mcpServerIds) && data.mcpServerIds.length > 0) {
          setCurrentMCPServerIds(data.mcpServerIds);
        }
        // If we have mcpTools but no server IDs, try to match them
        else if (data.mcpTools && Array.isArray(data.mcpTools) && mcpServers && mcpServers.length > 0) {
          console.log('🔄 Re-matching mcpTools after servers loaded');
          const mcpIds = data.mcpTools
            .map((tool: any) => {
              const normalizeUrl = (url: string) =>
                url?.replace(/\{[^}]+\}/g, '').replace(/\/+$/, '').toLowerCase();

              const matchingServer = mcpServers.find(
                (server: any) => {
                  const toolUrlNormalized = normalizeUrl(tool.url || '');
                  const serverUrlNormalized = normalizeUrl(server.url || '');

                  const urlMatch = toolUrlNormalized === serverUrlNormalized ||
                    (toolUrlNormalized && serverUrlNormalized &&
                     (toolUrlNormalized.includes(serverUrlNormalized) ||
                      serverUrlNormalized.includes(toolUrlNormalized)));

                  const nameMatch = server.name?.toLowerCase() === tool.name?.toLowerCase() ||
                    server.label?.toLowerCase() === tool.label?.toLowerCase();

                  return urlMatch || nameMatch;
                }
              );
              return matchingServer?._id;
            })
            .filter(Boolean);

          if (mcpIds.length > 0) {
            console.log('✅ Matched server IDs:', mcpIds);
            setCurrentMCPServerIds(mcpIds);
          }
        }
      }
    }
  }, [nodeData?.id, nodes, mcpServers]);

  // Initialize from nodeData if available
  const [name, setName] = useState(nodeData?.label || "My agent");
  const [instructions, setInstructions] = useState((nodeData as any)?.instructions || "");
  const [includeChatHistory, setIncludeChatHistory] = useState(true);
  const [model, setModel] = useState("anthropic/claude-sonnet-4-5-20250929");
  const [outputFormat, setOutputFormat] = useState("Text");
  const [customModel, setCustomModel] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showSearchSources, setShowSearchSources] = useState(false);
  const [jsonOutputSchema, setJsonOutputSchema] = useState(`{
  "type": "object",
  "properties": {
    "result": { "type": "string" }
  }
}`);
  const [schemaFields, setSchemaFields] = useState<
    Array<{ name: string; type: string; required: boolean }>
  >([{ name: "result", type: "string", required: false }]);
  const lastLoadedNodeId = useRef<string | null>(null);
  const lastSyncedInstructionsRef = useRef<string | null>(null);

  // Load actual node data when panel opens
  useEffect(() => {
    if (!nodeData || !nodes) return;

    const actualNode = nodes.find((n) => n.id === nodeData.id);
    if (!actualNode) return;

    const data = actualNode.data as any;
    const isNewNode = lastLoadedNodeId.current !== nodeData.id;
    const incomingInstructions =
      typeof data.instructions === "string" ? data.instructions : "";

    if (isNewNode) {
      lastLoadedNodeId.current = nodeData.id;
      setName(data.name || data.nodeName || nodeData.label);
      setInstructions(incomingInstructions);
      setIncludeChatHistory(data.includeChatHistory ?? true);
      setModel(data.model || "anthropic/claude-sonnet-4-5-20250929");
      setOutputFormat(data.outputFormat || "Text");
      setShowSearchSources(data.showSearchSources ?? false);
      lastSyncedInstructionsRef.current = incomingInstructions;

      // Initialize MCP servers from node data
      if (data.mcpServerIds && Array.isArray(data.mcpServerIds)) {
        // If node already has server IDs, use them directly
        setCurrentMCPServerIds(data.mcpServerIds);
      } else if (data.mcpTools && Array.isArray(data.mcpTools)) {
        // Convert mcpTools to server IDs by matching against available MCP servers
        if (mcpServers && mcpServers.length > 0) {
          console.log('🔍 Matching mcpTools from template:', data.mcpTools);
          console.log('🔍 Available MCP servers:', mcpServers.map((s: any) => ({ name: s.name, url: s.url })));

          const mcpIds = data.mcpTools
            .map((tool: any) => {
              // Try to find matching MCP server by URL or name
              const matchingServer = mcpServers.find(
                (server: any) => {
                  // Normalize URLs by removing placeholders for comparison
                  const normalizeUrl = (url: string) =>
                    url?.replace(/\{[^}]+\}/g, '').replace(/\/+$/, '').toLowerCase();

                  const toolUrlNormalized = normalizeUrl(tool.url || '');
                  const serverUrlNormalized = normalizeUrl(server.url || '');

                  // Match by URL (exact match after normalization)
                  const urlMatch = toolUrlNormalized === serverUrlNormalized ||
                    (toolUrlNormalized && serverUrlNormalized &&
                     toolUrlNormalized.includes(serverUrlNormalized.split('/')[0]) ||
                     serverUrlNormalized.includes(toolUrlNormalized.split('/')[0]));

                  // Match by name (case-insensitive)
                  const nameMatch = server.name?.toLowerCase() === tool.name?.toLowerCase() ||
                    server.label?.toLowerCase() === tool.label?.toLowerCase() ||
                    server.name?.toLowerCase() === tool.label?.toLowerCase();

                  if (urlMatch || nameMatch) {
                    console.log('✅ Matched tool', tool.name, 'to server', server.name);
                  }

                  return urlMatch || nameMatch;
                }
              );
              return matchingServer?._id;
            })
            .filter(Boolean);

          console.log('🎯 Matched MCP server IDs:', mcpIds);

          if (mcpIds.length > 0) {
            setCurrentMCPServerIds(mcpIds);
          }
        }
      }
      if (data.jsonOutputSchema) {
        setJsonOutputSchema(data.jsonOutputSchema);
        try {
          const parsed = JSON.parse(data.jsonOutputSchema);
          if (parsed.properties) {
            const fields = Object.entries(parsed.properties).map(
              ([propName, prop]: [string, any]) => ({
                name: propName,
                type: prop.type || "string",
                required: parsed.required?.includes(propName) || false,
              }),
            );
            setSchemaFields(fields);
          }
        } catch (e) {
          // ignore parse errors
        }
      }
      return;
    }

    if (isNewNode) {
      lastLoadedNodeId.current = nodeData.id;
    }

    if (incomingInstructions !== lastSyncedInstructionsRef.current) {
      lastSyncedInstructionsRef.current = incomingInstructions;
      if (incomingInstructions !== instructions) {
        setInstructions(incomingInstructions);
      }
    } else if (
      incomingInstructions === instructions &&
      incomingInstructions !== lastSyncedInstructionsRef.current
    ) {
      lastSyncedInstructionsRef.current = incomingInstructions;
    }
  }, [nodeData, nodes, instructions, mcpServers]);

  // Auto-save changes with proper dependency tracking
  useEffect(() => {
    if (!nodeData?.id) return;

    const timeoutId = setTimeout(() => {
      try {
        // Build mcpTools from currentMCPServerIds
        const mcpTools = currentMCPServerIds
          .map((serverId: string) => {
            const server = mcpServers?.find((s: any) => s._id === serverId);
            if (server) {
              return {
                id: server._id,
                name: server.name,
                url: server.url,
                label: server.label || server.name,
                authType: server.authType,
              };
            }
            return null;
          })
          .filter(Boolean);

        onUpdate(nodeData.id, {
          name,
          nodeName: name,
          instructions,
          includeChatHistory,
          model,
          outputFormat,
          jsonOutputSchema:
            outputFormat === "JSON" ? jsonOutputSchema : undefined,
          showSearchSources,
          mcpTools: mcpTools.length > 0 ? mcpTools : undefined,
          mcpServerIds: currentMCPServerIds.length > 0 ? currentMCPServerIds : undefined,
        });
      } catch (error) {
        console.error("Error updating node:", error);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [
    name,
    instructions,
    includeChatHistory,
    model,
    outputFormat,
    jsonOutputSchema,
    showSearchSources,
    currentMCPServerIds,
    mcpServers,
  ]);

  return (
    <AnimatePresence>
      {nodeData && (
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
                className="text-label-large font-medium text-accent-black bg-transparent border-none outline-none focus:outline-none hover:bg-black-alpha-4 px-2 -ml-2 rounded-4 transition-colors"
                placeholder="Enter node name..."
              />
              <div className="flex items-center gap-8">
                <button className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center">
                  <svg
                    className="w-18 h-18 text-black-alpha-48"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </button>
                <button
                  onClick={() => onDelete(nodeData?.id || "")}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center group"
                  title="Delete node"
                >
                  <svg
                    className="w-18 h-18 text-black-alpha-48 group-hover:text-black-alpha-64"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
                <button
                  onClick={onClose}
                  className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                >
                  <svg
                    className="w-18 h-18 text-black-alpha-48"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
            <p className="text-sm text-black-alpha-48">
              Call the model with your instructions and tools
            </p>
          </div>

          {/* Form Fields */}
          <div className="p-20 space-y-20">

            {/* Instructions Field */}
            <div>
              <div className="flex items-center justify-between mb-8">
                <label className="block text-sm font-medium text-black-alpha-48">
                  Instructions
                </label>
                <div className="flex items-center gap-8">
                  {nodes && (
                    <VariableReferencePicker
                      nodes={nodes}
                      currentNodeId={nodeData?.id || ""}
                      onSelect={(ref) =>
                        setInstructions(instructions + ` {{${ref}}}`)
                      }
                    />
                  )}
                </div>
              </div>
              <textarea
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="Enter agent instructions..."
                rows={8}
                className="w-full px-14 py-10 bg-background-base border border-border-faint rounded-10 text-sm text-accent-black placeholder-black-alpha-32 focus:outline-none focus:border-heat-100 transition-colors resize-y"
              />
              <p className="text-xs text-black-alpha-48 mt-6">
                Use <code className="px-4 py-1 bg-background-base rounded text-heat-100 font-mono text-xs">{`{{variable}}`}</code> syntax to reference data
              </p>
            </div>

            {/* Include chat history toggle */}
            <div className="flex items-center justify-between py-8">
              <label className="text-sm font-medium text-accent-black">
                Include chat history
              </label>
              <button
                onClick={() => setIncludeChatHistory(!includeChatHistory)}
                className={`w-48 h-28 rounded-full transition-colors relative ${
                  includeChatHistory ? "bg-heat-100" : "bg-black-alpha-12"
                }`}
              >
                <motion.div
                  className="w-24 h-24 bg-white rounded-full absolute top-2 shadow-sm"
                  animate={{ left: includeChatHistory ? "22px" : "2px" }}
                  transition={{ duration: 0.2 }}
                />
              </button>
            </div>

            {/* Model Field */}
            <div>
              <label className="block text-sm font-medium text-black-alpha-48 mb-8">
                Model
              </label>
              <button
                onClick={() => setShowModelsDropdown(!showModelsDropdown)}
                className="w-full px-14 py-10 bg-background-base border border-border-faint rounded-10 text-sm text-accent-black focus:outline-none focus:border-heat-100 transition-colors flex items-center justify-between hover:bg-black-alpha-4"
              >
                <span className="truncate">
                  {model ? (
                    // Find the display name for the selected model
                    getAvailableModels().flatMap(p => p.models).find(m => m.id === model)?.name ||
                    model
                  ) : (
                    <span className="text-black-alpha-32">Select a model...</span>
                  )}
                </span>
                <ChevronDown
                  className={`w-16 h-16 text-black-alpha-48 transition-transform ${
                    showModelsDropdown ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {showModelsDropdown && (
                <div className="mt-8 p-8 bg-background-base border border-border-faint rounded-10 space-y-8 max-h-[300px] overflow-y-auto">
                  {getAvailableModels().length === 0 ? (
                    <div className="p-16 text-center">
                      <p className="text-sm text-black-alpha-48 mb-12">
                        No API keys configured
                      </p>
                      <button
                        onClick={() => {
                          setShowModelsDropdown(false);
                          onOpenSettings?.();
                        }}
                        className="px-12 py-6 bg-heat-100 text-white rounded-8 text-sm hover:bg-heat-120 transition-colors"
                      >
                        Add API Keys
                      </button>
                    </div>
                  ) : (
                    <>
                      {getAvailableModels().map((provider) => (
                        <div key={provider.provider}>
                          <div className="text-xs font-medium text-black-alpha-48 mb-4">
                            {provider.provider}
                          </div>
                          {provider.models.map((modelOption) => (
                            <button
                              key={modelOption.id}
                              onClick={() => {
                                setModel(modelOption.id);
                                setShowModelsDropdown(false);
                              }}
                              className={`w-full text-left px-8 py-6 rounded-6 text-sm transition-colors ${
                                model === modelOption.id
                                  ? 'bg-heat-100 text-white'
                                  : 'hover:bg-black-alpha-4 text-accent-black'
                              }`}
                            >
                              {modelOption.name}
                            </button>
                          ))}
                        </div>
                      ))}
                      <div className="pt-8 mt-8 border-t border-border-faint">
                        <button
                          onClick={() => {
                            setModel("custom");
                            setShowModelsDropdown(false);
                          }}
                          className={`w-full text-left px-8 py-6 rounded-6 text-sm transition-colors ${
                            model === "custom"
                              ? 'bg-heat-100 text-white'
                              : 'hover:bg-black-alpha-4 text-accent-black'
                          }`}
                        >
                          Custom Model...
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}

              {model === "custom" && (
                <input
                  type="text"
                  value={customModel}
                  onChange={(e) => {
                    setCustomModel(e.target.value);
                    setModel(e.target.value);
                  }}
                  placeholder="provider/model-name"
                  className="w-full px-14 py-10 bg-background-base border border-border-faint rounded-10 text-sm text-accent-black placeholder-black-alpha-32 font-mono focus:outline-none focus:border-heat-100 transition-colors mt-8"
                />
              )}
            </div>

            {/* MCP Tools Field */}
            <div>
              <div className="flex items-center justify-between mb-8">
                <label className="block text-sm font-medium text-black-alpha-48">
                  Tools
                </label>
                <div className="flex items-center gap-8">
                  <button
                    onClick={() => {
                      setShowMCPSelector((prev) => {
                        const next = !prev;
                        if (next) {
                          // Expand first server if available
                          if (mcpServers && mcpServers.length > 0) {
                            setExpandedMcpId(mcpServers[0]._id);
                          } else {
                            setExpandedMcpId("custom");
                          }
                        } else {
                          setExpandedMcpId(null);
                        }
                        return next;
                      });
                    }}
                    className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                    title="Add MCP tools"
                  >
                    <svg
                      className="w-18 h-18 text-black-alpha-48"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                  </button>
                  {onOpenSettings && (
                    <button
                      onClick={onOpenSettings}
                      className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                      title="Configure MCPs in Settings"
                    >
                      <svg
                        className="w-18 h-18 text-black-alpha-48"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              {/* MCP Selector Modal */}
              {showMCPSelector && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mb-12 p-16 bg-[#f4f4f5] rounded-12 border border-border-faint"
                >
                  <div className="flex items-center justify-between mb-12">
                    <h4 className="text-sm font-semibold text-accent-black">
                      MCP Registry
                    </h4>
                    <button
                      onClick={() => {
                        setShowMCPSelector(false);
                        setExpandedMcpId(null);
                      }}
                      className="w-20 h-20 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                    >
                      <svg
                        className="w-14 h-14 text-black-alpha-48"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>
                  <div className="space-y-12">
                    {!mcpServers || mcpServers.length === 0 ? (
                      <div className="text-center py-16">
                        <p className="text-xs text-black-alpha-48 mb-8">
                          {/* No MCP servers configured in your registry. */}
                          Need to add a new MCP server?
                        </p>
                        <button 
                          onClick={() => {
                            setShowMCPSelector(true);
                          }}
                          className="text-xs text-heat-100 hover:text-heat-200 font-medium"
                        >
                          Go to <a href="https://composio.dev" target="_blank" rel="noopener noreferrer" className="underline text-heat-100 hover:text-heat-200 font-medium">Composio↗</a>→ MCP Configs
                        </button>
                      </div>
                    ) : (
                      mcpServers.map((server: any) => {
                        const isConnected = currentMCPServerIds.includes(server._id);
                        const isExpanded = expandedMcpId === server._id;
                        const isFirecrawl = server.name === 'Firecrawl' && server.isOfficial;

                        return (
                          <div key={server._id} className="rounded-12 border border-border-faint overflow-hidden bg-accent-white">
                            <button
                              onClick={() => setExpandedMcpId(isExpanded ? null : server._id)}
                              className="w-full px-16 py-12 flex items-center justify-between text-left hover:bg-black-alpha-4 transition-colors"
                            >
                              <div className="flex items-center gap-8">
                                <span className="text-sm font-medium text-accent-black">{server.name}</span>
                                {isFirecrawl && (
                                  <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-6 text-xs border border-heat-100 font-medium">
                                    API Key Required
                                  </span>
                                )}
                                {server.connectionStatus === 'connected' && (
                                  <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-6 text-xs border border-heat-100">
                                    Connected
                                  </span>
                                )}
                                {server.tools && (
                                  <span className="px-6 py-2 bg-background-base text-black-alpha-48 rounded-6 text-xs border border-border-faint">
                                    {server.tools.length} tools
                                  </span>
                                )}
                              </div>
                              <svg
                                className={`w-16 h-16 text-black-alpha-32 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </button>
                            {isExpanded && (
                              <div className="px-16 pb-16 space-y-10 bg-accent-white border-t border-border-faint">
                                {server.description && (
                                  <p className="pt-12 text-xs text-black-alpha-64">{server.description}</p>
                                )}
                                {isFirecrawl && (
                                  <a
                                    href="https://www.firecrawl.dev/app/api-keys"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-heat-100 hover:text-heat-200 underline block -mt-6"
                                  >
                                    Get API key here →
                                  </a>
                                )}
                                {server.tools && server.tools.length > 0 && (
                                  <div className="space-y-6">
                                    <p className="text-xs text-black-alpha-64 font-medium">Available Tools:</p>
                                    <div className="flex flex-wrap gap-4">
                                      {server.tools.map((tool: string) => (
                                        <span key={tool} className="px-6 py-2 bg-background-base text-black-alpha-64 rounded-4 text-xs border border-border-faint">
                                          {tool}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                <div className="flex items-center justify-end pt-8">
                                  <button
                                    onClick={() => {
                                      if (isConnected) {
                                        const newServerIds = currentMCPServerIds.filter(id => id !== server._id);
                                        onUpdate(nodeData?.id || '', { mcpServerIds: newServerIds });
                                        setCurrentMCPServerIds(newServerIds);
                                        toast.success(`Removed ${server.name}`);
                                      } else {
                                        const newServerIds = [...currentMCPServerIds, server._id];
                                        onUpdate(nodeData?.id || '', { mcpServerIds: newServerIds });
                                        setCurrentMCPServerIds(newServerIds);
                                        toast.success(`Added ${server.name} to this agent`);
                                      }
                                    }}
                                    className={`px-12 py-8 rounded-8 text-xs font-medium transition-colors ${
                                      isConnected
                                        ? 'bg-accent-white border border-border-faint text-accent-black hover:bg-black-alpha-4'
                                        : 'bg-heat-100 text-white hover:bg-heat-200'
                                    }`}
                                  >
                                    {isConnected ? 'Remove' : 'Add'}
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })
                    )}
                    <div className="rounded-12 border border-border-faint overflow-hidden bg-accent-white">
                      <button
                        onClick={() => setExpandedMcpId(expandedMcpId === 'custom' ? null : 'custom')}
                        className="w-full px-16 py-12 flex items-center justify-between text-left hover:bg-black-alpha-4 transition-colors"
                      >
                        <div className="flex items-center gap-8">
                          <span className="text-sm font-medium text-accent-black">Add New MCP Server</span>
                          <span className="px-6 py-2 bg-heat-4 text-heat-100 rounded-6 text-xs border border-heat-100">
                            Settings
                          </span>
                        </div>
                        <svg
                          className={`w-16 h-16 text-black-alpha-32 transition-transform ${expandedMcpId === 'custom' ? 'rotate-180' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      {expandedMcpId === 'custom' && (
                        <div className="px-16 pb-16 space-y-10 bg-[#f4f4f5]">
                          <p className="text-xs text-black-alpha-48">
                            Add new MCP servers from Composio to your registry in Settings. Once added, they'll appear here for all your agents to use.
                          </p>
                          <button
                            onClick={() => {
                              setShowMCPSelector(false);
                              setExpandedMcpId(null);
                              onOpenSettings?.();
                            }}
                            className="px-16 py-10 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-xs font-medium transition-colors"
                          >
                            Go to Settings
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Show connected MCP servers */}
              {currentMCPServerIds && currentMCPServerIds.length > 0 && mcpServers ? (
                <div className="space-y-8">
                  {currentMCPServerIds.map((serverId: string) => {
                    const server = mcpServers.find((s: any) => s._id === serverId);
                    if (!server) return null;
                    return (
                      <div
                        key={serverId}
                        className="px-14 py-10 bg-background-base rounded-10 border border-border-faint flex items-center justify-between group hover:border-heat-100 transition-colors"
                      >
                        <div className="flex items-center gap-8">
                          <span className="text-sm text-accent-black font-mono">
                            {server.name}
                          </span>
                          {server.tools && (
                            <span className="text-xs text-black-alpha-48">
                              {server.tools.length} tools
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => {
                            const newServerIds = currentMCPServerIds.filter(id => id !== serverId);
                            onUpdate(nodeData?.id || "", { mcpServerIds: newServerIds });
                            setCurrentMCPServerIds(newServerIds);
                          }}
                          className="w-20 h-20 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100"
                        >
                          <svg
                            className="w-14 h-14 text-black-alpha-48 hover:text-black-alpha-64"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-16 bg-background-base rounded-10 border border-border-faint text-center">
                  <p className="text-sm text-black-alpha-48">No MCP servers connected</p>
                </div>
              )}
            </div>

            {/* Output Format Field */}
            <div>
              <label className="block text-sm font-medium text-black-alpha-48 mb-8">
                Output format
              </label>
              <select
                value={outputFormat}
                onChange={(e) => setOutputFormat(e.target.value)}
                className="w-full px-14 py-10 bg-background-base border border-border-faint rounded-10 text-sm text-accent-black focus:outline-none focus:border-heat-100 transition-colors appearance-none cursor-pointer"
              >
                <option value="Text">Text</option>
                <option value="JSON">JSON</option>
              </select>
            </div>

            {/* JSON Output Schema - Show when JSON format selected */}
            {outputFormat === "JSON" && (
              <div>
                <div className="flex items-center justify-between mb-12">
                  <label className="block text-sm font-medium text-black-alpha-48">
                    Output Schema Builder
                  </label>
                  <button
                    onClick={() => {
                      const newField = {
                        name: "",
                        type: "string",
                        required: false,
                      };
                      const updated = [...schemaFields, newField];
                      setSchemaFields(updated);
                    }}
                    className="px-10 py-6 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-xs font-medium transition-colors flex items-center gap-4"
                  >
                    <svg
                      className="w-12 h-12"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                    Add Field
                  </button>
                </div>

                {/* Visual Schema Builder */}
                <div className="space-y-8 mb-12">
                  {schemaFields.length === 0 ? (
                    <div className="p-16 bg-background-base rounded-10 border border-border-faint text-center">
                      <p className="text-sm text-black-alpha-48">
                        No fields added yet
                      </p>
                      <p className="text-xs text-black-alpha-32 mt-4">
                        Click "Add Field" to start building your schema
                      </p>
                    </div>
                  ) : (
                    <div className="p-12 bg-background-base rounded-10 border border-border-faint space-y-10">
                      {schemaFields.map((field, index) => (
                        <div
                          key={`field-${index}-${field.name}`}
                          className="flex items-center gap-8"
                        >
                          <input
                            type="text"
                            value={field.name}
                            onChange={(e) => {
                              const updated = [...schemaFields];
                              updated[index].name = e.target.value;
                              setSchemaFields(updated);
                              updateSchemaFromFields(updated);
                            }}
                            placeholder="Field name"
                            className="flex-1 px-10 py-6 bg-accent-white border border-border-faint rounded-6 text-sm text-accent-black placeholder-black-alpha-32 focus:outline-none focus:border-heat-100"
                          />
                          <select
                            value={field.type}
                            onChange={(e) => {
                              const updated = [...schemaFields];
                              updated[index].type = e.target.value;
                              setSchemaFields(updated);
                              updateSchemaFromFields(updated);
                            }}
                            className="px-10 py-6 bg-accent-white border border-border-faint rounded-6 text-sm text-accent-black focus:outline-none focus:border-heat-100"
                          >
                            <option value="string">string</option>
                            <option value="number">number</option>
                            <option value="boolean">boolean</option>
                            <option value="array">array</option>
                            <option value="object">object</option>
                          </select>
                          <button
                            onClick={() => {
                              const updated = schemaFields.filter(
                                (_, i) => i !== index,
                              );
                              setSchemaFields(updated);
                              updateSchemaFromFields(updated);
                            }}
                            className="w-24 h-24 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
                          >
                            <svg
                              className="w-14 h-14 text-black-alpha-48"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                              />
                            </svg>
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Raw JSON View Toggle */}
                <details className="group">
                  <summary className="cursor-pointer text-xs text-heat-100 hover:text-heat-200 transition-colors flex items-center gap-4 mb-8">
                    <span>View Raw JSON</span>
                    <svg
                      className="w-12 h-12 transition-transform group-open:rotate-180"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </summary>
                  <textarea
                    value={jsonOutputSchema}
                    onChange={(e) => setJsonOutputSchema(e.target.value)}
                    rows={6}
                    placeholder='{"type": "object", "properties": {...}}'
                    className="w-full px-14 py-10 bg-gray-900 text-heat-100 border border-border-faint rounded-10 text-xs font-mono focus:outline-none focus:border-heat-100 transition-colors resize-y"
                  />
                </details>
              </div>
            )}

            {/* Advanced Settings */}
            <details className="group" open={showAdvanced}>
              <summary
                onClick={(e) => {
                  e.preventDefault();
                  setShowAdvanced(!showAdvanced);
                }}
                className="flex items-center justify-between cursor-pointer list-none text-sm font-medium text-black-alpha-48 hover:text-accent-black transition-colors py-12"
              >
                <span>Advanced</span>
                <svg
                  className={`w-16 h-16 transition-transform ${showAdvanced ? "rotate-180" : ""}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>

              {showAdvanced && (
                <div className="space-y-16 pt-16 border-t border-border-faint">
                  {/* Advanced settings section - reserved for future options */}
                </div>
              )}
            </details>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
