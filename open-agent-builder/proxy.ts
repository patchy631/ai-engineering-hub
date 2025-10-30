import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
  '/api/config(.*)',
  '/api/templates(.*)',
  '/api/mcp(.*)',
  '/api/test-mcp-connection(.*)',
])

// Define API routes that require API key authentication (bypass Clerk auth)
const isApiKeyRoute = createRouteMatcher([
  '/api/workflows/:workflowId/execute',
  '/api/workflows/:workflowId/execute-stream',
  '/api/workflows/:workflowId/resume',
])

export default clerkMiddleware(async (auth, request) => {
  // API key routes bypass Clerk auth (will be validated in the route handler)
  if (isApiKeyRoute(request)) {
    return
  }

  // Protect all routes except public ones
  if (!isPublicRoute(request)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    // Skip Next.js internals and static files
    '/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
