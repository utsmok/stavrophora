"""Constants used throughout the Stavrophora library."""

from importlib.metadata import PackageNotFoundError, version as _get_version

CROSSREF_API_BASE_URL = "https://api.crossref.org/v1"

DEFAULT_TIMEOUT: int = 30
DEFAULT_RETRIES: int = 3
DEFAULT_PAGE_SIZE: int = 25
#: Crossref caps ``rows`` at 1000; cursor iteration uses the maximum.
ITERATE_PAGE_SIZE: int = 1000
#: Maximum identifiers per comma-separated ``filter=doi:...`` batch.
BATCH_GET_SIZE: int = 50

try:
    __version__: str = _get_version("stavrophora")
except PackageNotFoundError:
    __version__: str = "0.0.0"

DEFAULT_USER_AGENT: str = f"stavrophora/{__version__}"
CLIENT_HEADERS: dict[str, str] = {
    "accept": "application/json",
    "User-Agent": DEFAULT_USER_AGENT,
}
