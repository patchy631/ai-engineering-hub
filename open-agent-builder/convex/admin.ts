import { mutation } from "./_generated/server";

/**
 * Admin functions for database management
 */

// Clear all workflows (use with caution!)
export const clearAllWorkflows = mutation({
  args: {},
  handler: async ({ db }) => {
    const workflows = await db.query("workflows").collect();
    let deleted = 0;

    for (const workflow of workflows) {
      await db.delete(workflow._id);
      deleted++;
    }

    return { deleted };
  },
});
