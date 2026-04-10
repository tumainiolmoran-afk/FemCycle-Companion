from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from femcycle_companion.config import settings


def google_search_available() -> bool:
    return bool(settings.google_search_api_key and settings.google_search_engine_id)


def search_google_context(query: str, max_results: int = 3) -> dict[str, Any]:
    if not google_search_available():
        return {
            "enabled": False,
            "results": [],
            "summary": "",
        }

    params = urlencode(
        {
            "key": settings.google_search_api_key,
            "cx": settings.google_search_engine_id,
            "q": query,
            "num": max(1, min(max_results, 5)),
        }
    )
    url = f"https://www.googleapis.com/customsearch/v1?{params}"
    request = Request(url, headers={"User-Agent": "FemCycleCompanion/1.0"})

    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return {
            "enabled": True,
            "results": [],
            "summary": "",
        }

    items = payload.get("items", [])[:max_results]
    results = [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", ""),
        }
        for item in items
    ]

    summary_parts = []
    for item in results:
        title = item["title"].strip()
        snippet = item["snippet"].strip().replace("\n", " ")
        if title or snippet:
            summary_parts.append(f"{title}: {snippet}".strip(": "))

    return {
        "enabled": True,
        "results": results,
        "summary": " ".join(summary_parts),
    }
