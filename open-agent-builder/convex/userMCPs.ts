import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

/**
 * User MCP Servers - Cursor-style configuration
 *
 * Allows users to import their MCP configs from Cursor/Claude Desktop
 */

// Add MCP server from cursor config
export const add = mutation({
  args: {
    name: v.string(),
    url: v.string(),
    headers: v.optional(v.any()),
    env: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    // Check if MCP with this name already exists for user
    const existing = await ctx.db
      .query("userMCPs")
      .filter((q) =>
        q.and(
          q.eq(q.field("userId"), identity.subject),
          q.eq(q.field("name"), args.name)
        )
      )
      .first();

    if (existing) {
      // Update existing
      await ctx.db.patch(existing._id, {
        url: args.url,
        headers: args.headers,
        env: args.env,
        updatedAt: new Date().toISOString(),
      });
      return existing._id;
    }

    // Create new
    return await ctx.db.insert("userMCPs", {
      userId: identity.subject,
      name: args.name,
      url: args.url,
      headers: args.headers,
      env: args.env,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
  },
});

// List user's MCP servers
export const list = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];

    return await ctx.db
      .query("userMCPs")
      .filter((q) => q.eq(q.field("userId"), identity.subject))
      .order("desc")
      .collect();
  },
});

// Remove MCP server
export const remove = mutation({
  args: { id: v.id("userMCPs") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const mcp = await ctx.db.get(args.id);
    if (!mcp) {
      throw new Error("MCP not found");
    }

    if (mcp.userId !== identity.subject) {
      throw new Error("Unauthorized");
    }

    await ctx.db.delete(args.id);
    return { success: true };
  },
});

// Import from cursor config
export const importFromCursor = mutation({
  args: {
    config: v.string(), // JSON string of cursor config
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    try {
      const parsed = JSON.parse(args.config);

      if (!parsed.mcpServers) {
        throw new Error("Invalid config: missing mcpServers field");
      }

      const imported: Array<{ id: any; name: string }> = [];

      for (const [name, config] of Object.entries(parsed.mcpServers)) {
        const mcpConfig = config as any;

        const mcpId = await ctx.db.insert("userMCPs", {
          userId: identity.subject,
          name,
          url: mcpConfig.url || mcpConfig.command || '',
          headers: mcpConfig.headers,
          env: mcpConfig.env,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        });

        imported.push({ id: mcpId, name });
      }

      return {
        success: true,
        imported: imported.length,
        servers: imported,
      };
    } catch (error) {
      throw new Error(`Failed to import: ${error instanceof Error ? error.message : 'Invalid JSON'}`);
    }
  },
});
