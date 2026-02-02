/**
 * Converts an Amazon image URL to a proxied URL through our server
 * This is needed because Amazon CDN blocks cross-origin requests,
 * which causes images to fail loading in ChatGPT and other external clients.
 * 
 * @param imageUrl - The original Amazon image URL
 * @param mcpUrl - The base URL of the MCP server (e.g., https://myserver.com)
 * @returns The proxied image URL
 */
export function getProxiedImageUrl(imageUrl: string | undefined, mcpUrl: string | undefined): string | undefined {
    if (!imageUrl || !mcpUrl) {
        return imageUrl;
    }

    // Check if it's an Amazon image URL that needs proxying
    const amazonHosts = [
        "m.media-amazon.com",
        "images-na.ssl-images-amazon.com",
        "images-eu.ssl-images-amazon.com",
        "images-fe.ssl-images-amazon.com",
        "ecx.images-amazon.com",
        ".media-amazon.com",
    ];

    try {
        const url = new URL(imageUrl);
        const isAmazonImage = amazonHosts.some(
            (host) => url.hostname.includes(host) || url.hostname.endsWith(".media-amazon.com")
        );

        if (isAmazonImage) {
            // Construct the proxied URL
            const baseUrl = mcpUrl.endsWith("/") ? mcpUrl.slice(0, -1) : mcpUrl;
            return `${baseUrl}/api/image-proxy?url=${encodeURIComponent(imageUrl)}`;
        }
    } catch {
        // If URL parsing fails, return original
        return imageUrl;
    }

    return imageUrl;
}