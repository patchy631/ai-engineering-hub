import { NextResponse } from 'next/server';
import { getAuthenticatedConvexClient, api } from '@/lib/convex/client';

/**
 * DELETE /api/workflows/cleanup
 * Clean up workflows without userId (development/admin only)
 */
export async function DELETE() {
  try {
    const convex = await getAuthenticatedConvexClient();
    const result = await convex.mutation(api.workflows.deleteWorkflowsWithoutUserId, {});

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error cleaning up workflows:', error);
    return NextResponse.json(
      {
        error: 'Failed to clean up workflows',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
