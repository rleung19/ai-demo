/**
 * Error Handling Utilities
 * Task 4.9: Error handling and logging
 */

import { NextResponse } from 'next/server';

export interface ApiError {
  error: string;
  message: string;
  fallback?: boolean;
  details?: any;
}

/**
 * Create standardized error response
 */
export function createErrorResponse(
  error: string,
  message: string,
  status: number = 500,
  fallback: boolean = false,
  details?: any
): NextResponse<ApiError> {
  const response: ApiError = {
    error,
    message,
    fallback,
  };

  if (details) {
    response.details = details;
  }

  // Log error (in production, use proper logging service)
  console.error(`[API Error] ${error}: ${message}`, details || '');

  return NextResponse.json(response, { status });
}

/**
 * Handle database errors
 */
export function handleDatabaseError(error: any): NextResponse<ApiError> {
  const errorMessage = error.message || 'Unknown database error';

  // Check for common database errors
  if (errorMessage.includes('ORA-01017') || errorMessage.includes('invalid credential')) {
    return createErrorResponse(
      'Authentication failed',
      'Database authentication failed. Please check credentials.',
      503,
      true
    );
  }

  if (errorMessage.includes('ORA-12514') || errorMessage.includes('TNS')) {
    return createErrorResponse(
      'Connection failed',
      'Unable to connect to database. Please check connection string.',
      503,
      true
    );
  }

  if (errorMessage.includes('ORA-00942') || errorMessage.includes('table or view does not exist')) {
    return createErrorResponse(
      'Resource not found',
      'Required database table or view does not exist.',
      503,
      true
    );
  }

  // Generic database error
  return createErrorResponse(
    'Database error',
    errorMessage,
    503,
    true
  );
}

/**
 * Handle validation errors
 */
export function handleValidationError(errors: string[]): NextResponse<ApiError> {
  return createErrorResponse(
    'Validation failed',
    'Invalid request parameters',
    400,
    false,
    { errors }
  );
}

/**
 * Handle not found errors
 */
export function handleNotFoundError(resource: string): NextResponse<ApiError> {
  return createErrorResponse(
    'Not found',
    `${resource} not found`,
    404,
    false
  );
}
