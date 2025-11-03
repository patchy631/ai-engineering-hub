import { NextRequest, NextResponse } from 'next/server';
import { getApprovalRecord, updateApprovalRecord } from '@/lib/approval/approval-store';

export const dynamic = 'force-dynamic';

/**
 * GET /api/approval/[approvalId] - Get approval status
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

  return NextResponse.json({
    success: true,
    record,
  });
}

/**
 * POST /api/approval/[approvalId] - Approve or reject
 */
export async function POST(
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

  try {
    const body = await request.json();
    const { action, userId } = body;

    if (action !== 'approve' && action !== 'reject') {
      return NextResponse.json(
        { success: false, error: 'Action must be "approve" or "reject"' },
        { status: 400 }
      );
    }

    const status = action === 'approve' ? 'approved' : 'rejected';
    const record = await updateApprovalRecord(approvalId, {
      status,
      resolvedBy: userId,
    });

    if (!record) {
      return NextResponse.json(
        { success: false, error: 'Approval record not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      record,
    });
  } catch (error) {
    console.error('Failed to update approval:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update approval',
      },
      { status: 500 }
    );
  }
}
