"""StavrophoraResourceClient — base class for all Crossref resource clients.

Overrides bibliofabric's parameter names and query serialization for
Crossref-specific conventions:

- ``rows`` for page size, ``offset`` (0-based) for paging, ``query`` for search
- ``filter=key:value,key:value`` — repeated keys OR, distinct keys AND
- ``sort=<field>&order=asc|desc`` — expressed as ``sort_by="field:desc"``
- ``select=DOI,title,...`` field projection

Subclasses that declare ``_batch_fields`` automatically get
``batch_get_by_<name>()`` convenience methods at class-creation time.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

from bibliofabric.exceptions import BibliofabricError
from bibliofabric.log_config import logger
from bibliofabric.resources import BaseResourceClient, OnError
from pydantic import BaseModel

from .._helpers import normalize_doi

#: Maximum identifiers per comma-separated filter (safe under URL limits).
BATCH_GET_SIZE = 50

#: Marker keys used to carry sort/order/select hints inside the filters dict
#: when delegating to the framework's cursor iterator. Never sent as filters.
_SORT_KEY = "__sort__"
_ORDER_KEY = "__order__"
_SELECT_KEY = "__select__"


def _format_filter_value(value: Any) -> str:
    """Render a filter value; booleans lowercase like Crossref expects."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _make_batch_getter(field: str) -> Any:
    """Return an async method that delegates to :meth:`batch_get`."""

    async def _batch_get_by(
        self: StavrophoraResourceClient,
        identifiers: list[str],
        *,
        batch_size: int = BATCH_GET_SIZE,
    ) -> dict[str, Any]:
        return await self.batch_get(identifiers, field=field, batch_size=batch_size)

    return _batch_get_by


