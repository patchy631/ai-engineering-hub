"use client";

import { animate } from "motion";
import { useEffect, useRef } from "react";

import { cn } from "@/utils/cn";
import initCanvas from "@/utils/init-canvas";

export default function EndpointsExtract({
  active,
  disabledCells,
  alwaysHeat = false,
  triggerOnHover = false,
  size = 20,
}: {
  active?: boolean;
  disabledCells?: number[];
  alwaysHeat?: boolean;
  triggerOnHover?: boolean;
  size?: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const fnRefs = useRef<{
    activate: () => void;
    deactivate: () => void;
  }>({ activate: () => {}, deactivate: () => {} });

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = initCanvas(canvas);

    let isRunning = false;
    let isActive = false;

    let activeCol = 0;
    const colAlphas = [1, 0.4, 0.2, 0.12];

    const scaler = size / 20;

    const render = () => {
      ctx.fillStyle = "#FF4C00";
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw Extract pattern - represents structured data extraction
      // Draw columns to represent data fields
      for (let col = 0; col < 4; col++) {
        ctx.globalAlpha = colAlphas[col];

        // Draw vertical bars of different heights to represent extracted data
        const heights = [3, 2, 3, 1];
        const startY = [1, 2, 1, 3];

        for (let row = 0; row < heights[col]; row++) {
          ctx.fillRect(
            (3 + col * 4) * scaler,
            (3 + startY[col] * 2 + row * 4) * scaler,
            2 * scaler,
            2 * scaler,
          );
        }
      }

      if (isRunning) {
        requestAnimationFrame(render);
      }
    };

    const timeouts: number[] = [];

    let runCount = 0;

    const cycle = () => {
      isRunning = true;
      activeCol = (activeCol + 1) % 4;

      colAlphas.forEach((alpha, index) => {
        let targetAlpha = alpha;

        if (index === activeCol) targetAlpha = 1;
        else if (index === (activeCol + 1) % 4) targetAlpha = 0.12;
        else if (index === (activeCol + 2) % 4) targetAlpha = 0.2;
        else if (index === (activeCol + 3) % 4) targetAlpha = 0.4;

        animate(alpha, targetAlpha, {
          duration: 0.05,
          onUpdate: (value) => {
            colAlphas[index] = value;
          },
        });
      });

      timeouts.forEach((timeout) => {
        window.clearTimeout(timeout);
      });

      timeouts.push(
        window.setTimeout(() => {
          isRunning = false;
        }, 400),
      );

      if (activeCol === 3) runCount += 1;

      if ((runCount === 2 || !isActive) && activeCol === 0) return;

      timeouts.push(
        window.setTimeout(() => {
          cycle();
        }, 50),
      );
    };

    fnRefs.current = {
      activate: () => {
        if (isActive) return;

        isActive = true;

        runCount = 0;
        cycle();
        render();
      },
      deactivate: () => {
        if (!isActive) return;

        isActive = false;
      },
    };

    render();
    canvas.addEventListener("resize", render);

    if (triggerOnHover) {
      const group = canvasRef.current!.closest(".group");

      if (group) {
        group.addEventListener("mouseenter", fnRefs.current.activate);
        group.addEventListener("mouseleave", fnRefs.current.deactivate);

        return () => {
          group.removeEventListener("mouseenter", fnRefs.current.activate);
          group.removeEventListener("mouseleave", fnRefs.current.deactivate);
        };
      }
    }
  }, [disabledCells, size, triggerOnHover]);

  useEffect(() => {
    if (triggerOnHover) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && active) {
          fnRefs.current.activate();
        } else {
          fnRefs.current.deactivate();
        }
      },
      { threshold: 0.5 },
    );

    observer.observe(canvasRef.current!);

    return () => {
      observer.disconnect();
    };
  }, [active, triggerOnHover]);

  return (
    <canvas
      className={cn(
        alwaysHeat
          ? ""
          : [
              "[&.grayscale]:opacity-60 transition-[filter,opacity]",
              !active && "grayscale",
            ],
      )}
      ref={canvasRef}
      style={{ width: size, height: size }}
    />
  );
}
