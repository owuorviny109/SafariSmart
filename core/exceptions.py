"""
Module: core/exceptions.py
Purpose: Custom exception hierarchy for SafariSmart Kenya

This module defines domain-specific exceptions for better error handling
and debugging throughout the application.

Classes:
    SafariSmartException: Base exception for all application errors
    WizardValidationError: Wizard input validation errors
    ItineraryGenerationError: Itinerary generation failures
    InsufficientBudgetError: Budget-related errors
    AIServiceError: AI service integration errors
    InvalidResponseError: Invalid AI response format errors
    
Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

from typing import Optional
from decimal import Decimal


class SafariSmartException(Exception):
    """
    Base exception for all SafariSmart application errors.
    
    All custom exceptions in the application should inherit from this class.
    This allows for catching all application-specific errors with a single
    except clause when needed.
    
    Attributes:
        message (str): Human-readable error message
        code (str): Machine-readable error code
        
    Example:
        >>> try:
        ...     raise SafariSmartException("Something went wrong")
        ... except SafariSmartException as e:
        ...     print(f"Application error: {e}")
    """
    
    def __init__(self, message: str, code: Optional[str] = None):
        """
        Initialize exception with message and optional code.
        
        Args:
            message (str): Human-readable error message
            code (str, optional): Machine-readable error code
        """
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)
        
    def __str__(self) -> str:
        """Return string representation of exception."""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class WizardValidationError(SafariSmartException):
    """
    Raised when wizard input validation fails.
    
    This exception is raised when user input in the wizard flow
    does not meet validation requirements.
    
    Attributes:
        field (str): Name of the field that failed validation
        value: The invalid value that was provided
        
    Example:
        >>> raise WizardValidationError(
        ...     "Duration must be between 1 and 30 days",
        ...     field="duration",
        ...     value=45
        ... )
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[any] = None
    ):
        """
        Initialize validation error with field context.
        
        Args:
            message (str): Error message
            field (str, optional): Field name that failed validation
            value (optional): The invalid value
        """
        self.field = field
        self.value = value
        super().__init__(message, code="WIZARD_VALIDATION_ERROR")
        
    def __str__(self) -> str:
        """Return detailed string representation."""
        if self.field:
            return f"Validation error in '{self.field}': {self.message}"
        return self.message


