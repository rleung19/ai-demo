/**
 * Request Validation Utilities
 * Task 4.8: Request validation and input sanitization
 */

/**
 * Validate and sanitize query parameters
 */
export function validateQueryParams(
  params: URLSearchParams,
  schema: Record<string, { type: 'string' | 'number' | 'boolean'; required?: boolean; allowed?: any[] }>
): { valid: boolean; data?: Record<string, any>; errors?: string[] } {
  const errors: string[] = [];
  const data: Record<string, any> = {};

  for (const [key, config] of Object.entries(schema)) {
    const value = params.get(key);

    if (config.required && !value) {
      errors.push(`Missing required parameter: ${key}`);
      continue;
    }

    if (!value && !config.required) {
      continue;
    }

    // Type conversion and validation
    let convertedValue: any = value;
    if (config.type === 'number') {
      convertedValue = Number(value);
      if (isNaN(convertedValue)) {
        errors.push(`Invalid number for parameter ${key}: ${value}`);
        continue;
      }
    } else if (config.type === 'boolean') {
      convertedValue = value === 'true' || value === '1';
    }

    // Check allowed values
    if (config.allowed && !config.allowed.includes(convertedValue)) {
      errors.push(`Invalid value for parameter ${key}: ${value}. Allowed: ${config.allowed.join(', ')}`);
      continue;
    }

    // Basic sanitization (remove potential SQL injection patterns)
    if (typeof convertedValue === 'string') {
      // Remove common SQL injection patterns
      const dangerous = [';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute'];
      const lowerValue = convertedValue.toLowerCase();
      if (dangerous.some(pattern => lowerValue.includes(pattern))) {
        errors.push(`Potentially unsafe value for parameter ${key}`);
        continue;
      }
    }

    data[key] = convertedValue;
  }

  return errors.length > 0 ? { valid: false, errors } : { valid: true, data };
}

/**
 * Sanitize string input (basic XSS prevention)
 */
export function sanitizeString(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove < and >
    .trim()
    .slice(0, 1000); // Limit length
}

/**
 * Validate date range
 */
export function validateDateRange(startDate?: string, endDate?: string): { valid: boolean; error?: string } {
  if (!startDate && !endDate) {
    return { valid: true };
  }

  const start = startDate ? new Date(startDate) : null;
  const end = endDate ? new Date(endDate) : null;

  if (start && isNaN(start.getTime())) {
    return { valid: false, error: 'Invalid start date format' };
  }

  if (end && isNaN(end.getTime())) {
    return { valid: false, error: 'Invalid end date format' };
  }

  if (start && end && start > end) {
    return { valid: false, error: 'Start date must be before end date' };
  }

  return { valid: true };
}
