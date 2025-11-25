"use client";

import { useEffect, useRef, useState } from "react";

export default function LivePreviewFrame({
  sessionId,
  onScrapeComplete,
  children,
}: {
  sessionId: string;
  children: React.ReactNode;
  onScrapeComplete?: () => void;
}) {
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const initialPositionSetRef = useRef(false);
  const idleStartTimerRef = useRef<NodeJS.Timeout | null>(null);
  const idleMoveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);
  const [cursorPosition, setCursorPosition] = useState<{
    x: number;
    y: number;
  }>({ x: 980, y: 54 });
  const [targetPosition, setTargetPosition] = useState<{
    x: number;
    y: number;
  }>({ x: 980, y: 54 });
  const [isIdle, setIsIdle] = useState(false);

  // Function to start the random idle movement sequence
  const scheduleNextIdleMove = () => {
    if (idleMoveTimerRef.current) {
      clearTimeout(idleMoveTimerRef.current);
    }
    const randomDelay = Math.random() * 500 + 500; // 500ms to 1000ms
    idleMoveTimerRef.current = setTimeout(() => {
      if (isIdle) {
        // Check if still idle
        const randomOffsetX = (Math.random() - 0.5) * 10; // -5 to +5 pixels
        const randomOffsetY = (Math.random() - 0.5) * 10;
        // Update target slightly - the main animation loop will handle the movement
        setTargetPosition((prevTarget) => ({
          x: prevTarget.x + randomOffsetX,
          y: prevTarget.y + randomOffsetY,
        }));
        scheduleNextIdleMove(); // Schedule the next one
      }
    }, randomDelay);
  };

  // Effect to handle starting/stopping idle movement sequence
  useEffect(() => {
    if (isIdle) {
      scheduleNextIdleMove();
    } else {
      if (idleMoveTimerRef.current) {
        clearTimeout(idleMoveTimerRef.current);
      }
    }
    // Cleanup function for this effect
    return () => {
      if (idleMoveTimerRef.current) {
        clearTimeout(idleMoveTimerRef.current);
      }
    };
  }, [isIdle]);

  // Main Animation effect (runs continuously)
  useEffect(() => {
    let animationFrameId: number | null = null;
    const step = () => {
      setCursorPosition((currentPos) => {
        const dx = targetPosition.x - currentPos.x;
        const dy = targetPosition.y - currentPos.y;
        const isClose = Math.abs(dx) < 0.1 && Math.abs(dy) < 0.1;

        if (isClose) {
          // Reached target
          if (!isIdle && !idleStartTimerRef.current) {
            // Only start the idle timer if not already idle and no timer is running
            idleStartTimerRef.current = setTimeout(() => {
              setIsIdle(true);
              idleStartTimerRef.current = null; // Clear ref after timer runs
            }, 5000);
          }
          if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
          }
          return targetPosition; // Snap to final position
        } else {
          // Moving towards target
          // If we were waiting to go idle, cancel it because we're moving again
          if (idleStartTimerRef.current) {
            clearTimeout(idleStartTimerRef.current);
            idleStartTimerRef.current = null;
          }
          // Ensure idle state is false if we are moving significantly
          if (isIdle) setIsIdle(false);

          const nextX = currentPos.x + dx * 0.05; // Keep slow easing for now
          const nextY = currentPos.y + dy * 0.05;
          animationFrameId = requestAnimationFrame(step);
          return { x: nextX, y: nextY };
        }
      });
    };

    // Start animation frame loop
    animationFrameId = requestAnimationFrame(step);

    // Cleanup function for main animation loop
    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      // Also clear idle start timer on unmount or if target changes causing effect re-run
      if (idleStartTimerRef.current) {
        clearTimeout(idleStartTimerRef.current);
      }
    };
  }, [targetPosition]); // Re-run main loop logic if targetPosition changes

  const cleanupConnection = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    // Cancel animation frame (handled in effect cleanup, but good practice here too)
    // Clear timers
    if (idleStartTimerRef.current) clearTimeout(idleStartTimerRef.current);
    if (idleMoveTimerRef.current) clearTimeout(idleMoveTimerRef.current);
    // Reset state
    setCursorPosition({ x: 0, y: 0 });
    setTargetPosition({ x: 0, y: 0 });
    setIsIdle(false);
    initialPositionSetRef.current = false;
  };

  useEffect(() => {
    if (onScrapeComplete) {
      cleanupConnection();
    }
  }, [onScrapeComplete]);

  const connect = () => {
    setIsConnecting(true);
    // Clear any existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Create new WebSocket connection
    const wsUrl = `wss://api.firecrawl.dev/agent-livecast?userProvidedId=${sessionId}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.addEventListener("open", () => {
        console.log("Connected - Streaming frames...");
        setIsConnecting(false);
        // Clear any pending reconnection attempts
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      });

      ws.addEventListener("message", (event) => {
        try {
          // Try to handle as raw base64 first
          if (
            typeof event.data === "string" &&
            event.data.startsWith("data:image")
          ) {
            if (imgRef.current) {
              imgRef.current.src = event.data;
              return;
            }
          }

          // If not direct image data, try parsing as JSON
          const data = JSON.parse(event.data);

          if (data.mouseCoordinates) {
            let { x, y } = data.mouseCoordinates;

            // --- Interrupt Idle State ---
            if (idleStartTimerRef.current) {
              clearTimeout(idleStartTimerRef.current);
              idleStartTimerRef.current = null;
            }
            if (isIdle) {
              setIsIdle(false);
              // idleMoveTimerRef is cleared by the isIdle effect cleanup
            }
            // --- End Interrupt Idle State ---

            if (imgRef.current && containerRef.current) {
              const rect = containerRef.current.getBoundingClientRect();
              const imageRect = imgRef.current.getBoundingClientRect();

              // Calculate the scale factor between the original coordinates and our container
              const scaleX = imageRect.width / 1920;
              const scaleY =
                imageRect.height > 2000 ? 0 : imageRect.height / 1080;

              if (x === 0 && y === 0) {
                x = 1800;
                y = 100;
              }

              // Scale the coordinates to match our container size
              const scaledX = x * scaleX;
              const scaledY = y * scaleY;

              setTargetPosition({ x: scaledX, y: scaledY });

              if (!initialPositionSetRef.current) {
                setCursorPosition({ x: scaledX, y: scaledY });
                initialPositionSetRef.current = true;
              }
            }
          }

          if (imgRef.current && data.frame) {
            const img = "data:image/jpeg;base64," + data.frame;
            localStorage.setItem("browserImageData", img);
            imgRef.current.src = img;
          }
        } catch (e) {
          // Try to use raw data as fallback if JSON parsing fails
          if (typeof event.data === "string" && imgRef.current) {
            try {
              imgRef.current.src = event.data;
            } catch (imgError) {
              console.error("Failed to set image source directly:", imgError);
            }
          }
        }
      });

      ws.addEventListener("close", (event) => {
        console.log(`Disconnected (Code: ${event.code})`);
        wsRef.current = null;

        // Attempt to reconnect after a delay for any unexpected closure
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (sessionId) {
              connect();
            }
          }, 3000); // Wait 3 seconds before reconnecting
        }
      });

      ws.addEventListener("error", (error) => {
        console.error("Connection error - Will attempt to reconnect");
      });
    } catch (error) {
      console.error("Failed to create connection");
      setIsConnecting(false);
    }
  };

  useEffect(() => {
    // Only connect if we have a sessionId
    if (sessionId) {
      connect();

      return () => {
        cleanupConnection();
      };
    } else {
      // Clean up any existing connection
      cleanupConnection();
      console.log("Waiting for session ID...");

      return () => {
        cleanupConnection();
      };
    }
  }, [sessionId]); // Re-run effect when sessionId changes

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full flex items-center justify-center"
    >
      {/* Cursor */}
      {cursorPosition && cursorPosition.x !== 0 && cursorPosition.y !== 0 && (
        <div
          className="absolute pointer-events-none transform-gpu"
          style={{
            left: `${cursorPosition.x}px`,
            top: `${cursorPosition.y}px`,
            width: "50px",
            height: "50px",
            backgroundImage: `url("/images/agent-cursor.svg")`,
            backgroundSize: "contain",
            backgroundRepeat: "no-repeat",
            transform: "translate(-20%, -20%)",
            zIndex: 10,
            transition: isIdle ? "all 0.5s ease-out" : "all 0.1s linear",
          }}
        />
      )}

      {/* Children fallback */}
      {children && !imgRef.current?.src ? (
        <div className="h-full w-full flex items-center justify-center">
          {children}
        </div>
      ) : null}

      {/* Preview image */}
      <img
        ref={imgRef}
        id="live-frame"
        onLoad={() => {
          setImageLoaded(true);
          if (onScrapeComplete) onScrapeComplete();
        }}
        className={`w-auto h-auto max-w-full max-h-full object-contain transform-gpu ${
          !imageLoaded ? "opacity-0 scale-95" : "opacity-100 scale-100"
        } transition-all duration-300 ease-out`}
        style={{
          backgroundColor: "#f0f0f0",
        }}
      />
    </div>
  );
}
