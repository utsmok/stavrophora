"""Resource clients for Crossref API endpoints."""

from .funders_client import FundersClient
from .journals_client import JournalsClient
from .licenses_client import LicensesClient
from .members_client import MembersClient
from .prefixes_client import PrefixesClient
from .types_client import TypesClient
from .works_client import ScopedWorksClient, WorksClient

__all__ = [
    "FundersClient",
    "JournalsClient",
    "LicensesClient",
    "MembersClient",
    "PrefixesClient",
    "ScopedWorksClient",
    "TypesClient",
    "WorksClient",
]
