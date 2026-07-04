import { useQuery } from "@tanstack/react-query";
import type { ProductAnalysisData } from "../types";

/**
 * React hook for fetching Amazon product analysis via API
 * This is CLIENT-SIDE code - safe for browser/widget use
 */
export function useProductAnalysis(
  url: string | undefined,
  zipcode: string | undefined,
  mcpUrl: string | undefined
) {
  return useQuery({
    queryKey: ["amazon-product-analysis", url, zipcode],
    queryFn: async (): Promise<ProductAnalysisData> => {
      const params = new URLSearchParams({ url: url! });
      if (zipcode) params.append("zipcode", zipcode);

      const response = await fetch(`${mcpUrl}/api/analyze-amazon-product?${params}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to analyze product");
      }
      return response.json();
    },
    enabled: !!mcpUrl && !!url,
  });
}