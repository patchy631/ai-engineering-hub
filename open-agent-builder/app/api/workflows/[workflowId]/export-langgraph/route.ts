import { NextRequest, NextResponse } from 'next/server';
import { workflowToLangGraphJSON } from '@/lib/workflow/langgraph';

export const dynamic = 'force-dynamic';

/**
 * Export workflow as LangGraph JSON
 * POST /api/workflows/:workflowId/export-langgraph
 * Expects workflow data in request body
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;
    const workflow = await request.json();

    if (!workflow || !workflow.nodes) {
      return NextResponse.json(
        { error: 'Workflow data is required in request body' },
        { status: 400 }
      );
    }

    // Convert to LangGraph format
    const langGraphJSON = workflowToLangGraphJSON(workflow);

    // Return as downloadable JSON
    return new NextResponse(JSON.stringify(langGraphJSON, null, 2), {
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="${workflow.name.replace(/\s+/g, '_')}_langgraph.json"`,
      },
    });
  } catch (error) {
    console.error('Export error:', error);
    return NextResponse.json(
      {
        error: 'Export failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
