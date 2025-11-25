import { NextRequest, NextResponse } from 'next/server';
import { getAuthenticatedConvexClient, api, isConvexConfigured } from '@/lib/convex/client';
import { listTemplates, getTemplate } from '@/lib/workflow/templates';

export const dynamic = 'force-dynamic';

/**
 * POST /api/templates/update - Update existing templates in Convex with latest changes
 */
export async function POST(request: NextRequest) {
  try {
    if (!isConvexConfigured()) {
      return NextResponse.json({
        success: false,
        message: 'Convex not configured',
      }, { status: 500 });
    }

    const convex = await getAuthenticatedConvexClient();

    // Get all templates from static file
    const templateList = listTemplates();
    const updatedTemplates: string[] = [];
    const failedTemplates: string[] = [];

    for (const templateInfo of templateList) {
      const template = getTemplate(templateInfo.id);
      if (!template) continue;

      try {
        const result = await convex.mutation(api.workflows.updateTemplateStructure, {
          customId: template.id,
          nodes: template.nodes,
          edges: template.edges,
        });

        if (result.success) {
          updatedTemplates.push(template.name);
        } else {
          failedTemplates.push(template.name);
        }
      } catch (error) {
        console.error(`Failed to update template ${template.name}:`, error);
        failedTemplates.push(template.name);
      }
    }

    return NextResponse.json({
      success: true,
      updated: updatedTemplates.length,
      failed: failedTemplates.length,
      total: templateList.length,
      updatedTemplates,
      failedTemplates,
      message: `Updated ${updatedTemplates.length} templates, ${failedTemplates.length} failed`,
    });
  } catch (error) {
    console.error('Error updating templates:', error);
    return NextResponse.json(
      {
        error: 'Failed to update templates',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
