"""Stavrophora: Python interface for the Crossref API."""

try:
    from importlib.metadata import PackageNotFoundError, version as _get_version

    __version__ = _get_version("stavrophora")
except PackageNotFoundError:
    __version__ = "0.0.0"

from bibliofabric.exceptions import (
    APIError,
    AuthError,
    BibliofabricError,
    ConfigurationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)

from .client import StavrophoraClient
from .models import (
    Agency,
    ApiResponse,
    Contributor,
    CrossRefDate,
    CrossRefType,
    Funder,
    FunderRef,
    IssnType,
    Journal,
    License,
    LicenseRef,
    Member,
    Message,
    Prefix,
    Work,
    WorkAgency,
)
from .session import StavrophoraSession

__all__ = [
    "__version__",
    "Agency",
    "APIError",
    "ApiResponse",
    "AuthError",
    "BibliofabricError",
    "ConfigurationError",
    "Contributor",
    "CrossRefDate",
    "CrossRefType",
    "Funder",
    "FunderRef",
    "IssnType",
    "Journal",
    "License",
    "LicenseRef",
    "Member",
    "Message",
    "NetworkError",
    "NotFoundError",
    "Prefix",
    "RateLimitError",
    "StavrophoraClient",
    "StavrophoraSession",
    "TimeoutError",
    "ValidationError",
    "Work",
    "WorkAgency",
]
