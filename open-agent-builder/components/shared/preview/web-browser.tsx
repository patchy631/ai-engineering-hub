import { useEffect, useState } from "react";
import LivePreviewFrame from "./live-preview-frame";

export default function WebBrowser({
  url,
  sessionId,
  isScrapeComplete,
  children,
}: {
  url?: string;
  sessionId: string;
  isScrapeComplete: boolean;
  children?: React.ReactNode;
}) {
  const [isLoading, setIsLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Add a slight delay before showing the browser to ensure smooth entrance
    const timer = setTimeout(() => {
      setIsVisible(true);
      setIsLoading(false);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="relative w-full h-full flex items-center justify-center bg-transparent">
      <div
        className={`w-full h-full max-w-[95vw] max-h-[85vh] min-w-full sm:min-w-[700px] rounded-2xl shadow-lg border border-gray-100 bg-white overflow-hidden flex flex-col transform-gpu ${
          isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        } transition-all duration-300 ease-out`}
      >
        {/* macOS-style top bar with loading indicator */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-100 bg-zinc-50 flex-shrink-0">
          <div className="flex gap-2">
            <div
              className={`w-3 h-3 rounded-full transition-colors duration-200 ${
                isLoading ? "bg-yellow-500" : "bg-red-500"
              }`}
            />
            <div
              className={`w-3 h-3 rounded-full transition-colors duration-200 ${
                isLoading ? "bg-yellow-500" : "bg-yellow-500"
              }`}
            />
            <div
              className={`w-3 h-3 rounded-full transition-colors duration-200 ${
                isLoading ? "bg-yellow-500" : "bg-green-500"
              }`}
            />
          </div>

          <div className="flex items-center gap-2">
            {/* Spinner */}
            <div className="browser-spinner animate-spin w-4 h-4 border-2 border-zinc-300 border-t-zinc-600 rounded-full" />
          </div>
        </div>

        {/* Content area with fade transition */}
        <div
          className={`flex-1 overflow-hidden transition-opacity duration-300 ${
            isLoading ? "opacity-50" : "opacity-100"
          }`}
        >
          <LivePreviewFrame
            sessionId={sessionId}
            onScrapeComplete={
              isScrapeComplete
                ? () => {
                    console.log("Scrape complete");
                    setIsLoading(false);
                  }
                : undefined
            }
          >
            {children}
          </LivePreviewFrame>
        </div>
      </div>
    </main>
  );
}
