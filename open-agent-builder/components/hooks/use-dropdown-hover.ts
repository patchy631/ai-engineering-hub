import { useCallback, useRef } from "react";
import { animate, cubicBezier } from "framer-motion";

export const useDropdownHover = () => {
  const backgroundRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<number | null>(null);

  const onMouseEnter = useCallback((e: React.MouseEvent<HTMLElement>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const t = e.target as HTMLElement;
    const target =
      t instanceof HTMLButtonElement
        ? t
        : (t.closest("button") as HTMLButtonElement);

    if (!target || !backgroundRef.current) return;

    if (backgroundRef.current) {
      // Scale animation sequence like marketing webapp
      animate(backgroundRef.current, { scale: 0.98, opacity: 1 }).then(() => {
        if (backgroundRef.current) {
          animate(backgroundRef.current!, { scale: 1 });
        }
      });

      // Y position animation - align with menu item
      animate(
        backgroundRef.current,
        {
          y: target.offsetTop,
        },
        {
          ease: cubicBezier(0.1, 0.1, 0.25, 1),
          duration: 0.2,
        },
      );
    }
  }, []);

  const onMouseLeave = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = window.setTimeout(() => {
      if (backgroundRef.current) {
        animate(backgroundRef.current, { scale: 1, opacity: 0 });
      }
    }, 100);
  }, []);

  const onClick = useCallback((e: React.MouseEvent<HTMLElement>) => {
    if (!backgroundRef.current) return;

    // Click animation - scale down then up
    animate(backgroundRef.current, { scale: 0.98 }, { duration: 0.1 }).then(
      () => {
        if (backgroundRef.current) {
          animate(backgroundRef.current, { scale: 1 }, { duration: 0.1 });
        }
      },
    );
  }, []);

  return {
    backgroundRef,
    onMouseEnter,
    onMouseLeave,
    onClick,
  };
};
