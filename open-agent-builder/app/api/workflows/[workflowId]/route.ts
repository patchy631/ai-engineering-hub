import { NextRequest, NextResponse } from 'next/server';
import { getConvexClient, getAuthenticatedConvexClient, api, isConvexConfigured } from '@/lib/convex/client';

export const dynamic = 'force-dynamic';

/**
 * GET /api/workflows/[workflowId] - Get a specific workflow from Convex
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;

    if (!isConvexConfigured()) {
      return NextResponse.json(
        { error: 'Convex not configured' },
        { status: 500 }
      );
    }

    const convex = await getAuthenticatedConvexClient();

    // Look up by customId first, then try as Convex ID
    let workflow = await convex.query(api.workflows.getWorkflowByCustomId, {
      customId: workflowId,
    });

    // If not found and looks like Convex ID, try direct lookup
    if (!workflow && workflowId.startsWith('j')) {
      try {
        workflow = await convex.query(api.workflows.getWorkflow, {
          id: workflowId as any,
        });
      } catch (e) {
        // Not a valid Convex ID
      }
    }

    if (!workflow) {
      return NextResponse.json(
        { error: `Workflow ${workflowId} not found` },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      workflow: {
        ...workflow,
        id: workflow.customId || workflow._id, // Return customId if exists
      },
      source: 'convex',
    });
  } catch (error) {
    console.error('Error fetching workflow:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch workflow',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/workflows/[workflowId] - Delete a workflow from Convex
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;

    if (!isConvexConfigured()) {
      return NextResponse.json(
        { error: 'Convex not configured' },
        { status: 500 }
      );
    }

    const convex = await getAuthenticatedConvexClient();

    // Look up by customId to get Convex ID
    const workflow = await convex.query(api.workflows.getWorkflowByCustomId, {
      customId: workflowId,
    });

    if (!workflow) {
      return NextResponse.json(
        { error: `Workflow ${workflowId} not found` },
        { status: 404 }
      );
    }

    // Delete using Convex ID
    await convex.mutation(api.workflows.deleteWorkflow, {
      id: workflow._id,
    });

    return NextResponse.json({
      success: true,
      source: 'convex',
      message: `Workflow ${workflowId} deleted`,
    });
  } catch (error) {
    console.error('Error deleting workflow:', error);
    return NextResponse.json(
      {
        error: 'Failed to delete workflow',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
