/**
 * Error Handling Utilities for Express
 * Express-compatible version of error handlers
 */

import { Response } from 'express';

export interface ApiError {
  error: string;
  message: string;
  fallback?: boolean;
  details?: any;
}

/**
 * Handle database errors
 */
export function handleDatabaseError(error: any, res: Response): Response {
  const errorMessage = error.message || 'Unknown database error';

  // Check for common database errors
  if (errorMessage.includes('ORA-01017') || errorMessage.includes('invalid credential')) {
    return res.status(503).json({
      error: 'Authentication failed',
      message: 'Database authentication failed. Please check credentials.',
      fallback: true,
    });
  }

  if (errorMessage.includes('ORA-12514') || errorMessage.includes('TNS')) {
    return res.status(503).json({
      error: 'Connection failed',
      message: 'Unable to connect to database. Please check connection string.',
      fallback: true,
    });
  }

  if (errorMessage.includes('ORA-00942') || errorMessage.includes('table or view does not exist')) {
    return res.status(503).json({
      error: 'Resource not found',
      message: 'Required database table or view does not exist.',
      fallback: true,
    });
  }

  // Generic database error
  return res.status(503).json({
    error: 'Database error',
    message: errorMessage,
    fallback: true,
  });
}

/**
 * Handle validation errors
 */
export function handleValidationError(errors: string[], res: Response): Response {
  return res.status(400).json({
    error: 'Validation failed',
    message: 'Invalid request parameters',
    details: { errors },
  });
}

/**
 * Handle not found errors
 */
export function handleNotFoundError(resource: string, res: Response): Response {
  return res.status(404).json({
    error: 'Not found',
    message: `${resource} not found`,
    fallback: false,
  });
}
