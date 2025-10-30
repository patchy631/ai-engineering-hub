"use client";

import { animate } from "motion";
import { useEffect, useRef } from "react";

import { cn } from "@/utils/cn";
import initCanvas from "@/utils/init-canvas";

export default function EndpointsScrape({
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

    let activeRow = 2;
    const rowAlphas = [0.2, 0.4, 1, 0.12];

    const scaler = size / 20;

    const render = () => {
      ctx.fillStyle = "#FF4C00";
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < 16; i++) {
        if (disabledCells && disabledCells.includes(i)) continue;

        ctx.globalAlpha = rowAlphas[Math.floor(i / 4)];

        ctx.fillRect(
          (3 + (i % 4) * 4) * scaler,
          (3 + Math.floor(i / 4) * 4) * scaler,
          2 * scaler,
          2 * scaler,
        );
      }

      if (isRunning) {
        requestAnimationFrame(render);
      }
    };

    const timeouts: number[] = [];

    let runCount = 0;

    const cycle = () => {
      isRunning = true;
      activeRow = (activeRow + 1) % 5;

      rowAlphas.forEach((alpha, index) => {
        let targetAlpha = alpha;

        if (index === activeRow) targetAlpha = 1;
        else if (index === (activeRow + 1) % 4) targetAlpha = 0.12;
        else if (index === (activeRow + 2) % 4) targetAlpha = 0.2;
        else if (index === (activeRow + 3) % 4) targetAlpha = 0.4;

        animate(alpha, targetAlpha, {
          duration: 0.05,
          onUpdate: (value) => {
            rowAlphas[index] = value;
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

      if (activeRow === 3) runCount += 1;

      if ((runCount === 2 || !isActive) && activeRow === 2) return;

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
