import { useEffect, useRef, useState } from "react";

const CHARACTERS = "!@#$%^&*()_+-=[]{}|;:,.<>?";

export default function ScrambleText({
  text,
  delay,
  duration = 1.5,
  isInView,
}: {
  text: string;
  delay: number;
  duration?: number;
  isInView: boolean;
}) {
  const [displayText, setDisplayText] = useState(text); // Initialize with final text to avoid hydration mismatch
  const [isClient, setIsClient] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const startTimeRef = useRef<number | undefined>(undefined);
  const [hasAnimated, setHasAnimated] = useState(false);
  const containerRef = useRef<HTMLSpanElement>(null);

  // Set client-side flag after mount
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Set initial width
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.visibility = "hidden";
      containerRef.current.textContent = text;
      const width = containerRef.current.offsetWidth;
      containerRef.current.textContent = displayText;
      containerRef.current.style.width = `${width}px`;
      containerRef.current.style.display = "inline-block";
      containerRef.current.style.visibility = "visible";
    }
  }, [text]);

  // Start animation only on client after initial render
  useEffect(() => {
    if (!isClient || !isInView || hasAnimated) return;

    // Set initial scrambled text
    setDisplayText(
      Array(text.length)
        .fill(0)
        .map(() => CHARACTERS[Math.floor(Math.random() * CHARACTERS.length)])
        .join(""),
    );

    const timeoutId = setTimeout(() => {
      startTimeRef.current = Date.now();

      const updateText = () => {
        const elapsed = Date.now() - (startTimeRef.current || 0);
        const progress = Math.min(elapsed / (duration * 1000), 1);

        if (progress < 1) {
          const scrambledLength = Math.floor((1 - progress) * text.length);
          const finalLength = text.length - scrambledLength;

          setDisplayText(
            text.slice(0, finalLength) +
              Array(scrambledLength)
                .fill(0)
                .map(
                  () =>
                    CHARACTERS[Math.floor(Math.random() * CHARACTERS.length)],
                )
                .join(""),
          );

          intervalRef.current = setTimeout(updateText, 30);
        } else {
          setDisplayText(text);
          setHasAnimated(true);
        }
      };

      updateText();
    }, delay * 1000);

    return () => {
      clearTimeout(timeoutId);
      if (intervalRef.current) {
        clearTimeout(intervalRef.current);
      }
    };
  }, [text, delay, duration, isInView, hasAnimated, isClient]);

  return (
    <span
      ref={containerRef}
      className="inline-block whitespace-pre"
      style={{ fontVariantNumeric: "tabular-nums" }}
    >
      {displayText}
    </span>
  );
}
