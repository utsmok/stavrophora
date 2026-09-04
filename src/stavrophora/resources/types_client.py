"""Client for the Crossref Types endpoint."""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)

from ..models import ApiResponse, CrossRefType
from ..resources._standard import StavrophoraResourceClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class TypesClient(
    StavrophoraResourceClient, GettableMixin, SearchableMixin, CursorIterableMixin
):
    """Client for the Crossref Types API endpoint."""

    _entity_path: str = "types"
    _entity_model = CrossRefType
    _search_response_model: type = ApiResponse[CrossRefType]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("TypesClient initialized.")
