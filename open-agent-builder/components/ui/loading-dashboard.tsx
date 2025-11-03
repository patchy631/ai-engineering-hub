"use client";

import { useEffect, useRef } from "react";

import data from "@/components/shared/effects/flame/hero-flame-data.json";
import { cn } from "@/utils/cn";
import { setIntervalOnVisible } from "@/utils/set-timeout-on-visible";

function LoadingDashboardFlame({ flameClassName }: { flameClassName: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let index = 0;

    const interval = setIntervalOnVisible({
      element: wrapperRef.current,
      callback: () => {
        index++;
        if (index >= data.length) index = 0;

        if (ref.current) {
          ref.current.innerHTML = data[index];
        }
      },
      interval: 85,
    });

    return () => interval?.();
  }, []);

  return (
    <div
      className="pointer-events-none select-none flex items-center justify-center"
      ref={wrapperRef}
    >
      <div className="overflow-clip relative h-182 flex items-center justify-center">
        <div
          className={cn(
            "text-black-alpha-32 font-ascii fc-decoration",
            flameClassName,
          )}
          dangerouslySetInnerHTML={{ __html: data[0] }}
          ref={ref}
          style={{
            whiteSpace: "pre",
            fontSize: "9px",
            lineHeight: "11px",
          }}
        />
      </div>
    </div>
  );
}

export default function LoadingDashboard({
  flameClassName,
}: {
  flameClassName: string;
}) {
  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen w-full">
      <LoadingDashboardFlame flameClassName={flameClassName} />
      <p className="text-body-medium text-black-alpha-20 mt-24">Loading...</p>
    </div>
  );
}
