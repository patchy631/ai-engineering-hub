import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useEffect, useRef } from "react";

/**
 * Real-time approval watcher using Convex subscriptions
 *
 * Why Convex is perfect for human-in-the-loop approvals:
 * --------------------------------------------------------
 * 1. REAL-TIME: Automatically updates when approval status changes (no polling!)
 * 2. REACTIVE: Component re-renders when someone approves/rejects
 * 3. PERSISTENT: Survives server restarts (unlike in-memory stores)
 * 4. EFFICIENT: Only sends updates when data actually changes
 * 5. AUTOMATIC: No need to manually subscribe/unsubscribe
 *
 * Example workflow:
 * -----------------
 * 1. Workflow hits "User Approval" node → pauses execution
 * 2. Create approval record in Convex
 * 3. Frontend watches approval with this hook
 * 4. User approves via UI
 * 5. Convex instantly notifies all watchers
 * 6. Workflow automatically resumes!
 *
 * Usage:
 * ```tsx
 * const { status, approval, isApproved, isRejected, isPending } = useApprovalWatch(approvalId);
 *
 * if (isPending) {
 *   return <ApprovalButton onApprove={() => approveWorkflow()} />;
 * }
 *
 * if (isApproved) {
 *   // Workflow will auto-resume!
 *   return <div>Approved - workflow continuing...</div>;
 * }
 * ```
 */
export function useApprovalWatch(approvalId: string | null | undefined) {
  const prevStatusRef = useRef<string | null>(null);

  // Real-time subscription - updates instantly when approval changes!
  const result = useQuery(
    api.approvals.watchStatus,
    approvalId ? { approvalId } : "skip"
  );

  const status = result?.status || "not_found";
  const approval = result?.approval;

  const isPending = status === "pending";
  const isApproved = status === "approved";
  const isRejected = status === "rejected";
  const isResolved = isApproved || isRejected;

  // Detect status changes for callbacks
  useEffect(() => {
    if (status && status !== prevStatusRef.current) {
      console.log(`Approval ${approvalId} status changed: ${prevStatusRef.current} → ${status}`);
      prevStatusRef.current = status;
    }
  }, [status, approvalId]);

  return {
    status,
    approval,
    isPending,
    isApproved,
    isRejected,
    isResolved,
    isLoading: result === undefined,
  };
}

/**
 * Hook for watching multiple pending approvals for a workflow
 *
 * Usage:
 * ```tsx
 * const { pendingApprovals, hasPending } = usePendingApprovals(workflowId);
 *
 * return (
 *   <div>
 *     {hasPending && (
 *       <div>
 *         {pendingApprovals.map(approval => (
 *           <ApprovalCard key={approval.approvalId} approval={approval} />
 *         ))}
 *       </div>
 *     )}
 *   </div>
 * );
 * ```
 */
export function usePendingApprovals(workflowId: string | null | undefined) {
  const approvals = useQuery(
    api.approvals.listPending,
    workflowId ? { workflowId: workflowId as any } : "skip"
  );

  const pendingApprovals = approvals || [];
  const hasPending = pendingApprovals.length > 0;

  return {
    pendingApprovals,
    hasPending,
    count: pendingApprovals.length,
  };
}

/**
 * Hook for watching approvals for a specific execution
 *
 * Useful for showing "Waiting for approval" status in execution panel
 */
export function useExecutionApprovals(executionId: string | null | undefined) {
  const approvals = useQuery(
    api.approvals.getByExecution,
    executionId ? { executionId } : "skip"
  );

  const allApprovals = approvals || [];
  const pendingApprovals = allApprovals.filter(a => a.status === "pending");
  const hasPending = pendingApprovals.length > 0;

  return {
    approvals: allApprovals,
    pendingApprovals,
    hasPending,
    isPaused: hasPending, // Execution is paused if any approvals are pending
  };
}
