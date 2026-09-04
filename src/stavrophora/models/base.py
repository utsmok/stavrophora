"""Base Pydantic models for the Crossref API response envelope."""

from typing import TypeVar

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .safe_types import SafeList

EntityType = TypeVar("EntityType", bound=BaseModel)


class Message[EntityType: BaseModel](BaseModel):
    """Body of a Crossref list response (the ``message`` envelope member)."""

    total_results: int | None = Field(None, alias="total-results")
    items_per_page: int | None = Field(None, alias="items-per-page")
    next_cursor: str | None = Field(None, alias="next-cursor")
    query: dict | None = None
    facets: dict | None = None
    items: list[EntityType] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class ApiResponse[EntityType: BaseModel](BaseModel):
    """Generic envelope for all Crossref responses.

    Every Crossref response is ``{status, message-type, message-version,
    message}``; list responses carry ``Message``-shaped ``message`` bodies.
    """

    status: str | None = None
    message_type: str | None = Field(None, alias="message-type")
    message_version: str | None = Field(None, alias="message-version")
    message: Message[EntityType] = Field(default_factory=Message)

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class CrossRefDate(BaseModel):
    """Crossref date object (``issued``, ``published``, ``created``, ...).

    Shape: ``{"date-parts": [[2021, 6, 11]], "timestamp": ..., "source": ...}``
    """

    date_parts: SafeList[SafeList[int]] = Field(
        default_factory=list, alias="date-parts"
    )
    date_time: str | None = Field(None, alias="date-time")
    timestamp: int | None = None
    source: str | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @property
    def year(self) -> int | None:
        """First year of the first date part, if present."""
        for part in self.date_parts:
            if part:
                return part[0]
        return None


class IssnType(BaseModel):
    """ISSN with its type (print/electronic)."""

    type: str | None = None
    value: str | None = None

    model_config = ConfigDict(extra="allow")


class LicenseRef(BaseModel):
    """License entry on a work."""

    url: str | None = Field(None, alias="URL")
    content_version: str | None = Field(None, alias="content-version")
    delay: int | None = None
    start: CrossRefDate | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class FunderRef(BaseModel):
    """Funder entry on a work (Funder Registry DOI + award numbers)."""

    name: str | None = None
    doi: str | None = Field(None, alias="DOI")
    award: SafeList[str] = Field(default_factory=list)
    doi_asserted: bool | None = Field(None, alias="doi-asserted")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Contributor(BaseModel):
    """Author/editor/contributor on a work."""

    given: str | None = None
    family: str | None = None
    name: str | None = None
    orcid: str | None = None
    affiliation: SafeList[dict] = Field(default_factory=list)
    sequence: str | None = None
    authenticated_orcid: bool | None = Field(None, alias="authenticated-orcid")
    suffix: str | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)
