/**
 * Convex Authentication Configuration
 *
 * Configures Clerk as the authentication provider for Convex
 * The CLERK_JWT_ISSUER_DOMAIN is set via: npx convex env set
 */

export default {
  providers: [
    {
      // This reads from Convex environment variable (not process.env)
      // Set via: npx convex env set CLERK_JWT_ISSUER_DOMAIN "https://..."
      domain: "https://ultimate-grub-14.clerk.accounts.dev",
      applicationID: "convex",
    },
  ],
};
