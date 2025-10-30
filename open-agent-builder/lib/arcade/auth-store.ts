export type ArcadeAuthStatus = 'pending' | 'completed' | 'failed';

export interface ArcadeAuthRecord {
  authId: string;
  executionId: string;
  workflowId: string;
  nodeId: string;
  toolName: string;
  authUrl?: string | null;
  status: ArcadeAuthStatus;
  userId?: string;
  pendingInput?: any;
  createdAt: string;
  updatedAt: string;
}

// In-memory fallback for when Redis is not configured
type ArcadeAuthStore = Map<string, ArcadeAuthRecord>;

declare global {
  // eslint-disable-next-line no-var
  var __arcadeAuthStore: ArcadeAuthStore | undefined;
}

function getMemoryStore(): ArcadeAuthStore {
  if (!globalThis.__arcadeAuthStore) {
    globalThis.__arcadeAuthStore = new Map();
  }
  return globalThis.__arcadeAuthStore;
}

function cloneRecord(record: ArcadeAuthRecord): ArcadeAuthRecord {
  return JSON.parse(JSON.stringify(record)) as ArcadeAuthRecord;
}

export async function createOrUpdateArcadeAuthRecord(
  data: Omit<ArcadeAuthRecord, 'createdAt' | 'updatedAt' | 'status'> & {
    status?: ArcadeAuthStatus;
  }
): Promise<ArcadeAuthRecord> {
  const now = new Date().toISOString();
  let existing: ArcadeAuthRecord | null = null;

  // Get existing record from memory store
  existing = getMemoryStore().get(data.authId) || null;

  const record: ArcadeAuthRecord = {
    authId: data.authId,
    executionId: data.executionId,
    workflowId: data.workflowId,
    nodeId: data.nodeId,
    toolName: data.toolName,
    authUrl: data.authUrl ?? existing?.authUrl ?? undefined,
    status: data.status ?? existing?.status ?? 'pending',
    userId: data.userId ?? existing?.userId,
    pendingInput: data.pendingInput ?? existing?.pendingInput,
    createdAt: existing?.createdAt ?? now,
    updatedAt: now,
  };

  // Use in-memory store
  getMemoryStore().set(record.authId, record);
  return cloneRecord(record);
}

export async function getArcadeAuthRecord(authId: string): Promise<ArcadeAuthRecord | null> {
  // Use in-memory store
  const record = getMemoryStore().get(authId);
  return record ? cloneRecord(record) : null;
}

export async function updateArcadeAuthRecord(
  authId: string,
  updates: Partial<Omit<ArcadeAuthRecord, 'authId' | 'createdAt'>>
): Promise<ArcadeAuthRecord | null> {
  const existing = await getArcadeAuthRecord(authId);
  if (!existing) {
    return null;
  }

  const next: ArcadeAuthRecord = {
    ...existing,
    ...updates,
    updatedAt: new Date().toISOString(),
  };

  // Use in-memory store
  getMemoryStore().set(authId, next);
  return cloneRecord(next);
}

export async function deleteArcadeAuthRecord(authId: string): Promise<void> {
  // Delete from memory store
  getMemoryStore().delete(authId);
}

export function listArcadeAuthRecords(): ArcadeAuthRecord[] {
  // This only returns memory store records
  // For Redis, we'd need a different approach (e.g., scan with pattern)
  return Array.from(getMemoryStore().values()).map(cloneRecord);
}
