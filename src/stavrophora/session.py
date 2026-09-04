"""StavrophoraSession — high-level async context manager for Crossref API access."""

from bibliofabric.log_config import configure_logging, logger

from .client import StavrophoraClient
from .config import StavrophoraSettings, get_settings

_DELEGATED_CLIENTS = frozenset(
    {
        "works",
        "journals",
        "funders",
        "members",
        "types",
        "prefixes",
        "licenses",
    }
)

configure_logging()


class StavrophoraSession:
    """High-level session manager for interacting with the Crossref API.

    Delegates attribute access to the underlying StavrophoraClient resource
    properties (``session.works``, ``session.journals``, ...).

    Usage::

        async with StavrophoraSession(
            mailto="you@example.org"
        ) as session:
            work = await session.works.get("10.1038/nature12373")
    """

    def __init__(
        self,
        settings: StavrophoraSettings | None = None,
        *,
        mailto: str | None = None,
        base_url: str | None = None,
    ):
        """Initialize the StavrophoraSession.

        Args:
            settings: Optional StavrophoraSettings instance. If None, loads from env.
            mailto: Contact email for the Crossref polite pool (overrides settings).
            base_url: Optional API base URL override.
        """
        self._settings = settings or get_settings()
        self._api_client = StavrophoraClient(
            self._settings, mailto=mailto, base_url=base_url
        )
        logger.debug("StavrophoraSession initialized.")

    def __getattr__(self, name: str):
        if name in _DELEGATED_CLIENTS:
            return getattr(self._api_client, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __dir__(self):
        return list(super().__dir__()) + list(_DELEGATED_CLIENTS)

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        await self._api_client.aclose()

    async def __aenter__(self) -> "StavrophoraSession":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
