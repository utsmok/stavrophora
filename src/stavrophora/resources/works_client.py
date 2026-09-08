"""Client for the Crossref Works endpoint."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)
from bibliofabric.types import ValidationErrorContext

from .._helpers import encode_doi_path
from ..models import ApiResponse, Work, WorkAgency
from ..resources._standard import StavrophoraResourceClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class WorksClient(
    StavrophoraResourceClient, GettableMixin, SearchableMixin, CursorIterableMixin
):
    """Client for the Crossref Works API endpoint.

    Supports GET by DOI, search, cursor iteration, filtering, sorting,
    field selection, batch DOI lookup, and registration-agency lookup.
    """

    _entity_path: str = "works"
    _entity_model: type[Work] = Work
    _search_response_model: type = ApiResponse[Work]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "doi": "doi",
    }

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("WorksClient initialized.")

    async def get(
        self,
        entity_id: str,
        *,
        raw: bool = False,
        on_validation_error: Callable[[ValidationErrorContext], None] | None = None,
    ) -> Any:
        """Retrieve a single work by DOI.

        Accepts bare or ``https://doi.org/``-prefixed DOIs (mixed case
        tolerated); the DOI is normalized and percent-encoded for the path.

        Args:
            entity_id: The DOI of the work.
            raw: Return the unparsed HTTP response.
            on_validation_error: Optional hook called when model parsing fails.

        Returns:
            The parsed :class:`~stavrophora.models.Work`.
        """
        return await super().get(
            encode_doi_path(entity_id),
            raw=raw,
            on_validation_error=on_validation_error,
        )  # ty: ignore[invalid-argument-type]

    async def agency(self, doi: str) -> WorkAgency:
        """Look up the DOI registration agency for a work.

        Args:
            doi: The DOI to look up.

        Returns:
            The parsed :class:`~stavrophora.models.WorkAgency`.
        """
        path = f"works/{encode_doi_path(doi)}/agency"
        response = await self._api_client.request(
            "GET", path, params=None, base_url_override=self._base_url_override
        )
        data = self.response_unwrapper.unwrap_single_item(response.json())
        return WorkAgency.model_validate(data)


class ScopedWorksClient(WorksClient):
    """Works client scoped to a parent resource path.

    Powers the ``/journals/{issn}/works``, ``/funders/{id}/works`` and
    ``/prefixes/{prefix}/works`` sub-resources; full works capabilities
    (search, iterate, batch, select, sort) against the scoped path.

    Obtain instances via :meth:`JournalsClient.works`,
    :meth:`FundersClient.works` or :meth:`PrefixesClient.works`.
    """

    def __init__(self, api_client: "StavrophoraClient", entity_path: str):
        super().__init__(api_client)
        self._entity_path = entity_path
        logger.debug(f"ScopedWorksClient initialized for path: {entity_path}")
