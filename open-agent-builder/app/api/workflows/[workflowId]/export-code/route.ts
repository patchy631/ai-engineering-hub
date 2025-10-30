import { NextRequest, NextResponse } from 'next/server';
import { workflowToLangGraphCode } from '@/lib/workflow/langgraph';

export const dynamic = 'force-dynamic';

/**
 * Export workflow as executable LangGraph TypeScript code
 * POST /api/workflows/:workflowId/export-code
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

    // Generate TypeScript code
    const code = workflowToLangGraphCode(workflow);

    // Return as JSON with code string
    return NextResponse.json({
      code,
      filename: `${workflow.name.replace(/\s+/g, '_')}.ts`,
      language: 'typescript',
    });
  } catch (error) {
    console.error('Code export error:', error);
    return NextResponse.json(
      {
        error: 'Code export failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
