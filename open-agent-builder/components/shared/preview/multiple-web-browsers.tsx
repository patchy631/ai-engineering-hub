"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import WebBrowser from "./web-browser";

let interval: NodeJS.Timeout;

type BrowserData = {
  id: number;
  sessionId: string;
  isScrapeComplete: boolean;
  children?: React.ReactNode;
};

export default function MultipleWebBrowsers({
  browsers,
  offset,
  scaleFactor,
  autoRotate = true,
  rotationInterval = 5000,
}: {
  browsers: BrowserData[];
  offset?: number;
  scaleFactor?: number;
  autoRotate?: boolean;
  rotationInterval?: number;
}) {
  const CARD_OFFSET = offset || 10;
  const SCALE_FACTOR = scaleFactor || 0.06;
  const [activeBrowsers, setActiveBrowsers] = useState<BrowserData[]>(browsers);

  useEffect(() => {
    if (autoRotate) {
      startRotation();
    }
    return () => clearInterval(interval);
  }, [autoRotate, rotationInterval]);

  const startRotation = () => {
    interval = setInterval(() => {
      setActiveBrowsers((prevBrowsers: BrowserData[]) => {
        const newArray = [...prevBrowsers];
        newArray.unshift(newArray.pop()!); // move the last element to the front
        return newArray;
      });
    }, rotationInterval);
  };

  return (
    <div className="relative h-[600px] w-full">
      {activeBrowsers.map((browser, index) => {
        return (
          <motion.div
            key={browser.id}
            className="absolute w-full rounded-xl overflow-hidden"
            style={{
              transformOrigin: "top center",
            }}
            animate={{
              top: index * -CARD_OFFSET,
              scale: 1 - index * SCALE_FACTOR,
              zIndex: activeBrowsers.length - index,
            }}
          >
            <WebBrowser
              sessionId={browser.sessionId}
              isScrapeComplete={browser.isScrapeComplete}
            >
              {browser.children}
            </WebBrowser>
          </motion.div>
        );
      })}
    </div>
  );
}
