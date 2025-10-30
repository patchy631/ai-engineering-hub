/**
 * Convex functions for user-created workflow templates
 */

import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Id } from "./_generated/dataModel";

/**
 * Save a workflow as a template
 */
export const saveAsTemplate = mutation({
  args: {
    workflowId: v.id("workflows"),
    name: v.string(),
    description: v.optional(v.string()),
    category: v.optional(v.string()),
    tags: v.optional(v.array(v.string())),
    isPublic: v.optional(v.boolean()),
    difficulty: v.optional(v.string()),
    estimatedTime: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Get the source workflow
    const sourceWorkflow = await ctx.db.get(args.workflowId);

    if (!sourceWorkflow) {
      throw new Error("Workflow not found");
    }

    const now = new Date().toISOString();

    // Create a new workflow marked as a template
    const templateId = await ctx.db.insert("workflows", {
      userId: sourceWorkflow.userId,
      name: args.name,
      description: args.description || sourceWorkflow.description,
      category: args.category || "User Templates",
      tags: args.tags || [],
      difficulty: args.difficulty,
      estimatedTime: args.estimatedTime,
      nodes: sourceWorkflow.nodes,
      edges: sourceWorkflow.edges,
      createdAt: now,
      updatedAt: now,
      version: "1.0.0",
      isTemplate: true,
      // Optional: make templates public for sharing
      ...(args.isPublic !== undefined && { isPublic: args.isPublic }),
    });

    return templateId;
  },
});

/**
 * Get all templates for a user (including their own and public templates)
 */
export const getUserTemplates = query({
  args: {
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Get user's own templates
    let userTemplates: any[] = [];
    if (args.userId) {
      userTemplates = await ctx.db
        .query("workflows")
        .withIndex("by_userId", (q) => q.eq("userId", args.userId))
        .filter((q) => q.eq(q.field("isTemplate"), true))
        .collect();
    }

    // Get public templates (if we implement sharing)
    const publicTemplates = await ctx.db
      .query("workflows")
      .withIndex("by_template", (q) => q.eq("isTemplate", true))
      .filter((q) => q.eq(q.field("isPublic"), true))
      .collect();

    // Combine and deduplicate
    const allTemplates: any[] = [...userTemplates];
    const userTemplateIds = new Set(userTemplates.map((t) => t._id));

    for (const template of publicTemplates) {
      if (!userTemplateIds.has(template._id)) {
        allTemplates.push(template);
      }
    }

    // Sort by creation date (newest first)
    allTemplates.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );

    return allTemplates;
  },
});

/**
 * Get templates by category
 */
export const getTemplatesByCategory = query({
  args: {
    category: v.string(),
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let templates = await ctx.db
      .query("workflows")
      .withIndex("by_category", (q) => q.eq("category", args.category))
      .filter((q) => q.eq(q.field("isTemplate"), true))
      .collect();

    // Filter by user if provided
    if (args.userId) {
      templates = templates.filter(
        (t) => t.userId === args.userId || t.isPublic === true
      );
    }

    return templates;
  },
});

/**
 * Update a template
 */
export const updateTemplate = mutation({
  args: {
    templateId: v.id("workflows"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    category: v.optional(v.string()),
    tags: v.optional(v.array(v.string())),
    isPublic: v.optional(v.boolean()),
    difficulty: v.optional(v.string()),
    estimatedTime: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const template = await ctx.db.get(args.templateId);

    if (!template || !template.isTemplate) {
      throw new Error("Template not found");
    }

    const updates: any = {
      updatedAt: new Date().toISOString(),
    };

    if (args.name !== undefined) updates.name = args.name;
    if (args.description !== undefined) updates.description = args.description;
    if (args.category !== undefined) updates.category = args.category;
    if (args.tags !== undefined) updates.tags = args.tags;
    if (args.isPublic !== undefined) updates.isPublic = args.isPublic;
    if (args.difficulty !== undefined) updates.difficulty = args.difficulty;
    if (args.estimatedTime !== undefined) updates.estimatedTime = args.estimatedTime;

    await ctx.db.patch(args.templateId, updates);
  },
});

/**
 * Delete a template
 */
export const deleteTemplate = mutation({
  args: {
    templateId: v.id("workflows"),
    userId: v.string(),
  },
  handler: async (ctx, args) => {
    const template = await ctx.db.get(args.templateId);

    if (!template || !template.isTemplate) {
      throw new Error("Template not found");
    }

    if (template.userId !== args.userId) {
      throw new Error("Unauthorized: You can only delete your own templates");
    }

    await ctx.db.delete(args.templateId);
  },
});

/**
 * Create a workflow from a template
 */
export const createWorkflowFromTemplate = mutation({
  args: {
    templateId: v.id("workflows"),
    workflowName: v.optional(v.string()),
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const template = await ctx.db.get(args.templateId);

    if (!template || !template.isTemplate) {
      throw new Error("Template not found");
    }

    const now = new Date().toISOString();

    // Create a new workflow from the template
    const workflowId = await ctx.db.insert("workflows", {
      userId: args.userId,
      name: args.workflowName || `${template.name} (Copy)`,
      description: template.description,
      category: template.category,
      tags: template.tags || [],
      difficulty: template.difficulty,
      estimatedTime: template.estimatedTime,
      nodes: template.nodes,
      edges: template.edges,
      createdAt: now,
      updatedAt: now,
      version: template.version || "1.0.0",
      isTemplate: false, // This is a regular workflow, not a template
    });

    return workflowId;
  },
});

/**
 * Get all template categories
 */
export const getTemplateCategories = query({
  args: {
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const templates = await ctx.db
      .query("workflows")
      .withIndex("by_template", (q) => q.eq("isTemplate", true))
      .collect();

    // Filter by user or public
    const filteredTemplates = args.userId
      ? templates.filter((t) => t.userId === args.userId || t.isPublic === true)
      : templates.filter((t) => t.isPublic === true);

    // Extract unique categories
    const categories = new Set<string>();
    filteredTemplates.forEach((t) => {
      if (t.category) {
        categories.add(t.category);
      }
    });

    // Always include default categories
    categories.add("User Templates");
    categories.add("Shared Templates");

    return Array.from(categories).sort();
  },
});