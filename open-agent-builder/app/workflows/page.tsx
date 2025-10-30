"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function WorkflowsPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to home
    router.push('/');
  }, [router]);

  return null;
}
