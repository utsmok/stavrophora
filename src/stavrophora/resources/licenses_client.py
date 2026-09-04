"""Client for the Crossref Licenses endpoint.

Crossref has no single-license route (verified live: ``/licenses/{id}``
returns 404); only the list endpoint exists.
"""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import CursorIterableMixin, SearchableMixin

from ..models import ApiResponse, License
from ..resources._standard import StavrophoraResourceClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class LicensesClient(StavrophoraResourceClient, SearchableMixin, CursorIterableMixin):
    """Client for the Crossref Licenses API endpoint (list/iterate only)."""

    _entity_path: str = "licenses"
    _entity_model = License
    _search_response_model: type = ApiResponse[License]

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("LicensesClient initialized.")
