"""Client for the Crossref Funders endpoint."""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)

from .._helpers import encode_doi_path
from ..models import ApiResponse, Funder
from ..resources._standard import StavrophoraResourceClient
from ..resources.works_client import ScopedWorksClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class FundersClient(
    StavrophoraResourceClient, GettableMixin, SearchableMixin, CursorIterableMixin
):
    """Client for the Crossref Funders API endpoint."""

    _entity_path: str = "funders"
    _entity_model = Funder
    _search_response_model: type = ApiResponse[Funder]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("FundersClient initialized.")

    async def get(self, entity_id: str) -> object:
        """Retrieve a single funder by its Funder Registry DOI.

        Args:
            entity_id: Funder Registry DOI (e.g. ``10.13039/501100000923``).

        Returns:
            The parsed :class:`~stavrophora.models.Funder`.
        """
        return await super().get(encode_doi_path(entity_id))  # ty: ignore[invalid-argument-type]

    def works(self, funder_id: str) -> ScopedWorksClient:
        """Get a works client scoped to a funder.

        Args:
            funder_id: Funder Registry DOI of the funder.

        Returns:
            A :class:`ScopedWorksClient` bound to ``funders/{id}/works``.
        """
        return ScopedWorksClient(
            self._api_client, f"funders/{encode_doi_path(funder_id)}/works"
        )
