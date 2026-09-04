"""Client for the Crossref Members endpoint."""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)

from ..models import ApiResponse, Member
from ..resources._standard import StavrophoraResourceClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class MembersClient(
    StavrophoraResourceClient, GettableMixin, SearchableMixin, CursorIterableMixin
):
    """Client for the Crossref Members API endpoint."""

    _entity_path: str = "members"
    _entity_model = Member
    _search_response_model: type = ApiResponse[Member]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("MembersClient initialized.")
