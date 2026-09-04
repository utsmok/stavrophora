# Stavrophora: Asynchronous Python client for the Crossref API

Samuel Mok -- s.mok@utwente.nl -- 2026

Stavrophora is an async Python client for the [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), built on [bibliofabric](https://github.com/utsmok/bibliofabric).

**License:** MIT

## Features

- **Async by design** -- built on `httpx` + `asyncio` with proper connection pooling
- **Typed end-to-end** -- Pydantic v2 models with `extra="allow"` (the Crossref spec is incomplete; extra fields are preserved, never dropped)
- **Cursor pagination** -- `async for work in session.works.iterate(...)` over `message.next-cursor`
- **Polite pool by default** -- one `mailto=` line triples your rate limit
- **Batch DOI lookup** -- comma-separated repeated `filter=doi:` keys (Crossref's supported OR form)
- **Scoped works** -- `session.journals.works(issn)`, `session.funders.works(id)`, `session.prefixes.works(prefix)`

## Installation

```bash
uv add stavrophora
```

Or with pip: `pip install stavrophora`. Requires Python >=3.12.

## Quick Start

```python
import asyncio
from stavrophora import StavrophoraSession


async def main():
    async with StavrophoraSession(mailto="you@example.org") as session:
        # Get a single work by DOI
        work = await session.works.get("10.1038/nature12373")
        print(work.title[0], work.issued.date_parts)

        # Search
        response = await session.works.search(search="crow nesting", page_size=5)
        for item in response.message.items:
            print(item.doi, item.is_referenced_by_count)


asyncio.run(main())
```

No authentication required. Pass a `mailto` (parameter or `STAVROPHORA_MAILTO` env var) to use the polite pool: verified live 2026-09, anonymous requests are capped at 1 request/s and 1 concurrent request, polite at 3/s and 3 concurrent (advertised in the `x-rate-limit-*` response headers). Both the `mailto` query parameter and `mailto:` in the User-Agent are honored; stavrophora uses the query parameter.

## Basic Usage

### Get a single entity

```python
work = await session.works.get("10.1038/nature12373")  # DOI (bare or doi.org-prefixed)
journal = await session.journals.get("0028-0836")  # ISSN or eISSN
funder = await session.funders.get("10.13039/501100000923")
member = await session.members.get("78")  # e.g. Elsevier
prefix = await session.prefixes.get("10.1016")  # no /prefixes list route exists
```

### Search, sort, filter, select

```python
from stavrophora.endpoints import WorksFilters

response = await session.works.search(
    filters=WorksFilters(type="journal-article", from_pub_date="2026-01-01"),
    sort_by="is-referenced-by-count:desc",
    select=["DOI", "title", "is-referenced-by-count"],
    page_size=20,
)
```

Crossref has **no publisher filter** (400, verified live); scope by `prefix`, `member` or `ror-id` instead.

### Iterate all results (cursor)

```python
async for work in session.works.iterate(
    filters={"from-index-date": "2026-08-01"}, page_size=1000
):
    process(work)
```

The last non-empty page still carries a `next-cursor`; stavrophora follows cursors until the API returns an empty page (one extra request, by design).

### Scoped works

```python
nature_works = session.journals.works("0028-0836")
response = await nature_works.search(page_size=5)

ut_works = session.prefixes.works("10.3990")  # UT student theses
async for w in ut_works.iterate(page_size=1000):
    ...
```

### Batch DOI lookup

```python
found = await session.works.batch_get_by_doi(
    ["10.1038/nature12373", "10.1103/PhysRevLett.116.061102"]
)
```

Keys are normalized bare lowercase DOIs; misses are absent from the dict. Requests are batched 50 DOIs per call via repeated `filter=doi:` keys (the pipe form `doi:a|b` returns **zero** results -- verified live).

### Registration agency

```python
agency = await session.works.agency("10.1038/nature12373")
print(agency.agency.label)  # "Crossref"
```

## Configuration

Settings load from env vars prefixed `STAVROPHORA_` (or `.env` / `secrets.env`):

```dotenv
STAVROPHORA_MAILTO=s.mok@utwente.nl
```

All bibliofabric settings (`REQUEST_TIMEOUT`, `MAX_RETRIES`, ...) are inherited under the same prefix.

## Known Crossref API Quirks

- **No pipe-OR in filters.** `filter=doi:a|b` silently returns 0 results (OpenAlex-style). Repeated `key:value` pairs (`filter=doi:a,doi:b`) are the supported OR form.
- **Unknown query parameters are rejected with 400** (no silent ignoring). The client therefore sends only `rows`, `offset`, `query`, `filter`, `sort`, `order`, `select`, `cursor`, `mailto`.
- **`page` is not a parameter** -- paging is `offset` (0-based, capped at 10,000 total) + `rows` (max 1000, 400 otherwise). Deep paging must use `cursor`.
- **Cursor exhaustion is implicit**: the last non-empty page still returns a `next-cursor`; only the following request returns an empty `items` and no cursor.
- **`/prefixes` has no list route** (404) -- only `/prefixes/{prefix}` and `/prefixes/{prefix}/works`. **`/licenses` has no single-item route** (404) -- only the list.
- **The `message` envelope is one level deep** for everything: single items live in `message`, lists in `message.items` with totals in `message.total-results`.
- **Rate limits changed 2025-12-01**: anonymous 1 req/s / 1 concurrent, polite 3 req/s / 3 concurrent (older docs say 5/10 req/s). Polite status is observable: only mailto-stamped requests carry `x-rate-limit-*` response headers.
- **API is served at both `https://api.crossref.org` and `.../v1`** with identical payloads (verified 2026-09); stavrophora pins `/v1`, the versioned form.
- **The Crossref spec is incomplete** -- several returned fields are missing from the official schema. All models use `extra="allow"`, same defense as aletheca.
- **Schemas differ between list and single-item routes** (verified live): `/journals/{issn}` returns `title` as a bare string while `/journals` returns a list; member `prefix` entries are `{name, value}` objects. The models normalize both shapes (`SafeStrList`, dict-typed prefix entries).

## Development

```bash
uv sync
uv run pytest                    # mocked tests (live tests excluded by default)
uv run pytest -m live_api        # live API smoke tests
uv run ruff check .
uvx ty check src/
```

## License

MIT
