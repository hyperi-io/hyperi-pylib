"""
Custom exceptions for the template package.
"""

class TemplateError(Exception):
    """Base exception for template-related errors."""


class ConfigurationError(TemplateError):
    """Raised when configuration values are invalid or missing."""
