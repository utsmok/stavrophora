"""Pydantic models for the Work entity and its nested types."""

from pydantic import AliasChoices, BaseModel, Field
from pydantic.config import ConfigDict

from .base import (
    Contributor,
    CrossRefDate,
    FunderRef,
    LicenseRef,
)
from .safe_types import SafeInt, SafeList, SafeStr, SafeStrList


class Work(BaseModel):
    """A Crossref work record.

    Field names are snake_case with kebab-case aliases matching the live
    API keys (``DOI``, ``container-title``, ``is-referenced-by-count``,
    ...). The Crossref spec is incomplete — ``extra="allow"`` keeps any
    field the API returns but the model does not declare.
    """

    # Identity
    doi: SafeStr | None = Field(None, alias="DOI")
    url: str | None = Field(None, alias="URL")
    title: SafeList[str] = Field(default_factory=list)
    subtitle: SafeList[str] = Field(default_factory=list)
    original_title: SafeList[str] = Field(default_factory=list, alias="original-title")
    short_title: SafeList[str] = Field(default_factory=list, alias="short-title")
    container_title: SafeList[str] = Field(
        default_factory=list, alias="container-title"
    )

    # People
    author: SafeList[Contributor] = Field(default_factory=list)
    editor: SafeList[Contributor] = Field(default_factory=list)
    translator: SafeList[Contributor] = Field(default_factory=list)

    # Dates
    issued: CrossRefDate | None = None
    published: CrossRefDate | None = None
    published_print: CrossRefDate | None = Field(None, alias="published-print")
    published_online: CrossRefDate | None = Field(None, alias="published-online")
    created: CrossRefDate | None = None
    deposited: CrossRefDate | None = None
    indexed: CrossRefDate | None = None
    approved: CrossRefDate | None = None
    posted: CrossRefDate | None = None
    accepted: CrossRefDate | None = None

    # Classification
    type: str | None = None
    publisher: SafeStr | None = None
    language: SafeStr | None = None
    subject: SafeList[str] = Field(default_factory=list)

    # Citation metrics
    is_referenced_by_count: SafeInt = Field(0, alias="is-referenced-by-count")
    references_count: SafeInt = Field(
        0, validation_alias=AliasChoices("references-count", "reference-count")
    )

    # Bibliographic
    issn: SafeList[str] = Field(default_factory=list, alias="ISSN")
    isbn: SafeList[str] = Field(default_factory=list, alias="ISBN")
    issn_type: SafeList[dict] = Field(default_factory=list, alias="issn-type")
    isbn_type: SafeList[dict] = Field(default_factory=list, alias="isbn-type")
    page: SafeStr | None = None
    volume: SafeStr | None = None
    issue: SafeStr | None = None
    article_number: SafeStr | None = Field(None, alias="article-number")
    edition_number: SafeStr | None = Field(None, alias="edition-number")

    # Content
    abstract: SafeStr | None = None
    license: SafeList[LicenseRef] = Field(default_factory=list)
    funder: SafeList[FunderRef] = Field(default_factory=list)
    reference: SafeList[dict] = Field(default_factory=list)
    link: SafeList[dict] = Field(default_factory=list)
    alternative_id: SafeList[str] = Field(default_factory=list, alias="alternative-id")

    # Provenance / relations
    member: int | str | None = None
    prefix: SafeStr | None = None
    resource: dict | None = None
    content_domain: dict | None = Field(None, alias="content-domain")
    relation: dict | None = None
    update_policy: SafeStr | None = Field(None, alias="update-policy")
    update_to: SafeStr | SafeList[dict] | None = Field(None, alias="update-to")
    group_title: SafeStr | None = Field(None, alias="group-title")
    clinical_trial_number: SafeList[dict] = Field(
        default_factory=list, alias="clinical-trial-number"
    )
    #: Live API returns bare archive names (``["CLOCKSS", "LOCKSS", "Portico"]``).
    archive: SafeStrList = Field(default_factory=list)
    assertion: SafeList[dict] = Field(default_factory=list)
    event: dict | None = None
    agent: SafeStr | None = None
    institution: SafeList[dict] = Field(default_factory=list)
    standards_body: SafeList[dict] = Field(default_factory=list, alias="standards-body")

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @property
    def primary_title(self) -> str:
        """First title string, or ``""`` when absent (SafeStr-style access)."""
        return self.title[0] if self.title else ""
