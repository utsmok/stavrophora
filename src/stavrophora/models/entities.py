"""Pydantic models for Crossref journal, funder, member, type, prefix and license entities."""

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .safe_types import SafeList, SafeStr, SafeStrList


class Journal(BaseModel):
    """A Crossref journal (list item and ``/journals/{issn}`` record)."""

    #: bare string on ``/journals/{issn}``, list on ``/journals`` — SafeStrList handles both
    title: SafeStrList = Field(default_factory=list)
    publisher: SafeStr | None = None
    issn: SafeList[str] = Field(default_factory=list, alias="ISSN")
    issn_type: SafeList[dict] = Field(default_factory=list, alias="issn-type")
    counts: dict | None = None
    coverage: dict | None = None
    coverage_type: dict | None = Field(None, alias="coverage-type")
    flags: dict | None = None
    breakdowns: dict | None = None
    subjects: SafeList[str] = Field(default_factory=list)
    last_status_check_time: float | None = Field(None, alias="last-status-check-time")

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @property
    def primary_title(self) -> str:
        """First title string, or ``""`` when absent."""
        return self.title[0] if self.title else ""


class Funder(BaseModel):
    """A Crossref funder (Funder Registry record)."""

    id: SafeStr | None = None
    name: SafeStr | None = None
    tokens: SafeList[str] = Field(default_factory=list)
    uri: SafeStr | None = None
    location: SafeStr | None = None
    alt_names: SafeList[str] = Field(default_factory=list, alias="alt-names")
    replaces: SafeList[str] = Field(default_factory=list)
    replaced_by: SafeList[str] = Field(default_factory=list, alias="replaced-by")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Member(BaseModel):
    """A Crossref member (publisher account)."""

    id: int | None = None
    primary_name: SafeStr | None = Field(None, alias="primary-name")
    names: SafeList[str] = Field(default_factory=list)
    prefixes: SafeList[str] = Field(default_factory=list)
    #: ``prefix`` entries are ``{name, value}`` objects on the live API.
    prefix: SafeList[dict] = Field(default_factory=list)
    tokens: SafeList[str] = Field(default_factory=list)
    location: SafeStr | None = None
    counts: dict | None = None
    coverage: dict | None = None
    coverage_type: dict | None = Field(None, alias="coverage-type")
    flags: dict | None = None
    breakdowns: dict | None = None
    last_status_check_time: float | None = Field(None, alias="last-status-check-time")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class CrossRefType(BaseModel):
    """A Crossref work type (e.g. ``journal-article``)."""

    id: SafeStr | None = None
    label: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class Prefix(BaseModel):
    """A Crossref DOI prefix owned by a member."""

    member: SafeStr | None = None
    name: SafeStr | None = None
    prefix: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class License(BaseModel):
    """A Crossref license (list item on ``/licenses``)."""

    url: str | None = Field(None, alias="URL")
    work_count: int = Field(0, alias="work-count")

    model_config = ConfigDict(extra="allow", populate_by_name=True)
