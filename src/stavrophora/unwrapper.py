"""Crossref-specific response unwrapper implementation.

Handles the Crossref JSON response structure::

    {
        "status": "ok",
        "message-type": "work-list",
        "message-version": "1.0.0",
        "message": {
            "total-results": 186261242,
            "items-per-page": 20,
            "next-cursor": "MTAyNzU1NjE0MzAwMCwxMC4xMDY3...",
            "items": [{...}, {...}],
        },
    }

Single-item routes (``/works/{doi}``, ``/journals/{issn}``, ...) put the
entity itself in ``message``.
"""

from typing import Any

from bibliofabric.models import ResponseUnwrapper


class CrossrefUnwrapper(ResponseUnwrapper):
    """Crossref implementation of the ResponseUnwrapper protocol."""

    @staticmethod
    def _message(response_json: dict[str, Any]) -> dict[str, Any]:
        """Return the ``message`` body, tolerating list-valued error bodies."""
        message = response_json.get("message")
        return message if isinstance(message, dict) else {}

    def unwrap_results(self, response_json: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract the list of results from ``message.items``."""
        return self._message(response_json).get("items", [])

    def unwrap_single_item(self, response_json: dict[str, Any]) -> dict[str, Any]:
        """Extract a single item. Crossref GET /{route}/{id} returns it in ``message``."""
        return self._message(response_json)

    def get_next_page_token(self, response_json: dict[str, Any]) -> str | None:
        """Extract the next cursor from ``message.next-cursor``."""
        return self._message(response_json).get("next-cursor")

    def get_total_results(self, response_json: dict[str, Any]) -> int | None:
        """Extract the total count from ``message.total-results``."""
        total = self._message(response_json).get("total-results")
        if total is not None:
            return int(total)
        return None
