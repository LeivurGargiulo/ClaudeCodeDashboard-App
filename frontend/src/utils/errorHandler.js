/**
 * Centralized error handling utilities for the frontend
 */

import toast from 'react-hot-toast'

export class AppError extends Error {
  constructor(message, code = 'UNKNOWN_ERROR', context = {}) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.context = context
    this.timestamp = new Date().toISOString()
  }
}

export const ErrorCodes = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  API_ERROR: 'API_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  SERVER_ERROR: 'SERVER_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
}

export const errorHandler = {
  /**
   * Handle and display API errors
   */
  handleApiError: (error, context = {}) => {
    console.error('API Error:', error, context)
    
    let errorMessage = 'An unexpected error occurred'
    let errorCode = ErrorCodes.UNKNOWN_ERROR
    
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          errorMessage = data?.detail || 'Bad request'
          errorCode = ErrorCodes.VALIDATION_ERROR
          break
        case 401:
          errorMessage = 'Authentication required'
          errorCode = ErrorCodes.AUTH_ERROR
          break
        case 403:
          errorMessage = 'Access forbidden'
          errorCode = ErrorCodes.AUTH_ERROR
          break
        case 404:
          errorMessage = data?.detail || 'Resource not found'
          errorCode = ErrorCodes.NOT_FOUND
          break
        case 429:
          errorMessage = 'Too many requests. Please try again later.'
          errorCode = ErrorCodes.API_ERROR
          break
        case 500:
          errorMessage = 'Server error. Please try again later.'
          errorCode = ErrorCodes.SERVER_ERROR
          break
        default:
          errorMessage = data?.detail || `HTTP ${status} error`
          errorCode = ErrorCodes.API_ERROR
      }
    } else if (error.request) {
      // Network error
      errorMessage = 'Unable to connect to server. Please check your connection.'
      errorCode = ErrorCodes.NETWORK_ERROR
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      errorMessage = 'Request timeout. Please try again.'
      errorCode = ErrorCodes.TIMEOUT_ERROR
    }
    
    const appError = new AppError(errorMessage, errorCode, {
      originalError: error,
      context
    })
    
    // Log error for debugging
    errorHandler.logError(appError)
    
    return appError
  },

  /**
   * Handle and display errors with toast notifications
   */
  handleErrorWithToast: (error, context = {}) => {
    const appError = errorHandler.handleApiError(error, context)
    
    // Show appropriate toast based on error type
    switch (appError.code) {
      case ErrorCodes.NETWORK_ERROR:
        toast.error(appError.message, {
          icon: '🌐',
          duration: 5000
        })
        break
      case ErrorCodes.AUTH_ERROR:
        toast.error(appError.message, {
          icon: '🔒',
          duration: 4000
        })
        break
      case ErrorCodes.NOT_FOUND:
        toast.error(appError.message, {
          icon: '❓',
          duration: 4000
        })
        break
      case ErrorCodes.SERVER_ERROR:
        toast.error(appError.message, {
          icon: '⚠️',
          duration: 6000
        })
        break
      default:
        toast.error(appError.message, {
          duration: 4000
        })
    }
    
    return appError
  },

  /**
   * Log errors for debugging and monitoring
   */
  logError: (error, context = {}) => {
    const errorLog = {
      timestamp: new Date().toISOString(),
      message: error.message,
      code: error.code || 'UNKNOWN',
      stack: error.stack,
      context: {
        ...context,
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: localStorage.getItem('user_id') || 'anonymous'
      }
    }
    
    // Log to console in development
    if (import.meta.env.DEV) {
      console.group('🚨 Error Log')
      console.error('Error:', error)
      console.table(errorLog.context)
      console.groupEnd()
    }
    
    // In production, you might want to send to monitoring service
    if (import.meta.env.PROD) {
      // Example: Send to monitoring service
      // sendToMonitoringService(errorLog)
    }
  },

  /**
   * Handle promise rejections globally
   */
  setupGlobalErrorHandling: () => {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason)
      
      const error = new AppError(
        'An unexpected error occurred',
        ErrorCodes.UNKNOWN_ERROR,
        { reason: event.reason }
      )
      
      errorHandler.logError(error)
      
      // Prevent default browser error handling
      event.preventDefault()
    })

    // Handle general JavaScript errors
    window.addEventListener('error', (event) => {
      const error = new AppError(
        event.message || 'JavaScript error occurred',
        ErrorCodes.UNKNOWN_ERROR,
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          error: event.error
        }
      )
      
      errorHandler.logError(error)
    })
  },

  /**
   * Retry function with exponential backoff
   */
  withRetry: async (fn, maxRetries = 3, baseDelay = 1000) => {
    let lastError
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await fn()
      } catch (error) {
        lastError = error
        
        // Don't retry certain error types
        if (error.response?.status === 400 || 
            error.response?.status === 401 || 
            error.response?.status === 403 ||
            error.response?.status === 404) {
          throw error
        }
        
        // Wait before retry (exponential backoff)
        if (attempt < maxRetries - 1) {
          const delay = baseDelay * Math.pow(2, attempt)
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }
    
    throw lastError
  },

  /**
   * Validate required fields
   */
  validateRequired: (data, requiredFields) => {
    const missingFields = []
    
    for (const field of requiredFields) {
      if (!data[field] || (typeof data[field] === 'string' && !data[field].trim())) {
        missingFields.push(field)
      }
    }
    
    if (missingFields.length > 0) {
      throw new AppError(
        `Missing required fields: ${missingFields.join(', ')}`,
        ErrorCodes.VALIDATION_ERROR,
        { missingFields, data }
      )
    }
  },

  /**
   * Create a safe async wrapper that handles errors
   */
  safeAsync: (fn) => {
    return async (...args) => {
      try {
        return await fn(...args)
      } catch (error) {
        return errorHandler.handleErrorWithToast(error)
      }
    }
  }
}

// Initialize global error handling
errorHandler.setupGlobalErrorHandling()

export default errorHandler