"""Application-specific exceptions for CaféCraft AI."""


class CafecraftError(Exception):
    """Base class for all CaféCraft AI application errors."""


class ConfigurationError(CafecraftError):
    """Raised when application configuration is missing or invalid."""


class ValidationError(CafecraftError):
    """Raised when input data fails application validation."""


class AIServiceError(CafecraftError):
    """Raised when an AI service operation fails."""


class DocumentGenerationError(CafecraftError):
    """Raised when document generation fails."""


class StorageError(CafecraftError):
    """Raised when a storage or database operation fails."""
