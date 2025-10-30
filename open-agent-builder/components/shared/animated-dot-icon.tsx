"use client";

import { animate } from "framer-motion";
import { useEffect, useRef } from "react";
import { cn } from "@/utils/cn";

interface AnimatedDotIconProps {
  active?: boolean;
  alwaysHeat?: boolean;
  triggerOnHover?: boolean;
  size?: number;
  className?: string;
  pattern?:
    | "usage"
    | "api-keys"
    | "settings"
    | "overview"
    | "team"
    | "billing"
    | "account-settings"
    | "admin"
    | "domain-checker"
    | "extract-playground"
    | "extract"
    | "logs"
    | "playground"
    | "teams";
}

const initCanvas = (canvas: HTMLCanvasElement) => {
  const { width, height } = canvas.getBoundingClientRect();
  const ctx = canvas.getContext("2d")!;

  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  const upscaleCanvas = () => {
    const scale = window.visualViewport?.scale || 1;
    const dpr = (window.devicePixelRatio || 1) * scale;

    canvas.width = width * dpr;
    canvas.height = height * dpr;

    ctx.scale(dpr, dpr);

    canvas.dispatchEvent(new Event("resize"));
  };

  upscaleCanvas();

  const handleResize = () => {
    setTimeout(upscaleCanvas, 500);
  };

  window.addEventListener("resize", handleResize);
  window.visualViewport?.addEventListener("resize", handleResize);

  return ctx;
};

// Pattern definitions for different pages
const patterns = {
  usage: {
    grid: [
      [10, 11, 12, 14, 15, 16],
      [3, 7, 19, 23],
      [0, 2, 24, 26],
      [27, 28, 29, 31, 32, 33],
    ],
    gridSize: 7,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  "api-keys": {
    grid: [[12], [10, 14], [8, 16], [6, 18], [4, 5, 19, 20]],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  settings: {
    grid: [
      [0, 1, 2, 3, 4],
      [5, 9],
      [10, 14],
      [15, 19],
      [20, 21, 22, 23, 24],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  overview: {
    grid: [
      [24],
      [16, 18, 30, 32],
      [8, 12, 36, 40],
      [0, 3, 6, 21, 27, 42, 45, 48],
    ],
    gridSize: 7,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  team: {
    grid: [
      [6, 7, 8],
      [11, 12, 13],
      [16, 17, 18],
      [0, 4, 20, 24],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  teams: {
    grid: [
      [6, 7, 8],
      [11, 12, 13],
      [16, 17, 18],
      [0, 4, 20, 24],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  billing: {
    grid: [
      [0, 4],
      [5, 6, 8, 9],
      [10, 11, 13, 14],
      [15, 19],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  "account-settings": {
    grid: [
      [2, 7, 12, 17, 22],
      [5, 10, 15, 20],
      [8, 13, 18],
      [11, 16],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  admin: {
    grid: [
      [0, 1, 2, 3, 4],
      [5, 14],
      [10, 11, 12, 13],
      [15, 24],
      [20, 21, 22, 23, 24],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  "domain-checker": {
    grid: [
      [12, 13, 14],
      [7, 11, 15, 19],
      [2, 6, 20, 24],
      [0, 1, 25, 26],
    ],
    gridSize: 6,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  "extract-playground": {
    grid: [
      [5, 10, 15, 20],
      [6, 11, 16, 21],
      [7, 12, 17, 22],
      [8, 13, 18, 23],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  extract: {
    grid: [[12], [7, 17], [2, 6, 18, 22], [0, 1, 3, 4, 20, 21, 23, 24]],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  logs: {
    grid: [
      [0, 5, 10, 15, 20],
      [1, 6, 11, 16, 21],
      [2, 7, 12, 17, 22],
      [3, 8, 13, 18, 23],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
  playground: {
    grid: [
      [6, 8, 16, 18],
      [10, 11, 12, 13, 14],
      [5, 9, 15, 19],
      [0, 4, 20, 24],
    ],
    gridSize: 5,
    cellSize: 2,
    spacing: 2,
    offset: 3,
  },
};

export function AnimatedDotIcon({
  active = true,
  alwaysHeat = false,
  triggerOnHover = false,
  size = 20,
  className,
  pattern = "usage",
}: AnimatedDotIconProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const fnRefs = useRef<{
    activate: () => void;
    deactivate: () => void;
  }>({ activate: () => {}, deactivate: () => {} });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = initCanvas(canvas);
    const config = patterns[pattern];

    let isRunning = false;
    let isActive = false;

    let activeGroup = 0;
    const rowAlphas = [0.2, 0.4, 1, 0.04];

    const scaler = size / 20;

    const render = () => {
      ctx.fillStyle = "#fa5d19";
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const group of config.grid.slice(0, 4)) {
        const groupIndex = config.grid.indexOf(group);
        ctx.globalAlpha = rowAlphas[groupIndex];

        for (const index of group) {
          ctx.fillRect(
            (config.offset + (index % config.gridSize) * config.spacing) *
              scaler,
            (config.offset +
              Math.floor(index / config.gridSize) * config.spacing) *
              scaler,
            config.cellSize * scaler,
            config.cellSize * scaler,
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
  }, [triggerOnHover, size, pattern]);

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
        className,
      )}
      ref={canvasRef}
      style={{ width: size, height: size }}
    />
  );
}
