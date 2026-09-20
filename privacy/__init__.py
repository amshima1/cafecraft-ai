"""Privacy foundations for consent, user data control, and retention."""

from .consent import ConsentManager, ConsentRecord
from .data_deletion import DataDeletionManager, DeletionResult
from .data_export import DataExporter
from .retention import RetentionPolicy
from .service import PrivacyService

__all__ = [
    "ConsentManager",
    "ConsentRecord",
    "DataDeletionManager",
    "DataExporter",
    "DeletionResult",
    "PrivacyService",
    "RetentionPolicy",
]
