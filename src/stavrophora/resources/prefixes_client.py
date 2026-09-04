"""Client for the Crossref Prefixes endpoint.

Crossref has no ``/prefixes`` list route (verified live: 404); prefixes
are only addressable individually, with a works sub-resource.
"""

from typing import TYPE_CHECKING

from bibliofabric.exceptions import BibliofabricError
from bibliofabric.log_config import logger
from bibliofabric.resources import GettableMixin

from ..models import Prefix
from ..resources._standard import StavrophoraResourceClient
from ..resources.works_client import ScopedWorksClient

if TYPE_CHECKING:
    from ..client import StavrophoraClient


class PrefixesClient(StavrophoraResourceClient, GettableMixin):
    """Client for the Crossref Prefixes API endpoint (get + scoped works only)."""

    _entity_path: str = "prefixes"
    _entity_model = Prefix
    _supports_direct_get: bool = True

    def __init__(self, api_client: "StavrophoraClient"):
        super().__init__(api_client)
        logger.debug("PrefixesClient initialized.")

    async def search(self, *_args, **_kwargs):
        """Not supported: Crossref serves no ``/prefixes`` list route."""
        raise BibliofabricError(
            "Crossref has no /prefixes list route; use get(prefix) or works(prefix)."
        )

    def works(self, prefix: str) -> ScopedWorksClient:
        """Get a works client scoped to a DOI prefix.

        Args:
            prefix: DOI prefix (e.g. ``10.1016``).

        Returns:
            A :class:`ScopedWorksClient` bound to ``prefixes/{prefix}/works``.
        """
        return ScopedWorksClient(self._api_client, f"prefixes/{prefix}/works")
