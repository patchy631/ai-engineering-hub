import { NextRequest, NextResponse } from 'next/server';
import { langGraphJSONToWorkflow } from '@/lib/workflow/langgraph';
import { saveWorkflow } from '@/lib/workflow/storage';

export const dynamic = 'force-dynamic';

/**
 * Import workflow from LangGraph JSON
 * POST /api/workflows/import-langgraph
 */
export async function POST(request: NextRequest) {
  try {
    const langGraphJSON = await request.json();

    // Validate input
    if (!langGraphJSON.nodes || !langGraphJSON.edges) {
      return NextResponse.json(
        { error: 'Invalid LangGraph JSON: missing nodes or edges' },
        { status: 400 }
      );
    }

    // Convert to workflow format
    const workflow = langGraphJSONToWorkflow(langGraphJSON);

    // Save workflow
    await saveWorkflow(workflow);

    return NextResponse.json({
      success: true,
      workflow: {
        id: workflow.id,
        name: workflow.name,
        description: workflow.description,
        nodeCount: workflow.nodes.length,
        edgeCount: workflow.edges.length,
      },
    });
  } catch (error) {
    console.error('Import error:', error);
    return NextResponse.json(
      {
        error: 'Import failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
