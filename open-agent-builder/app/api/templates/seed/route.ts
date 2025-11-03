import { NextRequest, NextResponse } from 'next/server';
import { getAuthenticatedConvexClient, api, isConvexConfigured } from '@/lib/convex/client';
import { exampleTemplates, exampleTemplatesList } from '@/lib/workflow/templates/examples';

export const dynamic = 'force-dynamic';

/**
 * POST /api/templates/seed - Seed official templates to Convex
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
    const templateList = exampleTemplatesList;
    const seededTemplates: string[] = [];
    const skippedTemplates: string[] = [];

    for (const templateInfo of templateList) {
      const template = exampleTemplates[templateInfo.id];
      if (!template) continue;

      try {
        const result = await convex.mutation(api.workflows.seedOfficialTemplate, {
          customId: template.id,
          name: template.name,
          description: template.description,
          category: template.category,
          tags: template.tags,
          difficulty: template.difficulty,
          estimatedTime: template.estimatedTime,
          nodes: template.nodes,
          edges: template.edges,
        });

        if (result.success) {
          seededTemplates.push(template.name);
        } else {
          skippedTemplates.push(template.name);
        }
      } catch (error) {
        console.error(`Failed to seed template ${template.name}:`, error);
        skippedTemplates.push(template.name);
      }
    }

    return NextResponse.json({
      success: true,
      seeded: seededTemplates.length,
      skipped: skippedTemplates.length,
      total: templateList.length,
      seededTemplates,
      skippedTemplates,
      message: `Seeded ${seededTemplates.length} templates, skipped ${skippedTemplates.length}`,
    });
  } catch (error) {
    console.error('Error seeding templates:', error);
    return NextResponse.json(
      {
        error: 'Failed to seed templates',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}