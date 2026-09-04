"""StavrophoraClient — async client for the Crossref API."""

from bibliofabric.auth import AuthStrategy, NoAuth, QueryParameterAuth
from bibliofabric.client import BaseApiClient
from bibliofabric.log_config import logger

from .config import StavrophoraSettings, get_settings
from .constants import CROSSREF_API_BASE_URL
from .resources.funders_client import FundersClient
from .resources.journals_client import JournalsClient
from .resources.licenses_client import LicensesClient
from .resources.members_client import MembersClient
from .resources.prefixes_client import PrefixesClient
from .resources.types_client import TypesClient
from .resources.works_client import WorksClient
from .unwrapper import CrossrefUnwrapper


class StavrophoraClient(BaseApiClient):
    """Asynchronous client for the Crossref API.

    Provides access to all Crossref entity endpoints through typed resource
    client properties.

    Usage::

        async with StavrophoraClient(
            mailto="you@example.org"
        ) as client:
            work = await client.works.get("10.1038/nature12373")
    """

    def __init__(
        self,
        settings: StavrophoraSettings | None = None,
        *,
        mailto: str | None = None,
        base_url: str | None = None,
        auth_strategy: AuthStrategy | None = None,
    ):
        """Initialize the StavrophoraClient.

        Args:
            settings: Optional StavrophoraSettings instance. If None, loads from env.
            mailto: Contact email for the Crossref polite pool (overrides
                settings). Sent as a ``mailto`` query parameter on every
                request. Ignored when ``auth_strategy`` is also provided.
            base_url: Optional API base URL override.
            auth_strategy: Optional auth strategy override. When provided,
                takes precedence over ``mailto``.
        """
        self._settings = settings or get_settings()
        resolved_mailto = mailto or self._settings.mailto
        resolved_base_url = base_url or CROSSREF_API_BASE_URL

        if auth_strategy is not None:
            auth = auth_strategy
        elif resolved_mailto:
            auth = QueryParameterAuth("mailto", resolved_mailto)
        else:
            auth = NoAuth()

        super().__init__(
            settings=self._settings,
            response_unwrapper=CrossrefUnwrapper(),
            auth_strategy=auth,
            base_url=resolved_base_url,
        )

        # Resource clients will be initialized lazily as properties
        self._works = None
        self._journals = None
        self._funders = None
        self._members = None
        self._types = None
        self._prefixes = None
        self._licenses = None

        logger.debug("StavrophoraClient initialized successfully.")

    # --- Resource client properties (lazy init) ---

    @property
    def works(self):
        """Access the Works endpoint client."""
        if self._works is None:
            self._works = WorksClient(self)
        return self._works

    @property
    def journals(self):
        """Access the Journals endpoint client."""
        if self._journals is None:
            self._journals = JournalsClient(self)
        return self._journals

    @property
    def funders(self):
        """Access the Funders endpoint client."""
        if self._funders is None:
            self._funders = FundersClient(self)
        return self._funders

    @property
    def members(self):
        """Access the Members endpoint client."""
        if self._members is None:
            self._members = MembersClient(self)
        return self._members

    @property
    def types(self):
        """Access the Types endpoint client."""
        if self._types is None:
            self._types = TypesClient(self)
        return self._types

    @property
    def prefixes(self):
        """Access the Prefixes endpoint client."""
        if self._prefixes is None:
            self._prefixes = PrefixesClient(self)
        return self._prefixes

    @property
    def licenses(self):
        """Access the Licenses endpoint client."""
        if self._licenses is None:
            self._licenses = LicensesClient(self)
        return self._licenses
