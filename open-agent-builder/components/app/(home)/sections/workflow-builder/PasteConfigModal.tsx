"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { AlertCircle, Loader2, ExternalLink } from "lucide-react";
import { toast } from "sonner";

interface PasteConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (servers: any[]) => Promise<void>;
}

export default function PasteConfigModal({ isOpen, onClose, onSave }: PasteConfigModalProps) {
  const [configJSON, setConfigJSON] = useState('');
  const [parsing, setParsing] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const parseAndSave = async () => {
    setParsing(true);
    setError('');

    try {
      // Parse the JSON
      const config = JSON.parse(configJSON);

      // Extract MCP servers from Cursor/Cline format
      const servers: any[] = [];

      if (config.mcpServers) {
        for (const [serverName, serverConfig] of Object.entries(config.mcpServers)) {
          const typedConfig = serverConfig as any;

          // Determine the server type and URL
          let name = serverName;
          let url = '';
          let category = 'custom';
          let authType = 'none';
          let accessToken = '';
          let description = '';
          let headers: any = null;

          // Check if it's a direct URL configuration (like Context7)
          if (typedConfig.url) {
            url = typedConfig.url;

            // Handle headers-based authentication
            if (typedConfig.headers) {
              headers = typedConfig.headers;
              authType = 'api-key';

              // Extract API key from headers
              const headerKeys = Object.keys(typedConfig.headers);
              if (headerKeys.length > 0) {
                // Find the key that contains API_KEY
                const apiKeyHeader = headerKeys.find(key => key.includes('API_KEY')) || headerKeys[0];
                accessToken = typedConfig.headers[apiKeyHeader];
              }
            }

            // Identify known services by URL or name
            if (serverName.includes('context7') || url.includes('context7')) {
              name = 'Context7';
              category = 'ai';
              description = 'Documentation and code assistance';
            } else if (serverName.includes('firecrawl') || url.includes('firecrawl')) {
              name = 'Firecrawl';
              category = 'web';
              description = 'Web scraping, searching, and data extraction';
            }

          } else if (typedConfig.command === 'npx' && typedConfig.args) {
            // Handle npx-style configurations (Firecrawl, etc.)
            const packageName = typedConfig.args.find((arg: string) => arg !== '-y' && !arg.startsWith('-'));

            // Identify known MCPs
            if (packageName === 'firecrawl-mcp' || serverName.includes('firecrawl')) {
              name = 'Firecrawl';
              category = 'web';
              authType = 'api-key';
              description = 'Web scraping, searching, and data extraction';

              // Extract API key from env
              if (typedConfig.env?.FIRECRAWL_API_KEY) {
                accessToken = typedConfig.env.FIRECRAWL_API_KEY;
                url = `https://mcp.firecrawl.dev/${accessToken}/v2/mcp`;
              } else {
                url = 'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp';
              }
            } else {
              // Generic MCP server
              name = packageName || serverName;
              url = `npx -y ${packageName || serverName}`;

              // Check for API keys in env
              if (typedConfig.env) {
                const envKeys = Object.keys(typedConfig.env);
                if (envKeys.length > 0) {
                  authType = 'api-key';
                  // Take the first API key found
                  accessToken = typedConfig.env[envKeys[0]];
                }
              }
            }
          } else {
            // Unsupported format, skip
            console.warn(`Skipping unsupported MCP config format for ${serverName}`, typedConfig);
            continue;
          }

          servers.push({
            name: name.replace(/-mcp$/, '').replace(/mcp-/, '').replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
            url,
            description,
            category,
            authType,
            accessToken,
            headers,
            tools: [], // Will be discovered on test
          });
        }
      }

      if (servers.length === 0) {
        throw new Error('No MCP servers found in configuration');
      }

      // Save all servers (onSave will handle testing)
      await onSave(servers);

      // Don't show success here as onSave will show individual results
      onClose();
      setConfigJSON('');

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid JSON configuration');
    } finally {
      setParsing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black-alpha-16 backdrop-blur-sm flex items-center justify-center z-[100]"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-accent-white rounded-16 shadow-2xl max-w-2xl w-full mx-20 flex flex-col"
        style={{ maxHeight: '85vh' }}
      >
        {/* Header */}
        <div className="p-20 border-b border-border-faint flex-shrink-0">
          <div className="flex items-center justify-between">
            <h2 className="text-title-h4 text-accent-black">Paste MCP Configuration</h2>
            <button
              onClick={onClose}
              className="w-32 h-32 rounded-6 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
            >
              <svg className="w-16 h-16 text-black-alpha-48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-body-small text-black-alpha-48 mt-8">
            Paste your Cursor/Cline MCP configuration JSON below
          </p>
        </div>

        {/* Body */}
        <div className="p-20 space-y-16 overflow-y-auto flex-1">
          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="text-body-small text-black-alpha-64 block">
                Configuration JSON
              </label>
              <a
                href="https://www.firecrawl.dev/app"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-heat-100 hover:text-heat-200 underline flex items-center gap-4"
              >
                See example config
                <ExternalLink className="w-12 h-12" />
              </a>
            </div>
            <textarea
              value={configJSON}
              onChange={(e) => setConfigJSON(e.target.value)}
              placeholder={`// Example 1 - Direct URL format (Context7):
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "your-api-key"
      }
    }
  }
}

// Example 2 - NPX format (Firecrawl):
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-api-key"
      }
    }
  }
}`}
              className="w-full h-[300px] px-14 py-10 bg-background-base border border-border-faint rounded-10 text-sm text-accent-black font-mono focus:outline-none focus:border-heat-100 transition-colors resize-none"
              spellCheck={false}
            />
          </div>

          {error && (
            <div className="p-12 bg-accent-black text-white rounded-8">
              <p className="text-body-small">{error}</p>
            </div>
          )}

          <div className="p-12 bg-heat-4 rounded-8 border border-heat-100">
            <div className="flex items-start gap-8">
              <AlertCircle className="w-16 h-16 text-heat-100 flex-shrink-0 mt-1" />
              <div>
                <p className="text-body-small text-accent-black font-medium mb-4">
                  Supported Formats
                </p>
                <p className="text-body-small text-black-alpha-64 mb-6">
                  Supports two formats:
                  <br />• Direct URL with headers (Context7, etc.)
                  <br />• NPX command format (Firecrawl, Cursor, Cline)
                  <br />
                  <br />Connections will be tested automatically after import.
                </p>
                <p className="text-xs text-black-alpha-48">
                  💡 Tip: Copy your MCP config from your editor's settings.json file
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-20 border-t border-border-faint flex gap-8 flex-shrink-0">
          <button
            onClick={onClose}
            className="flex-1 px-20 py-12 bg-black-alpha-4 hover:bg-black-alpha-8 text-accent-black rounded-8 text-body-medium font-medium transition-all"
          >
            Cancel
          </button>
          <button
            onClick={parseAndSave}
            disabled={!configJSON.trim() || parsing}
            className="flex-1 px-20 py-12 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-body-medium font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-6"
          >
            {parsing ? (
              <>
                <Loader2 className="w-16 h-16 animate-spin" />
                Importing & Testing...
              </>
            ) : (
              'Import & Test'
            )}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}