class StavrophoraResourceClient(BaseResourceClient):
    """Base for all Crossref resource clients.

    Sets Crossref parameter names and serializes filters into the single
    ``filter=key:value,...`` query parameter.
    """

    #: The API path for the resource; every concrete subclass must set it.
    _entity_path: str
    #: Held loosely: subclasses pass any client exposing ``request()``.
    _api_client: Any

    _param_page_size: str = "rows"
    _param_sort: str = "sort"
    _param_search: str = "query"
    #: Set by concrete subclasses to parse search envelopes.
    _search_response_model: Any = None

    #: Maps ``method_suffix`` → ``filter_field``; auto-generates
    #: ``batch_get_by_<suffix>()`` methods on subclasses.
    _batch_fields: dict[str, str] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for suffix, field in getattr(cls, "_batch_fields", {}).items():
            method_name = f"batch_get_by_{suffix}"
            if not hasattr(cls, method_name):
                setattr(cls, method_name, _make_batch_getter(field))

    def _serialize_filters(
        self, filters: BaseModel | dict[str, Any] | None
    ) -> dict[str, Any]:
        """Serialize filters into Crossref's ``filter`` query parameter.

        Crossref syntax::

            filter=type:journal-article,from-pub-date:2024-01-01
            filter=doi:10.1038/a,doi:10.1038/b      # repeated keys = OR

        List values become repeated keys. Bool values lowercase. Marker
        keys (``_SORT_KEY``/``_ORDER_KEY``/``_SELECT_KEY``) are extracted,
        never serialized as filters; the order/select markers (used when
        delegating to the framework cursor iterator) become parameters.
        """
        if filters is None:
            filter_dict: dict[str, Any] = {}
        elif isinstance(filters, BaseModel):
            filter_dict = filters.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(filters, dict):
            filter_dict = dict(filters)
        else:
            raise BibliofabricError(
                f"filters must be a Pydantic model or dictionary, got {type(filters)}"
            )
        filter_dict.pop(_SORT_KEY, None)
        order = filter_dict.pop(_ORDER_KEY, None)
        select = filter_dict.pop(_SELECT_KEY, None)

        params: dict[str, Any] = {}
        if filter_dict:
            parts = []
            for key, value in filter_dict.items():
                if isinstance(value, list | tuple | set):
                    parts.extend(f"{key}:{_format_filter_value(v)}" for v in value)
                else:
                    parts.append(f"{key}:{_format_filter_value(value)}")
            params["filter"] = ",".join(parts)
        if order is not None:
            params["order"] = order
        if select is not None:
            params["select"] = ",".join(select)
        return params

    async def search(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        filters: BaseModel | dict[str, Any] | None = None,
        search: str | None = None,
        select: list[str] | None = None,
    ) -> BaseModel | dict[str, Any]:
        """Search with Crossref's ``offset``/``rows`` paging.

        Args:
            page: Page number (1-indexed); translated to ``offset``.
            page_size: Results per request (``rows``, max 1000).
            sort_by: ``"field"`` or ``"field:asc"`` / ``"field:desc"``.
            filters: Filter criteria as a Pydantic model or dictionary.
            search: Free-text query (``query`` parameter).
            select: Field projection, e.g. ``["DOI", "title"]``.

        Returns:
            Parsed ``ApiResponse`` model (or raw dict if parsing fails).
        """
        merged = self._merge_query_hints(filters, sort_by, select)
        sort_field = merged.pop(_SORT_KEY, None)
        order = merged.pop(_ORDER_KEY, None)
        select_list = merged.pop(_SELECT_KEY, None)
        params = self._serialize_filters(merged or None)
        if sort_field:
            params["sort"] = sort_field
        if order:
            params["order"] = order
        if select_list:
            params["select"] = ",".join(select_list)
        params["offset"] = max(page - 1, 0) * page_size
        params["rows"] = page_size
        if search is not None:
            params["query"] = search
        try:
            response = await self._api_client.request(
                "GET",
                self._entity_path,
                params=params,
                base_url_override=self._base_url_override,
            )
            response_data = response.json()
            if self._search_response_model:
                try:
                    return self._search_response_model.model_validate(response_data)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse search response with "
                        f"{self._search_response_model.__name__}: {e}. "
                        "Returning raw data."
                    )
                    return response_data
            return response_data
        except Exception as e:
            if isinstance(e, BibliofabricError):
                raise
            logger.exception(
                f"Failed to search {self._entity_path} with params {params}"
            )
            raise BibliofabricError(
                f"Unexpected error searching {self._entity_path}: {e}"
            ) from e

    async def iterate(
        self,
        page_size: int = 100,
        sort_by: str | None = None,
        filters: BaseModel | dict[str, Any] | None = None,
        search: str | None = None,
        select: list[str] | None = None,
        *,
        cursor: str | None = None,
        on_error: OnError = "raw",
        failures: list[tuple[dict[str, Any], Exception]] | None = None,
        on_page: Callable[[int, str | None], Any] | None = None,
    ) -> AsyncIterator[Any]:
        """Iterate through all matching entities using Crossref cursor pagination.

        Sends ``cursor=*`` for the first request and follows
        ``message.next-cursor`` until a page comes back empty (the last
        non-empty page still carries a cursor — the API emits one extra
        empty page before the cursor disappears).

        Args:
            page_size: Results per request (``rows``, max 1000).
            sort_by: ``"field"`` or ``"field:asc"`` / ``"field:desc"``.
            filters: Filter criteria as a Pydantic model or dictionary.
            search: Free-text query.
            select: Field projection.
            cursor: Resume from a previously emitted cursor (bibliofabric 0.5).
            on_error: Parse-failure policy (``raw`` preserves legacy yields).
            failures: Optional collector for ``(record, exception)`` pairs.
            on_page: Optional ``(page_number, cursor)`` callback.
        """
        merged = self._merge_query_hints(filters, sort_by, select)
        sort_field = merged.pop(_SORT_KEY, None)
        async for entity in super().iterate(  # ty: ignore[unresolved-attribute]
            page_size=page_size,
            sort_by=sort_field,
            filters=merged,
            search=search,
            cursor=cursor,
            on_error=on_error,
            failures=failures,
            on_page=on_page,
        ):
            yield entity

    @staticmethod
    def _merge_query_hints(
        filters: BaseModel | dict[str, Any] | None,
        sort_by: str | None,
        select: list[str] | None,
    ) -> dict[str, Any]:
        """Encode sort/order/select into a filters dict of parameters.

        Splits ``sort_by="field:desc"`` into the ``sort`` field (marker key)
        and ``order`` (marker key); ``select`` rides the select marker.
        """
        if filters is None:
            merged: dict[str, Any] = {}
        elif isinstance(filters, BaseModel):
            merged = filters.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(filters, dict):
            merged = dict(filters)
        else:
            raise BibliofabricError(
                f"filters must be a Pydantic model or dictionary, got {type(filters)}"
            )
        if sort_by:
            field, _, order = str(sort_by).partition(":")
            merged[_SORT_KEY] = field.strip()
            if order:
                merged[_ORDER_KEY] = order.strip().lower()
        if select:
            merged[_SELECT_KEY] = list(select)
        return merged

    async def count(
        self,
        *,
        filters: BaseModel | dict[str, Any] | None = None,
        search: str | None = None,
    ) -> int:
        """Return total number of matching entities.

        Performs a minimal search (rows=1) and reads
        ``message.total-results``.
        """
        response = await self.search(
            page=1, page_size=1, filters=filters, search=search
        )
        if isinstance(response, BaseModel):
            message = getattr(response, "message", None)
            total = getattr(message, "total_results", None)
            if total is not None:
                return int(total)
        return 0

    async def batch_get(
        self,
        identifiers: list[str],
        *,
        field: str = "doi",
        key_fn: Callable[[Any], str] | None = None,
        batch_size: int = BATCH_GET_SIZE,
    ) -> dict[str, Any]:
        """Retrieve multiple entities by identifier in batched filter queries.

        Splits *identifiers* into groups of *batch_size* and issues one
        ``search`` per group using Crossref's repeated-key OR syntax::

            filter=doi:10.1038/a,doi:10.1038/b,...

        Note: Crossref has no pipe-separated OR — the pipe syntax returns
        zero results (verified live); repeated ``key:value`` pairs are the
        supported form.

        Args:
            identifiers: Values to look up (DOIs).
            field: Filter field name (``"doi"``).
            key_fn: Optional function to extract the lookup key from a
                parsed entity. Defaults to normalizing ``entity.<field>``.
            batch_size: Max identifiers per API call.

        Returns:
            Dict mapping each normalized identifier to its parsed entity.
            Identifiers not found are absent from the dict.
        """
        if not identifiers:
            return {}
        batch_size = max(1, min(batch_size, BATCH_GET_SIZE))
        results: dict[str, Any] = {}
        for i in range(0, len(identifiers), batch_size):
            batch = identifiers[i : i + batch_size]
            response = await self.search(
                page=1,
                page_size=len(batch),
                filters={field: list(batch)},
            )
            entities = self._extract_results(response)
            for entity in entities:
                key = self._resolve_key(entity, field, key_fn)
                if key is not None:
                    results[key] = entity
        return results

    @staticmethod
    def _extract_results(response: Any) -> list[Any]:
        """Pull the results list from a search response (model or raw dict)."""
        if isinstance(response, BaseModel):
            message = getattr(response, "message", None)
            if message is not None:
                return list(getattr(message, "items", []) or [])
        if isinstance(response, dict):
            message = response.get("message")
            if isinstance(message, dict):
                return list(message.get("items") or [])
        return []

    @staticmethod
    def _resolve_key(
        entity: Any,
        field: str,
        key_fn: Callable[[Any], str] | None,
    ) -> str | None:
        """Derive the lookup key from a parsed entity."""
        if key_fn is not None:
            return key_fn(entity)
        raw = getattr(entity, field, None) if isinstance(entity, BaseModel) else None
        if raw is None and isinstance(entity, dict):
            raw = entity.get(field)
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0] if raw else None
            if raw is None:
                return None
        raw = str(raw)
        if field == "doi":
            return normalize_doi(raw)
        return raw.strip().lower()
