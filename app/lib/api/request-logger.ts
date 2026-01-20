/**
 * Request Logger Utility
 * 
 * Logs API requests for monitoring in production
 * Includes endpoint, method, timestamp, and response status
 */

interface RequestLog {
  timestamp: string;
  method: string;
  path: string;
  status: number;
  duration: number;
}

/**
 * Log API request (production only - dev mode is too noisy)
 */
export function logRequest(
  method: string,
  path: string,
  status: number,
  startTime: number
): void {
  // Only log in production to avoid cluttering dev mode output
  if (process.env.NODE_ENV === 'production') {
    const duration = Date.now() - startTime;
    const timestamp = new Date().toISOString();
    console.log(
      `[API] ${timestamp} ${method} ${path} ${status} ${duration}ms`
    );
  }
}

/**
 * Create a request logger wrapper for Next.js API routes
 */
export function withRequestLogging<T>(
  handler: () => Promise<T>,
  method: string,
  path: string
): Promise<T> {
  const startTime = Date.now();
  return handler()
    .then((result) => {
      // Try to extract status from NextResponse if possible
      const status = (result as any)?.status || 200;
      logRequest(method, path, status, startTime);
      return result;
    })
    .catch((error) => {
      logRequest(method, path, 500, startTime);
      throw error;
    });
}
