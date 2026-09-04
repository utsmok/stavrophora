# Stavrophora

**Python interface for the Crossref API**, built on [bibliofabric](https://github.com/utsmok/bibliofabric).

Stavrophora provides a fully-typed, async-first Python client for the [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) — the DOI registration agency metadata service. It wraps the works, journals, funders, members, types, prefixes and licenses endpoints with Pydantic models, Crossref filter serialization, and cursor-based pagination.

## Why stavrophora?

- **Async-native** — every operation is `async`, designed for modern Python (3.12+).
- **Typed end-to-end** — Pydantic v2 models for all entities, `extra="allow"` because the Crossref spec is incomplete.
- **Polite pool by default** — one `mailto=` line (`STAVROPHORA_MAILTO` env or parameter) triples the rate limit.
- **Built on bibliofabric** — inherits robust HTTP handling, retries, and reactive rate limiting from the same framework behind aletheca and AIREloom.

## Quick peek

```python
import asyncio
from stavrophora import StavrophoraSession


async def main():
    async with StavrophoraSession(mailto="you@example.org") as session:
        work = await session.works.get("10.1038/nature12373")
        print(work.primary_title)


asyncio.run(main())
```

## Features

| Feature | Description |
|---|---|
| Entity clients | Works, Journals, Funders, Members, Types, Prefixes, Licenses |
| Pydantic filter models | `WorksFilters(type="journal-article", from_pub_date="2026-01-01")` |
| Cursor pagination | `async for work in session.works.iterate(...):` |
| Batch DOI lookup | `await session.works.batch_get_by_doi([...])` (repeated `filter=doi:` OR keys) |
| Scoped works | `session.journals.works(issn)`, `session.funders.works(id)`, `session.prefixes.works(prefix)` |
| Field projection | `select=["DOI", "title", "is-referenced-by-count"]` |
| Sort + order | `sort_by="is-referenced-by-count:desc"` |
| Registration agency | `await session.works.agency(doi)` |
| Polite pool | Env var `STAVROPHORA_MAILTO` or explicit `mailto=` parameter |

See the project README for the full set of live-verified Crossref API quirks the client defends against.
