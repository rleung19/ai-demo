/**
 * Express churn API base URL for the Next.js UI.
 * Must stay aligned with app/lib/api/churn-api.ts.
 */

/** Express standalone server URL when NEXT_PUBLIC_API_URL is unset (local dev). */
export const DEFAULT_EXPRESS_API_URL = 'http://localhost:3001';

/** Resolved Express churn API base URL (no trailing slash). */
export function getChurnApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_EXPRESS_API_URL;
}
