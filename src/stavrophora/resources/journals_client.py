"""Client for the Crossref Journals endpoint."""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)

from ..models import ApiResponse, Journal
from ..resources._standard import StavrophoraResourceClient
from ..resources.works_client import ScopedWorksClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class JournalsClient(
    StavrophoraResourceClient, GettableMixin, SearchableMixin, CursorIterableMixin
):
    """Client for the Crossref Journals API endpoint."""

    _entity_path: str = "journals"
    _entity_model = Journal
    _search_response_model: type = ApiResponse[Journal]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("JournalsClient initialized.")

    def works(self, issn: str) -> ScopedWorksClient:
        """Get a works client scoped to a journal.

        Args:
            issn: ISSN or eISSN of the journal (hyphen optional).

        Returns:
            A :class:`ScopedWorksClient` bound to ``journals/{issn}/works``.
        """
        return ScopedWorksClient(self._api_client, f"journals/{issn}/works")
