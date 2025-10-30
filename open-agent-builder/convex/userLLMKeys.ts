/**
 * Convex functions for managing user LLM API keys
 * Keys are encrypted and stored per-user
 */

import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Id } from "./_generated/dataModel";

// Simple obfuscation for API keys (you should use a proper encryption library in production)
// Since Convex doesn't have Buffer or btoa/atob, we'll use a simple reversible obfuscation
const encrypt = (text: string): string => {
  // In production, use proper encryption with a secret key
  // Simple character code shifting for obfuscation
  return text.split('').map(char =>
    String.fromCharCode(char.charCodeAt(0) + 7)
  ).join('');
};

const decrypt = (encrypted: string): string => {
  // In production, use proper decryption
  // Reverse the character code shifting
  try {
    return encrypted.split('').map(char =>
      String.fromCharCode(char.charCodeAt(0) - 7)
    ).join('');
  } catch {
    return encrypted; // Return as-is if decryption fails
  }
};

const maskKey = (key: string): string => {
  if (key.length < 8) return '••••••••';
  return `${key.slice(0, 6)}...${key.slice(-4)}`;
};

/**
 * Get all LLM keys for a user
 */
export const getUserLLMKeys = query({
  args: {
    userId: v.string(),
  },
  handler: async (ctx, args) => {
    const keys = await ctx.db
      .query("userLLMKeys")
      .withIndex("by_userId", (q) => q.eq("userId", args.userId))
      .collect();

    // Don't return the actual encrypted keys, just metadata
    return keys.map(key => ({
      _id: key._id,
      provider: key.provider,
      keyPrefix: key.keyPrefix,
      label: key.label,
      isActive: key.isActive,
      createdAt: key.createdAt,
      updatedAt: key.updatedAt,
      lastUsedAt: key.lastUsedAt,
      usageCount: key.usageCount,
    }));
  },
});

/**
 * Get active key for a specific provider
 */
export const getActiveKey = query({
  args: {
    userId: v.string(),
    provider: v.string(),
  },
  handler: async (ctx, args) => {
    const key = await ctx.db
      .query("userLLMKeys")
      .withIndex("by_userProvider", (q) =>
        q.eq("userId", args.userId).eq("provider", args.provider)
      )
      .filter((q) => q.eq(q.field("isActive"), true))
      .first();

    if (!key) return null;

    // Return decrypted key for use
    return {
      _id: key._id,
      provider: key.provider,
      apiKey: decrypt(key.encryptedKey),
      label: key.label,
    };
  },
});

/**
 * Add or update a user's LLM API key
 */
export const upsertLLMKey = mutation({
  args: {
    userId: v.string(),
    provider: v.string(),
    apiKey: v.string(),
    label: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Check if user already has a key for this provider
    const existingKey = await ctx.db
      .query("userLLMKeys")
      .withIndex("by_userProvider", (q) =>
        q.eq("userId", args.userId).eq("provider", args.provider)
      )
      .first();

    const now = new Date().toISOString();
    const encryptedKey = encrypt(args.apiKey);
    const keyPrefix = maskKey(args.apiKey);

    if (existingKey) {
      // Update existing key
      await ctx.db.patch(existingKey._id, {
        encryptedKey,
        keyPrefix,
        label: args.label || existingKey.label,
        isActive: true,
        updatedAt: now,
      });

      // Deactivate other keys for this provider
      const otherKeys = await ctx.db
        .query("userLLMKeys")
        .withIndex("by_userProvider", (q) =>
          q.eq("userId", args.userId).eq("provider", args.provider)
        )
        .collect();

      for (const key of otherKeys) {
        if (key._id !== existingKey._id) {
          await ctx.db.patch(key._id, { isActive: false });
        }
      }

      return existingKey._id;
    } else {
      // Create new key
      const id = await ctx.db.insert("userLLMKeys", {
        userId: args.userId,
        provider: args.provider,
        encryptedKey,
        keyPrefix,
        label: args.label,
        isActive: true,
        createdAt: now,
        updatedAt: now,
        usageCount: 0,
      });

      return id;
    }
  },
});

/**
 * Delete a user's LLM API key
 */
export const deleteLLMKey = mutation({
  args: {
    id: v.id("userLLMKeys"),
    userId: v.string(), // For authorization
  },
  handler: async (ctx, args) => {
    const key = await ctx.db.get(args.id);

    if (!key || key.userId !== args.userId) {
      throw new Error("Key not found or unauthorized");
    }

    await ctx.db.delete(args.id);
  },
});

/**
 * Toggle active state of a key
 */
export const toggleKeyActive = mutation({
  args: {
    id: v.id("userLLMKeys"),
    userId: v.string(),
  },
  handler: async (ctx, args) => {
    const key = await ctx.db.get(args.id);

    if (!key || key.userId !== args.userId) {
      throw new Error("Key not found or unauthorized");
    }

    const now = new Date().toISOString();

    // If activating this key, deactivate others for same provider
    if (!key.isActive) {
      const otherKeys = await ctx.db
        .query("userLLMKeys")
        .withIndex("by_userProvider", (q) =>
          q.eq("userId", args.userId).eq("provider", key.provider)
        )
        .collect();

      for (const otherKey of otherKeys) {
        if (otherKey._id !== args.id && otherKey.isActive) {
          await ctx.db.patch(otherKey._id, {
            isActive: false,
            updatedAt: now,
          });
        }
      }
    }

    await ctx.db.patch(args.id, {
      isActive: !key.isActive,
      updatedAt: now,
    });
  },
});

/**
 * Update usage stats for a key
 */
export const updateKeyUsage = mutation({
  args: {
    userId: v.string(),
    provider: v.string(),
  },
  handler: async (ctx, args) => {
    const key = await ctx.db
      .query("userLLMKeys")
      .withIndex("by_userProvider", (q) =>
        q.eq("userId", args.userId).eq("provider", args.provider)
      )
      .filter((q) => q.eq(q.field("isActive"), true))
      .first();

    if (key) {
      const now = new Date().toISOString();
      await ctx.db.patch(key._id, {
        lastUsedAt: now,
        usageCount: (key.usageCount || 0) + 1,
      });
    }
  },
});