import { cn } from "@/utils/cn";
import React, { useRef, useState, useEffect } from "react";

export function JsonErrorHighlighter({
  value,
  error,
  onChange,
  onBlur,
  className,
  style,
}: {
  value: string;
  error: { line?: number; column?: number; message: string } | null;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onBlur?: () => void;
  className?: string;
  style?: React.CSSProperties;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const preRef = useRef<HTMLPreElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);
  const [scrollInfo, setScrollInfo] = useState({
    firstVisible: 0,
    lastVisible: 20,
    scrollTop: 0,
    lineHeight: 24,
    clientHeight: 250,
  });

  const lines = value.split("\n");
  const errorLineIdx = (error?.line ?? 1) - 1;

  // Calculate visible lines on scroll or resize
  const recalcVisibleLines = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 24;
    const scrollTop = textarea.scrollTop;
    const clientHeight = textarea.clientHeight;
    const firstVisible = Math.floor(scrollTop / lineHeight);
    const lastVisible = Math.min(
      lines.length - 1,
      Math.ceil((scrollTop + clientHeight) / lineHeight),
    );
    setScrollInfo({
      firstVisible,
      lastVisible,
      scrollTop,
      lineHeight,
      clientHeight,
    });
  };

  useEffect(() => {
    recalcVisibleLines();
    // Sync overlay height with textarea
    const handleResize = () => recalcVisibleLines();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [value]);

  // Attach scroll handler
  const handleScroll = () => {
    recalcVisibleLines();
    if (textareaRef.current && preRef.current) {
      preRef.current.scrollTop = textareaRef.current.scrollTop;
      preRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  // Only render visible lines in <pre>
  const visibleLines = lines.slice(
    scrollInfo.firstVisible,
    scrollInfo.lastVisible + 1,
  );

  return (
    <div
      className={cn(
        "w-full h-full relative font-mono text-foreground text-sm min-h-[250px] overflow-hidden focus:border-none focus-visible:border-none focus-visible:outline-none",
        className,
      )}
      style={style}
    >
      {/* Highlight overlay */}
      {error?.line && (
        <pre
          ref={preRef}
          className="absolute inset-0 pointer-events-none select-none text-transparent whitespace-pre-wrap break-words focus-visible:outline-none shadow-none border-none rounded-md"
          aria-hidden="true"
          style={{
            fontFamily: "inherit",
            fontSize: "inherit",
            lineHeight: "1.5",
            margin: 0,
            padding: "8px 12px",
            paddingLeft: "0",
            boxSizing: "border-box",
            minHeight: "250px",
            transform: `translateY(-${scrollInfo.scrollTop}px)`,
          }}
        >
          <div style={{ height: scrollInfo.firstVisible * 1.5 + "em" }} />
          {visibleLines.map((line, idx) => {
            const globalIdx = idx + scrollInfo.firstVisible;
            if (globalIdx === errorLineIdx) {
              return (
                <div
                  key={globalIdx}
                  className="bg-red-500/20"
                  style={{ display: "block" }}
                >
                  {line}
                </div>
              );
            }
            return <div key={globalIdx}>{line}</div>;
          })}
        </pre>
      )}
      {/* Line numbers overlay */}
      <div
        ref={lineNumbersRef}
        className="absolute left-0 top-0 bottom-0 pointer-events-none select-none text-muted-foreground/60 text-xs border-r border-border/50 bg-muted/20 rounded-l-md h-fit"
        style={{
          width: "3rem",
          padding: "11px 9px",
          boxSizing: "border-box",
          fontFamily: "inherit",
          fontSize: "0.75em",
          lineHeight: "1.5",
          transform: `translateY(-${scrollInfo.scrollTop}px)`,
        }}
      >
        <div
          style={{
            height: scrollInfo.firstVisible * scrollInfo.lineHeight + "px",
          }}
        />
        {visibleLines.map((_, idx) => {
          const globalIdx = idx + scrollInfo.firstVisible;
          return (
            <div
              key={globalIdx}
              className="pr-2"
              style={{
                height: "16px",
                marginTop: idx === 0 ? 0 : "5px",
                paddingTop: "2px",
              }}
            >
              {globalIdx + 1}
            </div>
          );
        })}
      </div>
      {/* Textarea */}
      <textarea
        ref={textareaRef}
        className={cn(
          "absolute inset-0 resize-none bg-transparent border rounded-md text-black dark:text-white focus:overline-none focus:border-zinc-200 focus-visible:border-zinc-200 focus-visible:outline-none",
          error?.message ? "!border-destructive" : "border-zinc-200",
        )}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        onScroll={handleScroll}
        spellCheck={false}
        style={{
          fontFamily: "inherit",
          fontSize: "inherit",
          lineHeight: "1.5",
          margin: 0,
          padding: "8px 12px 8px 4rem", // Add left padding to account for line numbers
          boxSizing: "border-box",
          minHeight: "250px",
          background: "transparent",
          color: "inherit",
          zIndex: 1,
          outline: "none",
          boxShadow: "none",
        }}
      />
      {/* Error message overlay */}
      {error?.message && (
        <div
          className="absolute left-0 right-0 bottom-0 px-3 py-1 text-xs text-white bg-red-500/90 z-10 pointer-events-none"
          style={{
            fontFamily: "inherit",
            fontSize: "0.85em",
            borderBottomLeftRadius: 6,
            borderBottomRightRadius: 6,
          }}
        >
          {error.message}
        </div>
      )}
    </div>
  );
}
