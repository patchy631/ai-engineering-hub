import { NextRequest, NextResponse } from 'next/server';
import { createOrUpdateApprovalRecord } from '@/lib/approval/approval-store';

export const dynamic = 'force-dynamic';

/**
 * POST /api/approval - Create a new approval request
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { approvalId, executionId, workflowId, nodeId, message, userId } = body;

    if (!approvalId || !executionId || !workflowId || !nodeId) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const record = await createOrUpdateApprovalRecord({
      approvalId,
      executionId,
      workflowId,
      nodeId,
      message: message || 'Approval required',
      userId,
      status: 'pending',
    });

    return NextResponse.json({ success: true, record });
  } catch (error) {
    console.error('Failed to create approval record:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create approval',
      },
      { status: 500 }
    );
  }
}
