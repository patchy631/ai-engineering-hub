"use client";

import { animate } from "motion";
import { useEffect, useRef } from "react";

import { cn } from "@/utils/cn";
import initCanvas from "@/utils/init-canvas";

export default function EndpointsMcp({
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

    let activeIndex = 5;
    const rowAlphas = [0.12, 0.2, 0.4, 0.4, 1, 1, 1, 0.4, 0.2];

    const scaler = size / 20;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#FF4C00";

      for (let i = 0; i < 9; i++) {
        ctx.globalAlpha = rowAlphas[i];

        ctx.fillRect(
          (5 + (i % 3) * 4) * scaler,
          (5 + Math.floor(i / 3) * 4) * scaler,
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
      activeIndex = (activeIndex + 1) % 9;

      rowAlphas.forEach((alpha, index) => {
        let targetAlpha = alpha;

        if (index === activeIndex) targetAlpha = 1;
        else if (index === (activeIndex - 1 + 9) % 9) targetAlpha = 1;
        else if (index === (activeIndex - 2 + 9) % 9) targetAlpha = 1;
        else if (index === (activeIndex - 3 + 9) % 9) targetAlpha = 0.4;
        else if (index === (activeIndex - 4 + 9) % 9) targetAlpha = 0.2;
        else if (index === (activeIndex - 5 + 9) % 9) targetAlpha = 0.2;
        else if (index === (activeIndex - 6 + 9) % 9) targetAlpha = 0.12;
        else if (index === (activeIndex - 7 + 9) % 9) targetAlpha = 0.12;
        else if (index === (activeIndex - 8 + 9) % 9) targetAlpha = 0.4;

        animate(alpha, targetAlpha, {
          duration: 30 / 1000,
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

      if (activeIndex === 7) runCount += 1;

      if ((runCount === 2 || !isActive) && activeIndex === 6) return;

      timeouts.push(
        window.setTimeout(() => {
          cycle();
        }, 30),
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
  }, [size, triggerOnHover]);

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
