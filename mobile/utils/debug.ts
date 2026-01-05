/**
 * Debugging utilities for development
 */

// Enable React Native's error overlay
if (__DEV__) {
    // Log all errors with full stack traces
    // Note: Error.prepareStack may not be available in all environments

    // Log component renders in development
    if (typeof window !== 'undefined' && (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        console.log('React DevTools available');
    }
}

/**
 * Log error with full context
 */
export function logError(error: Error, context?: string) {
    console.error('=== ERROR ===');
    if (context) {
        console.error('Context:', context);
    }
    console.error('Message:', error.message);
    console.error('Stack:', error.stack);
    console.error('Error object:', error);
    console.error('=============');
}

/**
 * Log warning with context
 */
export function logWarning(message: string, context?: any) {
    console.warn('=== WARNING ===');
    console.warn('Message:', message);
    if (context) {
        console.warn('Context:', context);
    }
    console.warn('===============');
}