class ItineraryGenerationError(SafariSmartException):
    """
    Raised when itinerary generation fails.
    
    This exception is raised when the itinerary generation process
    encounters an error, whether from AI service or template generation.
    
    Attributes:
        generator_type (str): Type of generator that failed (ai/template)
        original_error (Exception): Original exception that caused failure
        
    Example:
        >>> try:
        ...     generate_itinerary()
        ... except Exception as e:
        ...     raise ItineraryGenerationError(
        ...         "Failed to generate itinerary",
        ...         generator_type="ai",
        ...         original_error=e
        ...     )
    """
    
    def __init__(
        self,
        message: str,
        generator_type: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize generation error with context.
        
        Args:
            message (str): Error message
            generator_type (str, optional): Generator type (ai/template)
            original_error (Exception, optional): Original exception
        """
        self.generator_type = generator_type
        self.original_error = original_error
        super().__init__(message, code="ITINERARY_GENERATION_ERROR")
        
    def __str__(self) -> str:
        """Return detailed string representation."""
        msg = self.message
        if self.generator_type:
            msg = f"[{self.generator_type}] {msg}"
        if self.original_error:
            msg = f"{msg} (Caused by: {str(self.original_error)})"
        return msg


class InsufficientBudgetError(SafariSmartException):
    """
    Raised when budget is insufficient for selected options.
    
    This exception provides detailed information about budget
    requirements vs. what was provided.
    
    Attributes:
        required (Decimal): Minimum required budget
        provided (Decimal): Budget that was provided
        currency (str): Currency code (default: KSh)
        
    Example:
        >>> raise InsufficientBudgetError(
        ...     required=Decimal('100000'),
        ...     provided=Decimal('50000')
        ... )
    """
    
    def __init__(
        self,
        required: Decimal,
        provided: Decimal,
        currency: str = "KSh"
    ):
        """
        Initialize budget error with amounts.
        
        Args:
            required (Decimal): Minimum required budget
            provided (Decimal): Budget provided by user
            currency (str): Currency code (default: KSh)
        """
        self.required = required
        self.provided = provided
        self.currency = currency
        
        message = (
            f"Budget insufficient. "
            f"Required: {currency} {required:,}, "
            f"Provided: {currency} {provided:,}"
        )
        super().__init__(message, code="INSUFFICIENT_BUDGET")
        
    @property
    def shortfall(self) -> Decimal:
        """
        Calculate budget shortfall.
        
        Returns:
            Decimal: Amount by which budget is insufficient
        """
        return self.required - self.provided


class AIServiceError(SafariSmartException):
    """
    Raised when AI service integration fails.
    
    This exception is raised when communication with external AI
    services (like Gemini) fails or returns errors.
    
    Attributes:
        service_name (str): Name of the AI service
        status_code (int): HTTP status code if applicable
        
    Example:
        >>> raise AIServiceError(
        ...     "Gemini API rate limit exceeded",
        ...     service_name="gemini",
        ...     status_code=429
        ... )
    """
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        """
        Initialize AI service error.
        
        Args:
            message (str): Error message
            service_name (str, optional): Name of AI service
            status_code (int, optional): HTTP status code
        """
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(message, code="AI_SERVICE_ERROR")
        
    def __str__(self) -> str:
        """Return detailed string representation."""
        msg = self.message
        if self.service_name:
            msg = f"[{self.service_name}] {msg}"
        if self.status_code:
            msg = f"{msg} (Status: {self.status_code})"
        return msg


class InvalidResponseError(SafariSmartException):
    """
    Raised when AI response format is invalid.
    
    This exception is raised when the AI service returns a response
    that cannot be parsed or does not match expected format.
    
    Attributes:
        response_text (str): The invalid response text
        expected_format (str): Description of expected format
        
    Example:
        >>> raise InvalidResponseError(
        ...     "Response is not valid JSON",
        ...     response_text=raw_response,
        ...     expected_format="JSON with 'title' and 'days' fields"
        ... )
    """
    
    def __init__(
        self,
        message: str,
        response_text: Optional[str] = None,
        expected_format: Optional[str] = None
    ):
        """
        Initialize invalid response error.
        
        Args:
            message (str): Error message
            response_text (str, optional): The invalid response
            expected_format (str, optional): Expected format description
        """
        self.response_text = response_text
        self.expected_format = expected_format
        super().__init__(message, code="INVALID_RESPONSE")
        
    def __str__(self) -> str:
        """Return detailed string representation."""
        msg = self.message
        if self.expected_format:
            msg = f"{msg} (Expected: {self.expected_format})"
        return msg


class DestinationNotFoundError(SafariSmartException):
    """
    Raised when a requested destination does not exist.
    
    This exception is raised when attempting to access a destination
    that is not in the database.
    
    Attributes:
        destination_id (int): ID of the missing destination
        destination_slug (str): Slug of the missing destination
        
    Example:
        >>> raise DestinationNotFoundError(
        ...     "Destination not found",
        ...     destination_id=999
        ... )
    """
    
    def __init__(
        self,
        message: str,
        destination_id: Optional[int] = None,
        destination_slug: Optional[str] = None
    ):
        """
        Initialize destination not found error.
        
        Args:
            message (str): Error message
            destination_id (int, optional): Destination ID
            destination_slug (str, optional): Destination slug
        """
        self.destination_id = destination_id
        self.destination_slug = destination_slug
        super().__init__(message, code="DESTINATION_NOT_FOUND")
        
    def __str__(self) -> str:
        """Return detailed string representation."""
        msg = self.message
        if self.destination_id:
            msg = f"{msg} (ID: {self.destination_id})"
        elif self.destination_slug:
            msg = f"{msg} (Slug: {self.destination_slug})"
        return msg


class SessionExpiredError(SafariSmartException):
    """
    Raised when wizard session has expired.
    
    This exception is raised when attempting to access wizard data
    from an expired or invalid session.
    
    Example:
        >>> raise SessionExpiredError(
        ...     "Your session has expired. Please start over."
        ... )
    """
    
    def __init__(self, message: str = "Session has expired"):
        """
        Initialize session expired error.
        
        Args:
            message (str): Error message
        """
        super().__init__(message, code="SESSION_EXPIRED")
