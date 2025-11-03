"use client";

import { useState, useEffect } from "react";
import ScrambleText from "@/components/ui/motion/scramble-text";

export function UsageLoadingText({ text = "Loading..." }: { text?: string }) {
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    setIsInView(true);
  }, []);

  return (
    <div className="text-xs text-zinc-500">
      <ScrambleText text={text} delay={0} duration={1} isInView={isInView} />
    </div>
  );
}
