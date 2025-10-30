/* eslint-disable @stylistic/array-element-newline */
"use client";

import { animate } from "motion";
import { useEffect, useRef } from "react";

import initCanvas from "@/utils/init-canvas";

export default function EndpointsExtract({ size = 20 }: { size?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = initCanvas(canvas);

    let isRunning = false;
    let isActive = false;

    let diff = 0;
    const defaultRowAlphas = [
      0.4, 0.04, 0.2, 0.4, 0.2, 0, 0, 0.04, 0.04, 0, 0, 0.2, 0.4, 0.2, 0.04,
      0.4,
    ];

    const differs = Array.from({ length: 16 }, () => 0.2 + Math.random() * 0.2);

    const scaler = size / 20;

    const render = () => {
      ctx.fillStyle = "#FF4C00";
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < 16; i++) {
        if ([5, 6, 9, 10].includes(i)) continue;

        ctx.globalAlpha = defaultRowAlphas[i] + diff * differs[i];
        ctx.globalAlpha =
          Math.min(ctx.globalAlpha, 0.4) - Math.max(ctx.globalAlpha - 0.4, 0);

        ctx.fillRect(
          (3 + (i % 4) * 4) * scaler,
          (3 + Math.floor(i / 4) * 4) * scaler,
          2 * scaler,
          2 * scaler,
        );
      }

      ctx.globalAlpha = 1;
      ctx.fillRect(7, 7, 6, 2);
      ctx.globalAlpha = 0.4;
      ctx.fillRect(7, 11, 2 + diff * 4, 2);

      if (isRunning) {
        requestAnimationFrame(render);
      }
    };

    const timeouts: number[] = [];

    let runCount = 0;

    const duration = 300;

    const cycle = () => {
      isRunning = true;

      animate(diff, 1, {
        duration: duration / 1000,
        onUpdate: (value) => {
          diff = value < 0.5 ? value * 2 : 1 - (value - 0.5) * 2;
        },
      });

      timeouts.forEach((timeout) => {
        window.clearTimeout(timeout);
      });

      timeouts.push(
        window.setTimeout(
          () => {
            isRunning = false;
          },
          Math.max(duration, 300),
        ),
      );

      runCount += 1;

      if (runCount === 3 || !isActive) return;

      timeouts.push(
        window.setTimeout(() => {
          cycle();
        }, duration),
      );
    };

    const activate = () => {
      if (isActive) return;

      isActive = true;

      runCount = 0;
      cycle();
      render();
    };

    const deactivate = () => {
      if (!isActive) return;

      isActive = false;
    };

    render();
    canvas.addEventListener("resize", render);

    const group = canvasRef.current!.closest(".group");

    if (group) {
      group.addEventListener("mouseenter", activate);
      group.addEventListener("mouseleave", deactivate);

      return () => {
        group.removeEventListener("mouseenter", activate);
        group.removeEventListener("mouseleave", deactivate);
      };
    }
  }, [size]);

  return <canvas ref={canvasRef} style={{ width: size, height: size }} />;
}
