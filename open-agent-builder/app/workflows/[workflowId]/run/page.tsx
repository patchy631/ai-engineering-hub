"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import WorkflowBuilder from "@/components/app/(home)/sections/workflow-builder/WorkflowBuilder";

export default function WorkflowRunPage({ params }: { params: Promise<{ workflowId: string }> }) {
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    params.then(({ workflowId }) => {
      setWorkflowId(workflowId);
    });
  }, [params]);

  const handleBack = () => {
    router.push('/');
  };

  if (!workflowId) {
    return <div>Loading...</div>;
  }

  // This page auto-opens the execution panel
  return (
    <WorkflowBuilder
      onBack={handleBack}
      initialWorkflowId={workflowId}
      initialTemplateId={null}
    />
  );
}
