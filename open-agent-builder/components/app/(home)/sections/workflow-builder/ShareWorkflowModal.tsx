"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { toast } from "sonner";

interface ShareWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  workflowId: string;
  workflowName: string;
}

export default function ShareWorkflowModal({ isOpen, onClose, workflowId, workflowName }: ShareWorkflowModalProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const baseUrl = typeof window !== 'undefined'
    ? window.location.origin
    : 'http://localhost:3000';

  const executeUrl = `${baseUrl}/api/workflows/${workflowId}/execute`;
  const streamUrl = `${baseUrl}/api/workflows/${workflowId}/execute-stream`;

  const curlExample = `curl -X POST ${executeUrl} \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}'`;

  const curlStreamExample = `curl -X POST ${streamUrl} \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}' \\
  --no-buffer`;

  const fetchExample = `// JavaScript/TypeScript
const response = await fetch('${executeUrl}', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' }),
});

const result = await response.json();
console.log(result);`;

  const fetchStreamExample = `// JavaScript/TypeScript - Streaming
const response = await fetch('${streamUrl}', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' }),
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const events = chunk.split('\\n\\n');

  for (const event of events) {
    if (event.startsWith('data: ')) {
      const data = JSON.parse(event.slice(6));
      console.log('Update:', data);
    }
  }
}`;

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(null), 2000);
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
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-[200]"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 m-auto w-full max-w-3xl h-fit bg-accent-white rounded-16 border border-border-faint shadow-2xl z-[201] max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="p-24 border-b border-border-faint sticky top-0 bg-accent-white rounded-t-16">
              <div className="flex items-center justify-between mb-12">
                <div>
                  <h2 className="text-title-h3 text-accent-black mb-4">Workflow Saved!</h2>
                  <p className="text-body-medium text-black-alpha-48">
                    Your workflow is ready to use via API
                  </p>
                </div>
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

            {/* Content */}
            <div className="p-24 space-y-20">
              {/* URLs Section */}
              <div className="space-y-16">
                <div>
                  <div className="flex items-center justify-between mb-8">
                    <label className="text-label-medium text-accent-black font-medium">
                      Standard Execution
                    </label>
                    <button
                      onClick={() => handleCopy(executeUrl, 'url')}
                      className="px-12 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-6 text-body-small transition-colors"
                    >
                      {copied === 'url' ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <input
                    type="text"
                    value={executeUrl}
                    readOnly
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-mono"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-8">
                    <label className="text-label-medium text-accent-black font-medium">
                      Streaming Execution
                    </label>
                    <button
                      onClick={() => handleCopy(streamUrl, 'stream-url')}
                      className="px-12 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-6 text-body-small transition-colors"
                    >
                      {copied === 'stream-url' ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <input
                    type="text"
                    value={streamUrl}
                    readOnly
                    className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-mono"
                  />
                  <p className="text-body-small text-black-alpha-48 mt-6">Real-time updates as each node executes</p>
                </div>
              </div>

              <div className="border-t border-border-faint my-20"></div>

              {/* Code Examples */}
              <div className="space-y-16">
                <h3 className="text-label-large text-accent-black font-medium">Code Examples</h3>

                {/* cURL */}
                <div>
                  <div className="flex items-center justify-between mb-8">
                    <label className="text-body-medium text-accent-black">
                      cURL
                    </label>
                    <button
                      onClick={() => handleCopy(curlExample, 'curl')}
                      className="px-12 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-6 text-body-small transition-colors"
                    >
                      {copied === 'curl' ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <pre className="p-16 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-mono overflow-x-auto">
{curlExample}
                  </pre>
                </div>

                {/* JavaScript */}
                <div>
                  <div className="flex items-center justify-between mb-8">
                    <label className="text-body-medium text-accent-black">
                      JavaScript/TypeScript
                    </label>
                    <button
                      onClick={() => handleCopy(fetchExample, 'fetch')}
                      className="px-12 py-6 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-6 text-body-small transition-colors"
                    >
                      {copied === 'fetch' ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <pre className="p-16 bg-background-base border border-border-faint rounded-8 text-body-small text-accent-black font-mono overflow-x-auto whitespace-pre-wrap">
{fetchExample}
                  </pre>
                </div>

                {/* Streaming Info */}
                <div className="p-16 bg-background-base rounded-12 border border-border-faint">
                  <div className="flex items-center gap-8 mb-8">
                    <div className="w-6 h-6 bg-heat-100 rounded-full"></div>
                    <p className="text-label-small text-accent-black font-medium">Streaming Available</p>
                  </div>
                  <p className="text-body-small text-black-alpha-48 mb-12">
                    Use <code className="px-6 py-2 bg-white rounded-4 text-accent-black font-mono text-xs">execute-stream</code> endpoint for real-time updates
                  </p>
                  <div className="space-y-4 text-body-small text-black-alpha-48">
                    <div className="flex items-center gap-8">
                      <code className="px-6 py-2 bg-white rounded-4 text-accent-black font-mono text-xs">node_started</code>
                      <span>Node begins</span>
                    </div>
                    <div className="flex items-center gap-8">
                      <code className="px-6 py-2 bg-white rounded-4 text-accent-black font-mono text-xs">node_completed</code>
                      <span>Node finishes</span>
                    </div>
                    <div className="flex items-center gap-8">
                      <code className="px-6 py-2 bg-white rounded-4 text-accent-black font-mono text-xs">workflow_completed</code>
                      <span>All done</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 p-20 bg-accent-white border-t border-border-faint rounded-b-16">
              <button
                onClick={onClose}
                className="w-full px-20 py-12 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-body-medium font-medium transition-all active:scale-[0.98]"
              >
                Done
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
