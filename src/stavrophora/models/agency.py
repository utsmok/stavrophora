"""Pydantic model for the DOI registration agency lookup."""

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .safe_types import SafeStr


class Agency(BaseModel):
    """Registration agency for a DOI."""

    id: SafeStr | None = None
    label: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class WorkAgency(BaseModel):
    """Response of ``GET /works/{doi}/agency``."""

    doi: SafeStr | None = Field(None, alias="DOI")
    agency: Agency | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)
