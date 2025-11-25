import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

/**
 * Convex Schema for Open Agent Builder
 *
 * Replaces Upstash Redis for workflow storage
 */

export default defineSchema({
  // Users table - synced from Clerk
  users: defineTable({
    clerkId: v.string(),
    email: v.optional(v.string()),
    name: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    createdAt: v.string(),
  })
    .index("by_clerkId", ["clerkId"])
    .index("by_email", ["email"]),

  // Workflows table - stores complete workflow definitions
  workflows: defineTable({
    // User ownership
    userId: v.optional(v.string()), // Clerk user ID - optional for backward compat

    // Workflow identification
    customId: v.optional(v.string()), // Original workflow ID (like "workflow_123" or "amazon-product-research")
    name: v.string(),
    description: v.optional(v.string()),
    category: v.optional(v.string()),
    tags: v.optional(v.array(v.string())),
    difficulty: v.optional(v.string()),
    estimatedTime: v.optional(v.string()),

    // Workflow structure
    nodes: v.array(v.any()), // Workflow nodes with flexible structure
    edges: v.array(v.any()), // Workflow edges

    // Timestamps
    createdAt: v.string(),
    updatedAt: v.string(),

    // Optional metadata
    version: v.optional(v.string()),
    isTemplate: v.optional(v.boolean()),
    isPublic: v.optional(v.boolean()), // For shared templates
  })
    .index("by_userId", ["userId"])
    .index("by_customId", ["customId"])
    .index("by_creation", ["createdAt"])
    .index("by_category", ["category"])
    .index("by_template", ["isTemplate"]),

  // Workflow executions - track execution state
  executions: defineTable({
    workflowId: v.id("workflows"),
    status: v.string(), // "running" | "completed" | "failed"

    // Execution state
    currentNodeId: v.optional(v.string()),
    nodeResults: v.any(), // Flexible execution results
    variables: v.any(), // State variables

    // Input/Output
    input: v.optional(v.any()),
    output: v.optional(v.any()),
    error: v.optional(v.string()),

    // Timestamps
    startedAt: v.string(),
    completedAt: v.optional(v.string()),

    // Execution metadata
    threadId: v.optional(v.string()),
  })
    .index("by_workflow", ["workflowId"])
    .index("by_status", ["status"])
    .index("by_started", ["startedAt"]),

  // MCP servers registry - Centralized configuration
  mcpServers: defineTable({
    // Ownership
    userId: v.string(), // Clerk user ID who owns this MCP

    // Basic info
    name: v.string(),
    url: v.string(),
    description: v.optional(v.string()),
    category: v.string(), // "web" | "ai" | "data" | "custom"

    // Authentication
    authType: v.string(), // "none" | "api-key" | "bearer" | "oauth-coming-soon"
    accessToken: v.optional(v.string()), // Encrypted token

    // Tools & Status
    tools: v.optional(v.array(v.string())), // List of available tool names
    connectionStatus: v.string(), // "connected" | "error" | "untested"
    lastTested: v.optional(v.string()),
    lastError: v.optional(v.string()),

    // Configuration
    enabled: v.boolean(),
    isOfficial: v.boolean(), // Built-in MCPs from registry

    // Headers for custom config
    headers: v.optional(v.any()),

    createdAt: v.string(),
    updatedAt: v.string(),
  })
    .index("by_userId", ["userId"])
    .index("by_name", ["name"])
    .index("by_enabled", ["enabled"])
    .index("by_category", ["category"])
    .index("by_official", ["isOfficial"]),

  // Arcade auth records
  arcadeAuth: defineTable({
    authId: v.string(),
    toolName: v.string(),
    authUrl: v.optional(v.string()),
    userId: v.optional(v.string()),
    status: v.string(), // "pending" | "completed" | "failed"

    createdAt: v.string(),
    completedAt: v.optional(v.string()),
  })
    .index("by_authId", ["authId"])
    .index("by_status", ["status"]),

  // User MCP Servers - Cursor-style configuration
  userMCPs: defineTable({
    userId: v.string(),
    name: v.string(),
    url: v.string(),
    headers: v.optional(v.any()),
    env: v.optional(v.any()),
    createdAt: v.string(),
    updatedAt: v.string(),
  })
    .index("by_userId", ["userId"])
    .index("by_name", ["name"]),

  // API Keys - User-generated keys for API access
  apiKeys: defineTable({
    key: v.string(), // Hashed key
    keyPrefix: v.string(), // "sk_live_abc..." for display
    userId: v.string(), // Clerk user ID who owns this key
    name: v.string(), // User-given name

    usageCount: v.number(),
    lastUsedAt: v.optional(v.string()),

    createdAt: v.string(),
    expiresAt: v.optional(v.string()),
    revokedAt: v.optional(v.string()),
  })
    .index("by_userId", ["userId"])
    .index("by_key", ["key"])
    .index("by_keyPrefix", ["keyPrefix"]),

  // User LLM API Keys - Store user's own LLM provider keys
  userLLMKeys: defineTable({
    userId: v.string(), // Clerk user ID
    provider: v.string(), // "anthropic" | "openai" | "groq"
    encryptedKey: v.string(), // Encrypted API key
    keyPrefix: v.string(), // First/last few chars for display (e.g. "sk-ant...abc")

    // Metadata
    label: v.optional(v.string()), // User-friendly label
    isActive: v.boolean(), // Whether this key is currently active

    // Timestamps
    createdAt: v.string(),
    updatedAt: v.string(),
    lastUsedAt: v.optional(v.string()),

    // Usage tracking (optional)
    usageCount: v.optional(v.number()),
  })
    .index("by_userId", ["userId"])
    .index("by_provider", ["provider"])
    .index("by_userProvider", ["userId", "provider"])
    .index("by_active", ["isActive"]),

  // Approval records - Human-in-the-loop workflow pauses
  approvals: defineTable({
    approvalId: v.string(),
    workflowId: v.id("workflows"),
    executionId: v.optional(v.string()), // Which execution is waiting
    nodeId: v.optional(v.string()), // Which node is waiting for approval
    message: v.string(),
    status: v.string(), // "pending" | "approved" | "rejected"
    userId: v.optional(v.string()), // Who needs to approve (Clerk user ID)
    createdBy: v.optional(v.string()), // Who created the approval request

    createdAt: v.string(),
    respondedAt: v.optional(v.string()),
    respondedBy: v.optional(v.string()), // Who responded (Clerk user ID)
  })
    .index("by_approvalId", ["approvalId"])
    .index("by_status", ["status"])
    .index("by_userId", ["userId"])
    .index("by_workflow", ["workflowId"])
    .index("by_execution", ["executionId"]),
});
