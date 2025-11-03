"use client";

import { CSSProperties, useEffect, useRef, useState } from "react";

import { cn } from "@/utils/cn";

interface VideoProps {
  src?: string;
  className?: string;
  videoClassName?: string;
  autoPlay?: boolean;
  muted?: boolean;
  loop?: boolean;
  controls?: boolean;
  poster?: string;
  style?: CSSProperties;
  sources?: Array<{
    src: string;
    type: string;
  }>;
}

export default function Video({
  src,
  className = "",
  videoClassName = "",
  style = {},
  autoPlay = true,
  muted = true,
  loop = true,
  controls = false,
  poster,
  sources = [],
}: VideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1 },
    );

    observer.observe(containerRef.current);

    return () => {
      if (container) {
        observer.unobserve(container);
      }
    };
  }, []);

  // Control playback based on visibility
  useEffect(() => {
    if (!videoRef.current) return;

    if (isVisible) {
      videoRef.current.play().catch(() => null);
    } else {
      videoRef.current.pause();
    }
  }, [isVisible]);

  return (
    <div className={className} ref={containerRef} style={style}>
      <video
        autoPlay={autoPlay && isVisible}
        className={cn("w-full h-full", videoClassName)}
        controls={controls}
        loop={loop}
        muted={muted}
        poster={poster}
        preload="auto"
        ref={videoRef}
        playsInline
      >
        {sources.length > 0 ? (
          sources.map((source, index) => (
            <source key={index} src={source.src} type={source.type} />
          ))
        ) : (
          <source src={src} type="video/mp4" />
        )}
        Your browser does not support the video tag.
      </video>
    </div>
  );
}
