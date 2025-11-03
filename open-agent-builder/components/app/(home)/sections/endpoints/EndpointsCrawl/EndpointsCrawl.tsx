"use client";

import { animate } from "motion";
import { useEffect, useRef } from "react";

import { cn } from "@/utils/cn";
import initCanvas from "@/utils/init-canvas";

export default function EndpointsCrawl({
  active,
  alwaysHeat = false,
  triggerOnHover = false,
  size = 20,
}: {
  active?: boolean;
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

    let activeGroup = 0;
    const rowAlphas = [0.2, 0.4, 1, 0.04];

    const grid = [
      [24],
      [16, 18, 30, 32],
      [8, 12, 36, 40],
      [0, 3, 6, 21, 27, 42, 45, 48],
    ];

    const scaler = size / 20;

    const render = () => {
      ctx.fillStyle = "#FF4C00";
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const group of grid.slice(0, 4)) {
        const groupIndex = grid.indexOf(group);
        ctx.globalAlpha = rowAlphas[groupIndex];

        for (const index of group) {
          ctx.fillRect(
            (3 + (index % 7) * 2) * scaler,
            (3 + Math.floor(index / 7) * 2) * scaler,
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
      activeGroup = (activeGroup + 1) % 5;

      rowAlphas.forEach((alpha, index) => {
        let targetAlpha = alpha;

        if (index === activeGroup) targetAlpha = 1;
        else if (index === (activeGroup + 1) % 4) targetAlpha = 0.12;
        else if (index === (activeGroup + 2) % 4) targetAlpha = 0.2;
        else if (index === (activeGroup + 3) % 4) targetAlpha = 0.4;

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
        }, 300),
      );

      if (activeGroup === 3) runCount += 1;

      if ((runCount === 2 || !isActive) && activeGroup === 2) return;

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
  }, [triggerOnHover, size]);

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
