'use client';

import { useEffect } from 'react';

/**
 * BigInt Serialization Provider
 *
 * Adds global JSON.stringify support for BigInt values.
 * Required for Next.js 16 beta + React 19 compatibility.
 */
export function BigIntProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Add BigInt serialization support globally
    if (typeof BigInt !== 'undefined') {
      // @ts-ignore - Adding toJSON to BigInt prototype
      BigInt.prototype.toJSON = function() {
        return this.toString();
      };
    }
  }, []);

  return <>{children}</>;
}
