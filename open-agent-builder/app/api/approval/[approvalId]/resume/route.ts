import { NextRequest, NextResponse } from 'next/server';
import { getApprovalRecord } from '@/lib/approval/approval-store';

export const dynamic = 'force-dynamic';

/**
 * GET /api/approval/[approvalId]/resume - Get workflow resume data
 * This endpoint returns the execution state needed to resume the workflow
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ approvalId: string }> }
) {
  const { approvalId } = await params;

  if (!approvalId) {
    return NextResponse.json(
      { success: false, error: 'Approval ID is required' },
      { status: 400 }
    );
  }

  const record = await getApprovalRecord(approvalId);
  if (!record) {
    return NextResponse.json(
      { success: false, error: 'Approval record not found' },
      { status: 404 }
    );
  }

  if (record.status === 'pending') {
    return NextResponse.json(
      { success: false, error: 'Approval is still pending' },
      { status: 400 }
    );
  }

  return NextResponse.json({
    success: true,
    approved: record.status === 'approved',
    record,
  });
}
