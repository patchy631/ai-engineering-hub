import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

/**
 * Workflow CRUD Operations
 */

// Get all workflows (filtered by user if authenticated)
export const list = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();

    // If authenticated, only show user's workflows (exclude templates and undefined userId)
    if (identity) {
      const workflows = await ctx.db
        .query("workflows")
        .filter((q) =>
          q.and(
            q.eq(q.field("userId"), identity.subject),
            q.neq(q.field("isTemplate"), true)
          )
        )
        .order("desc")
        .collect();
      return workflows;
    }

    // If not authenticated, return empty array
    return [];
  },
});

// Alias for backwards compatibility
export const listWorkflows = list;

// Get workflow by Convex ID
export const getWorkflow = query({
  args: { id: v.id("workflows") },
  handler: async ({ db }, { id }) => {
    const workflow = await db.get(id);
    return workflow;
  },
});

// Get workflow by custom ID (like "workflow_123" or "amazon-product-research")
export const getWorkflowByCustomId = query({
  args: { customId: v.string() },
  handler: async ({ db }, { customId }) => {
    const workflow = await db
      .query("workflows")
      .withIndex("by_customId", (q) => q.eq("customId", customId))
      .first();
    return workflow;
  },
});

// Create or update workflow
export const saveWorkflow = mutation({
  args: {
    customId: v.optional(v.string()), // Optional - the workflow's custom ID
    name: v.string(),
    description: v.optional(v.string()),
    category: v.optional(v.string()),
    tags: v.optional(v.array(v.string())),
    difficulty: v.optional(v.string()),
    estimatedTime: v.optional(v.string()),
    nodes: v.array(v.any()),
    edges: v.array(v.any()),
    version: v.optional(v.string()),
    isTemplate: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();

    // Check if workflow with this customId already exists (if customId provided)
    if (args.customId) {
      const existing = await ctx.db
        .query("workflows")
        .withIndex("by_customId", (q) => q.eq("customId", args.customId))
        .first();

      if (existing) {
        // Check ownership if user is authenticated
        if (identity && existing.userId && existing.userId !== identity.subject) {
          throw new Error("Unauthorized: workflow belongs to another user");
        }

        // Update existing workflow
        await ctx.db.patch(existing._id, {
          ...args,
          updatedAt: new Date().toISOString(),
        });
        return existing._id;
      }
    }

    // Create new workflow with user ownership
    const newId = await ctx.db.insert("workflows", {
      ...args,
      userId: identity?.subject, // Add user ownership if authenticated
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    return newId;
  },
});

// Delete workflow
export const deleteWorkflow = mutation({
  args: { id: v.id("workflows") },
  handler: async ({ db }, { id }) => {
    await db.delete(id);
    return { success: true };
  },
});

// Get workflows by category
export const getWorkflowsByCategory = query({
  args: { category: v.string() },
  handler: async ({ db }, { category }) => {
    const workflows = await db
      .query("workflows")
      .withIndex("by_category", (q) => q.eq("category", category))
      .collect();
    return workflows;
  },
});

// Get template workflows
export const getTemplates = query({
  args: {},
  handler: async ({ db }) => {
    const templates = await db
      .query("workflows")
      .withIndex("by_template", (q) => q.eq("isTemplate", true))
      .collect();
    return templates;
  },
});

// Seed a single official template
export const seedOfficialTemplate = mutation({
  args: {
    customId: v.string(),
    name: v.string(),
    description: v.optional(v.string()),
    category: v.optional(v.string()),
    tags: v.optional(v.array(v.string())),
    difficulty: v.optional(v.string()),
    estimatedTime: v.optional(v.string()),
    nodes: v.array(v.any()),
    edges: v.array(v.any()),
  },
  handler: async (ctx, template) => {
    // Check if this template already exists
    const existing = await ctx.db
      .query("workflows")
      .withIndex("by_customId", (q) => q.eq("customId", template.customId))
      .first();

    if (existing) {
      // Template already exists, skip
      return { success: false, message: "Template already exists" };
    }

    // Create the template in Convex
    const newId = await ctx.db.insert("workflows", {
      customId: template.customId,
      name: template.name,
      description: template.description,
      category: template.category || "Templates",
      tags: template.tags || [],
      difficulty: template.difficulty,
      estimatedTime: template.estimatedTime,
      nodes: template.nodes,
      edges: template.edges,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: "1.0.0",
      isTemplate: true,
      isPublic: true, // Make templates public by default
    });

    return {
      success: true,
      id: newId.toString(),
      message: `Seeded template: ${template.name}`,
    };
  },
});

// Get all official templates
export const getAllOfficialTemplates = query({
  args: {},
  handler: async ({ db }) => {
    const templates = await db
      .query("workflows")
      .filter((q) =>
        q.and(
          q.eq(q.field("isTemplate"), true),
          q.eq(q.field("isPublic"), true)
        )
      )
      .collect();

    return templates.map(t => ({
      ...t,
      id: t.customId || t._id, // Use customId as the primary identifier
    }));
  },
});

// Get template by custom ID (e.g., 'multi-company-stock-analysis')
export const getTemplateByCustomId = query({
  args: { customId: v.string() },
  handler: async ({ db }, { customId }) => {
    const template = await db
      .query("workflows")
      .withIndex("by_customId", (q) => q.eq("customId", customId))
      .filter((q) => q.eq(q.field("isTemplate"), true))
      .first();

    if (template) {
      return {
        ...template,
        id: template.customId || template._id,
      };
    }
    return null;
  },
});

// Update template structure (nodes and edges)
export const updateTemplateStructure = mutation({
  args: {
    customId: v.string(),
    nodes: v.array(v.any()),
    edges: v.array(v.any()),
  },
  handler: async (ctx, { customId, nodes, edges }) => {
    // Find the template
    const template = await ctx.db
      .query("workflows")
      .withIndex("by_customId", (q) => q.eq("customId", customId))
      .filter((q) => q.eq(q.field("isTemplate"), true))
      .first();

    if (!template) {
      throw new Error(`Template ${customId} not found`);
    }

    // Update the template
    await ctx.db.patch(template._id, {
      nodes,
      edges,
      updatedAt: new Date().toISOString(),
    });

    return { success: true, message: `Updated template ${customId}` };
  },
});

// Reset template to original from static file
export const resetTemplateToDefault = mutation({
  args: { customId: v.string() },
  handler: async (ctx, { customId }) => {
    // Get the original template from static file
    const originalTemplate = await import("@/lib/workflow/templates/examples").then((mod) =>
      mod.exampleTemplates[customId]
    );

    if (!originalTemplate) {
      throw new Error(`Original template ${customId} not found`);
    }

    // Find the template in database
    const template = await ctx.db
      .query("workflows")
      .withIndex("by_customId", (q) => q.eq("customId", customId))
      .filter((q) => q.eq(q.field("isTemplate"), true))
      .first();

    if (!template) {
      throw new Error(`Template ${customId} not found in database`);
    }

    // Reset to original
    await ctx.db.patch(template._id, {
      nodes: originalTemplate.nodes,
      edges: originalTemplate.edges,
      updatedAt: new Date().toISOString(),
    });

    return { success: true, message: `Reset template ${customId} to default` };
  },
});

// Clean up workflows without userId (admin/development only)
export const deleteWorkflowsWithoutUserId = mutation({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();

    // Only allow if authenticated (add admin check in production)
    if (!identity) {
      throw new Error("Unauthorized: must be authenticated");
    }

    // Find all workflows without userId and not templates
    const workflows = await ctx.db
      .query("workflows")
      .filter((q) =>
        q.and(
          q.eq(q.field("userId"), undefined),
          q.neq(q.field("isTemplate"), true)
        )
      )
      .collect();

    // Delete them
    const deletePromises = workflows.map((w) => ctx.db.delete(w._id));
    await Promise.all(deletePromises);

    return {
      success: true,
      count: workflows.length,
      message: `Deleted ${workflows.length} workflows without userId`,
    };
  },
});
