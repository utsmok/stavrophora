"""Utility helpers for working with Crossref identifiers."""

from __future__ import annotations

from urllib.parse import quote


def normalize_doi(doi: str) -> str:
    """Normalize a DOI to its bare, lowercase form.

    Strips ``https://doi.org/``, ``http://doi.org/`` and ``doi.org/``
    prefixes and lowercases the result (Crossref treats DOIs
    case-insensitively and returns them lowercased).

    Args:
        doi: A DOI, possibly URL-prefixed or mixed-case.

    Returns:
        The bare lowercase DOI (e.g. ``10.1038/nature12373``).
    """
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix) :]
            break
    return doi.lower()


def encode_doi_path(doi: str) -> str:
    """Percent-encode a DOI for use in a URL path segment.

    Crossref recommends encoding DOIs in paths; bare ``/`` stays readable
    but characters like ``#`` or ``?`` must never leak into the URL raw.

    Args:
        doi: Bare or URL-prefixed DOI.

    Returns:
        The path-safe encoded DOI.
    """
    return quote(normalize_doi(doi), safe="/")
