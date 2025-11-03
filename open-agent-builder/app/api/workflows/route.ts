import { NextRequest, NextResponse } from 'next/server';
import { getConvexClient, getAuthenticatedConvexClient, api, isConvexConfigured } from '@/lib/convex/client';

export const dynamic = 'force-dynamic';

/**
 * GET /api/workflows - List all workflows
 * Uses Convex for storage
 */
export async function GET(request: NextRequest) {
  try {
    if (!isConvexConfigured()) {
      return NextResponse.json({
        workflows: [],
        total: 0,
        source: 'none',
        message: 'Convex not configured. Add NEXT_PUBLIC_CONVEX_URL to .env.local',
      });
    }

    const convex = await getAuthenticatedConvexClient();
    const workflows = await convex.query(api.workflows.listWorkflows, {});

    return NextResponse.json({
      workflows: workflows.map((w: any) => ({
        id: w.customId || w._id, // Use customId if exists, otherwise Convex ID
        name: w.name,
        description: w.description,
        category: w.category,
        tags: w.tags,
        difficulty: w.difficulty,
        estimatedTime: w.estimatedTime,
        nodes: w.nodes,
        edges: w.edges,
        createdAt: w.createdAt,
        updatedAt: w.updatedAt,
        nodeCount: w.nodes?.length || 0,
        edgeCount: w.edges?.length || 0,
      })),
      total: workflows.length,
      source: 'convex',
    });
  } catch (error) {
    console.error('Error fetching workflows:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch workflows',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/workflows - Save a workflow to Convex
 */
export async function POST(request: NextRequest) {
  try {
    let workflow;
    try {
      const body = await request.text();
      if (!body || body.trim() === '') {
        return NextResponse.json(
          { error: 'Request body is empty' },
          { status: 400 }
        );
      }
      workflow = JSON.parse(body);
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }

    if (!workflow.id && !workflow.name) {
      return NextResponse.json(
        { error: 'Workflow must have either id or name' },
        { status: 400 }
      );
    }

    if (!isConvexConfigured()) {
      return NextResponse.json({
        success: false,
        message: 'Convex not configured. Add NEXT_PUBLIC_CONVEX_URL to .env.local',
      }, { status: 500 });
    }

    // Validate workflow has required fields
    if (!workflow.nodes || !Array.isArray(workflow.nodes)) {
      return NextResponse.json(
        { error: 'Workflow must have a nodes array' },
        { status: 400 }
      );
    }

    if (!workflow.edges || !Array.isArray(workflow.edges)) {
      return NextResponse.json(
        { error: 'Workflow must have an edges array' },
        { status: 400 }
      );
    }

    const convex = await getAuthenticatedConvexClient();

    // Use workflow.id as customId for Convex
    const customId = workflow.id || `workflow_${Date.now()}`;

    const savedId = await convex.mutation(api.workflows.saveWorkflow, {
      customId,
      name: workflow.name || 'Untitled Workflow',
      description: workflow.description,
      category: workflow.category,
      tags: workflow.tags,
      difficulty: workflow.difficulty,
      estimatedTime: workflow.estimatedTime,
      nodes: workflow.nodes,
      edges: workflow.edges,
      version: workflow.version,
      isTemplate: workflow.isTemplate,
    });

    return NextResponse.json({
      success: true,
      workflowId: savedId,
      source: 'convex',
      message: 'Workflow saved successfully',
    });
  } catch (error) {
    console.error('Error saving workflow:', error);
    return NextResponse.json(
      {
        error: 'Failed to save workflow',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/workflows?id=xxx - Delete a workflow from Convex
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const workflowId = searchParams.get('id');

    if (!workflowId) {
      return NextResponse.json(
        { error: 'Workflow ID is required' },
        { status: 400 }
      );
    }

    if (!isConvexConfigured()) {
      return NextResponse.json({
        success: false,
        message: 'Convex not configured',
      }, { status: 500 });
    }

    const convex = await getAuthenticatedConvexClient();

    // Look up workflow by customId first, then try Convex ID
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

    // Delete using Convex ID
    await convex.mutation(api.workflows.deleteWorkflow, {
      id: workflow._id,
    });

    return NextResponse.json({
      success: true,
      source: 'convex',
      message: 'Workflow deleted successfully',
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

