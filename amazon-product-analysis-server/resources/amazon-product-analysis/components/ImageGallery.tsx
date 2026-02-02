import React, { useState, useMemo } from "react";
import { getProxiedImageUrl } from "../utils";

interface ImageGalleryProps {
    images: string[];
    title: string;
    mcpUrl?: string;
}

const ChevronLeftIcon: React.FC = () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="15 18 9 12 15 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const ChevronRightIcon: React.FC = () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="9 18 15 12 9 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const ImageIcon: React.FC = () => (
    <svg className="w-6 h-6 text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
    </svg>
);

export const ImageGallery: React.FC<ImageGalleryProps> = ({ images, title, mcpUrl }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [isZoomed, setIsZoomed] = useState(false);

    // Proxy all images to avoid CORS issues
    const proxiedImages = useMemo(() => {
        return images?.map((img) => getProxiedImageUrl(img, mcpUrl) || img) || [];
    }, [images, mcpUrl]);

    if (!proxiedImages || proxiedImages.length === 0) return null;

    const handlePrevious = () => {
        setSelectedIndex((prev) => (prev === 0 ? proxiedImages.length - 1 : prev - 1));
    };

    const handleNext = () => {
        setSelectedIndex((prev) => (prev === proxiedImages.length - 1 ? 0 : prev + 1));
    };

    const handleThumbnailClick = (index: number) => {
        setSelectedIndex(index);
    };

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl">
            <h4 className="text-lg font-semibold text-default mb-4 flex items-center gap-2">
                <ImageIcon />
                Product Gallery
                <span className="text-xs font-normal text-secondary ml-auto">
                    {selectedIndex + 1} / {proxiedImages.length}
                </span>
            </h4>

            {/* Main Image */}
            <div className="relative group mb-4">
                <div
                    className={`relative bg-white rounded-xl overflow-hidden transition-all duration-300 ${isZoomed ? "cursor-zoom-out" : "cursor-zoom-in"
                        }`}
                    onClick={() => setIsZoomed(!isZoomed)}
                >
                    <img
                        src={proxiedImages[selectedIndex]}
                        alt={`${title} - Image ${selectedIndex + 1}`}
                        className={`w-full object-contain transition-transform duration-300 ${isZoomed ? "h-96 scale-150" : "h-64"
                            }`}
                        onError={(e) => {
                            (e.target as HTMLImageElement).style.display = "none";
                        }}
                    />
                </div>

                {/* Navigation Arrows */}
                {proxiedImages.length > 1 && (
                    <>
                        <button
                            onClick={(e) => { e.stopPropagation(); handlePrevious(); }}
                            className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                            aria-label="Previous image"
                        >
                            <ChevronLeftIcon />
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); handleNext(); }}
                            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                            aria-label="Next image"
                        >
                            <ChevronRightIcon />
                        </button>
                    </>
                )}

                {/* Zoom hint */}
                <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/50 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    Click to {isZoomed ? "zoom out" : "zoom in"}
                </div>
            </div>

            {/* Thumbnails */}
            {proxiedImages.length > 1 && (
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
                    {proxiedImages.map((image, index) => (
                        <button
                            key={index}
                            onClick={() => handleThumbnailClick(index)}
                            className={`shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all ${index === selectedIndex
                                    ? "border-violet-500 ring-2 ring-violet-500/30"
                                    : "border-transparent hover:border-default"
                                }`}
                        >
                            <img
                                src={image}
                                alt={`Thumbnail ${index + 1}`}
                                className="w-full h-full object-contain bg-white p-1"
                                onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = "none";
                                }}
                            />
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};