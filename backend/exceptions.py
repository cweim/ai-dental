"""
Custom exception classes for the AI Dentist application.

This module defines custom exceptions that provide better error handling
and more descriptive error messages throughout the application.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class AIDentistException(Exception):
    """Base exception class for AI Dentist application"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(AIDentistException):
    """Exception raised for database-related errors"""
    pass


class EmbeddingException(AIDentistException):
    """Exception raised for embedding service errors"""
    pass


class VectorSearchException(AIDentistException):
    """Exception raised for vector search errors"""
    pass


class ChatbotException(AIDentistException):
    """Exception raised for chatbot service errors"""
    pass


class EmailException(AIDentistException):
    """Exception raised for email service errors"""
    pass


class AppointmentException(AIDentistException):
    """Exception raised for appointment-related errors"""
    pass


class ValidationException(AIDentistException):
    """Exception raised for input validation errors"""
    pass


class ExternalServiceException(AIDentistException):
    """Exception raised for external service errors (GROQ, SendGrid)"""
    pass


class ConfigurationException(AIDentistException):
    """Exception raised for configuration errors"""
    pass


# HTTP Exception wrappers for FastAPI
class AIDentistHTTPException(HTTPException):
    """Custom HTTP exception for AI Dentist API"""
    
    def __init__(
        self, 
        status_code: int, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        detail = {
            "message": message,
            "details": details or {},
            "error_type": "ai_dentist_error"
        }
        super().__init__(status_code=status_code, detail=detail, headers=headers)


# Specific HTTP exceptions
class BadRequestException(AIDentistHTTPException):
    """400 Bad Request"""
    def __init__(self, message: str = "Bad request", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, message=message, details=details)


class UnauthorizedException(AIDentistHTTPException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=401, message=message, details=details)


class ForbiddenException(AIDentistHTTPException):
    """403 Forbidden"""
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=403, message=message, details=details)


class NotFoundException(AIDentistHTTPException):
    """404 Not Found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, message=message, details=details)


class ConflictException(AIDentistHTTPException):
    """409 Conflict"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, message=message, details=details)


class UnprocessableEntityException(AIDentistHTTPException):
    """422 Unprocessable Entity"""
    def __init__(self, message: str = "Unprocessable entity", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=422, message=message, details=details)


class InternalServerErrorException(AIDentistHTTPException):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)


class ServiceUnavailableException(AIDentistHTTPException):
    """503 Service Unavailable"""
    def __init__(self, message: str = "Service unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=503, message=message, details=details)


# Exception mapping utility
def map_exception_to_http(exception: Exception) -> AIDentistHTTPException:
    """Map internal exceptions to appropriate HTTP exceptions"""
    
    exception_mapping = {
        ValidationException: BadRequestException,
        AppointmentException: BadRequestException,
        DatabaseException: InternalServerErrorException,
        EmbeddingException: ServiceUnavailableException,
        VectorSearchException: ServiceUnavailableException,
        ChatbotException: ServiceUnavailableException,
        EmailException: ServiceUnavailableException,
        ExternalServiceException: ServiceUnavailableException,
        ConfigurationException: InternalServerErrorException,
    }
    
    exception_type = type(exception)
    http_exception_class = exception_mapping.get(exception_type, InternalServerErrorException)
    
    message = str(exception)
    details = getattr(exception, 'details', {}) if hasattr(exception, 'details') else {}
    
    # Log the exception
    logger.error(f"{exception_type.__name__}: {message}", extra={"details": details})
    
    return http_exception_class(message=message, details=details)


def handle_exception(exception: Exception) -> AIDentistHTTPException:
    """Handle any exception and convert to appropriate HTTP exception"""
    
    # If it's already an HTTP exception, return as is
    if isinstance(exception, HTTPException):
        return exception
    
    # If it's one of our custom exceptions, map it
    if isinstance(exception, AIDentistException):
        return map_exception_to_http(exception)
    
    # For any other exception, return generic internal server error
    logger.error(f"Unhandled exception: {type(exception).__name__}: {str(exception)}")
    return InternalServerErrorException(
        message="An unexpected error occurred",
        details={"original_error": str(exception)}
    )


# Context manager for exception handling
class ExceptionHandler:
    """Context manager for consistent exception handling"""
    
    def __init__(self, operation: str):
        self.operation = operation
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Exception in {self.operation}: {exc_type.__name__}: {exc_val}")
            return False  # Re-raise the exception
        return True