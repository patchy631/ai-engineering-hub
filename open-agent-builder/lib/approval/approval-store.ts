export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export interface ApprovalRecord {
  approvalId: string;
  executionId: string;
  workflowId: string;
  nodeId: string;
  message: string;
  status: ApprovalStatus;
  userId?: string;
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  resolvedBy?: string;
}

// In-memory fallback for when Redis is not configured
type ApprovalStore = Map<string, ApprovalRecord>;

declare global {
  // eslint-disable-next-line no-var
  var __approvalStore: ApprovalStore | undefined;
}

function getMemoryStore(): ApprovalStore {
  if (!globalThis.__approvalStore) {
    globalThis.__approvalStore = new Map();
  }
  return globalThis.__approvalStore;
}

/**
 * Create or update an approval record
 */
export async function createOrUpdateApprovalRecord(
  data: Omit<ApprovalRecord, 'createdAt' | 'updatedAt' | 'status'> & {
    status?: ApprovalStatus;
  }
): Promise<ApprovalRecord> {
  const now = new Date().toISOString();

  const record: ApprovalRecord = {
    approvalId: data.approvalId,
    executionId: data.executionId,
    workflowId: data.workflowId,
    nodeId: data.nodeId,
    message: data.message,
    status: data.status ?? 'pending',
    userId: data.userId,
    createdAt: now,
    updatedAt: now,
    resolvedAt: data.status === 'approved' || data.status === 'rejected' ? now : undefined,
    resolvedBy: data.status === 'approved' || data.status === 'rejected' ? data.userId : undefined,
  };

  // Use in-memory store
  getMemoryStore().set(record.approvalId, record);
  return record;
}

/**
 * Get an approval record by ID
 */
export async function getApprovalRecord(approvalId: string): Promise<ApprovalRecord | null> {
  // Use in-memory store
  const record = getMemoryStore().get(approvalId);
  return record ? { ...record } : null;
}

/**
 * Update an approval record
 */
export async function updateApprovalRecord(
  approvalId: string,
  updates: Partial<Omit<ApprovalRecord, 'approvalId' | 'createdAt'>>
): Promise<ApprovalRecord | null> {
  const existing = await getApprovalRecord(approvalId);
  if (!existing) {
    return null;
  }

  const now = new Date().toISOString();
  const record: ApprovalRecord = {
    ...existing,
    ...updates,
    updatedAt: now,
    resolvedAt: updates.status === 'approved' || updates.status === 'rejected' ? now : existing.resolvedAt,
    resolvedBy: updates.status === 'approved' || updates.status === 'rejected' ? updates.resolvedBy || existing.resolvedBy : existing.resolvedBy,
  };

  // Use in-memory store
  getMemoryStore().set(approvalId, record);
  return record;
}

/**
 * Delete an approval record
 */
export async function deleteApprovalRecord(approvalId: string): Promise<void> {
  // Delete from memory store
  getMemoryStore().delete(approvalId);
}

/**
 * List all approval records (memory only, Redis would need a different approach)
 */
export function listApprovalRecords(): ApprovalRecord[] {
  return Array.from(getMemoryStore().values()).map(r => ({ ...r }));
}

/**
 * Generate a unique approval ID
 */
export function generateApprovalId(): string {
  return `approval_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}
