import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

/**
 * Convex Approvals - Human-in-the-loop workflow approvals
 *
 * Features:
 * - Real-time subscriptions (no polling needed!)
 * - Automatic reactivity when approval status changes
 * - Perfect for pausing workflows waiting for human input
 */

// Create a new approval request
export const create = mutation({
  args: {
    approvalId: v.string(),
    workflowId: v.id("workflows"),
    nodeId: v.optional(v.string()),
    executionId: v.optional(v.string()),
    message: v.string(),
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const now = new Date().toISOString();

    const approvalDoc = await ctx.db.insert("approvals", {
      approvalId: args.approvalId,
      workflowId: args.workflowId,
      executionId: args.executionId,
      nodeId: args.nodeId,
      message: args.message,
      status: "pending",
      userId: args.userId,
      createdAt: now,
    });

    return approvalDoc;
  },
});

// Get approval by approvalId (for polling or one-time checks)
export const getByApprovalId = query({
  args: { approvalId: v.string() },
  handler: async (ctx, args) => {
    const approval = await ctx.db
      .query("approvals")
      .withIndex("by_approvalId", (q) => q.eq("approvalId", args.approvalId))
      .first();

    return approval;
  },
});

// Watch approval status - REAL-TIME SUBSCRIPTION
// Use this in your frontend to automatically resume when approved
export const watchStatus = query({
  args: { approvalId: v.string() },
  handler: async (ctx, args) => {
    const approval = await ctx.db
      .query("approvals")
      .withIndex("by_approvalId", (q) => q.eq("approvalId", args.approvalId))
      .first();

    if (!approval) {
      return { status: "not_found", approval: null };
    }

    return {
      status: approval.status,
      approval,
    };
  },
});

// Approve an approval request
export const approve = mutation({
  args: {
    approvalId: v.string(),
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const approval = await ctx.db
      .query("approvals")
      .withIndex("by_approvalId", (q) => q.eq("approvalId", args.approvalId))
      .first();

    if (!approval) {
      throw new Error(`Approval ${args.approvalId} not found`);
    }

    if (approval.status !== "pending") {
      throw new Error(`Approval ${args.approvalId} already ${approval.status}`);
    }

    const now = new Date().toISOString();

    await ctx.db.patch(approval._id, {
      status: "approved",
      respondedAt: now,
      respondedBy: args.userId,
    });

    return { success: true, status: "approved" };
  },
});

// Reject an approval request
export const reject = mutation({
  args: {
    approvalId: v.string(),
    userId: v.optional(v.string()),
    reason: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const approval = await ctx.db
      .query("approvals")
      .withIndex("by_approvalId", (q) => q.eq("approvalId", args.approvalId))
      .first();

    if (!approval) {
      throw new Error(`Approval ${args.approvalId} not found`);
    }

    if (approval.status !== "pending") {
      throw new Error(`Approval ${args.approvalId} already ${approval.status}`);
    }

    const now = new Date().toISOString();

    await ctx.db.patch(approval._id, {
      status: "rejected",
      respondedAt: now,
      respondedBy: args.userId,
    });

    return { success: true, status: "rejected", reason: args.reason };
  },
});

// List pending approvals for a workflow
export const listPending = query({
  args: { workflowId: v.id("workflows") },
  handler: async (ctx, args) => {
    const approvals = await ctx.db
      .query("approvals")
      .withIndex("by_workflow", (q) => q.eq("workflowId", args.workflowId))
      .filter((q) => q.eq(q.field("status"), "pending"))
      .collect();

    return approvals;
  },
});

// List all approvals for a workflow
export const listByWorkflow = query({
  args: { workflowId: v.id("workflows") },
  handler: async (ctx, args) => {
    const approvals = await ctx.db
      .query("approvals")
      .withIndex("by_workflow", (q) => q.eq("workflowId", args.workflowId))
      .order("desc")
      .collect();

    return approvals;
  },
});

// Get approvals for a specific execution (useful for tracking what's blocking a run)
export const getByExecution = query({
  args: { executionId: v.string() },
  handler: async (ctx, args) => {
    const approvals = await ctx.db
      .query("approvals")
      .withIndex("by_execution", (q) => q.eq("executionId", args.executionId))
      .order("desc")
      .collect();

    return approvals;
  },
});

// Clean up old approvals (approved/rejected older than 24 hours)
export const cleanup = mutation({
  args: {},
  handler: async (ctx) => {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const oldApprovals = await ctx.db
      .query("approvals")
      .filter((q) =>
        q.and(
          q.neq(q.field("status"), "pending"),
          q.lt(q.field("createdAt"), oneDayAgo)
        )
      )
      .collect();

    for (const approval of oldApprovals) {
      await ctx.db.delete(approval._id);
    }

    return { deleted: oldApprovals.length };
  },
});
