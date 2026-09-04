"""Safe types — bibliofabric re-exports plus Crossref-local variants."""

from typing import Annotated

from bibliofabric.safe_types import SafeList, SafeStr
from pydantic import BeforeValidator

#: Coerces ``None`` → ``0`` (Crossref occasionally nulls numeric fields).
SafeInt = Annotated[int, BeforeValidator(lambda v: 0 if v is None else v)]

#: Like ``SafeList[str]`` but also wraps a bare string into a single-element
#: list. Needed because single-item routes return scalars where list routes
#: return arrays (e.g. ``/journals/{issn}`` returns ``title: "Nature"`` while
#: ``/journals`` returns ``title: ["Nature"]``).
SafeStrList = Annotated[
    list[str],
    BeforeValidator(
        lambda v: (
            []
            if v is None
            else [v]
            if isinstance(v, str)
            else [x for x in v if x is not None]
        )
    ),
]

#: ``SafeStr`` that also strips the ``https://id.crossref.org/{kind}/`` stem.
#: ``/prefixes/{prefix}`` returns ``member``/``prefix`` as full URIs
#: (``https://id.crossref.org/prefix/10.1038``); models normalize to bare values.
IdSafeStr = Annotated[
    SafeStr,
    BeforeValidator(
        lambda v: (
            v.rsplit("/", 1)[-1]
            if isinstance(v, str) and v.startswith("https://id.crossref.org/")
            else v
        )
    ),
]

__all__ = ["IdSafeStr", "SafeInt", "SafeList", "SafeStr", "SafeStrList"]
