#!/usr/bin/env python3
"""Pure NASA Image and Video Library response mapper.

This module does not make network requests and never grants publication rights.
It converts one NASA NAIL API item into the TV-BRASIL-PLAY incoming schema.
All records remain review_required until item-specific rights are verified.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _first_link_preview(links: list[dict[str, Any]]) -> str | None:
    for link in links:
        if link.get("rel") == "preview" and str(link.get("href", "")).startswith("https://"):
            return str(link["href"])
    return None


def map_nasa_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """Map a NASA NAIL collection item; return None when its ID/title is absent."""
    data = item.get("data") or []
    metadata = data[0] if data and isinstance(data[0], dict) else {}
    nasa_id = _text(metadata.get("nasa_id"))
    title = _text(metadata.get("title"))
    if not nasa_id or not title:
        return None

    media_type = _text(metadata.get("media_type")).lower()
    if media_type not in {"image", "video", "audio"}:
        media_type = "unknown"

    creator = _text(metadata.get("photographer") or metadata.get("secondary_creator")) or None
    description = _text(metadata.get("description")) or None
    source_url = f"https://images.nasa.gov/details/{nasa_id}"
    preview = _first_link_preview(item.get("links") or [])

    return {
        "source": "nasa_nail",
        "source_id": nasa_id,
        "title": title,
        "creator": creator,
        "description": description,
        "category": "espaco_ciencia",
        "media_type": media_type,
        "source_url": source_url,
        "media_url": None,
        "thumbnail_url": preview,
        "duration_seconds": None,
        "license": None,
        "license_url": None,
        "rights_status": "review_required",
        "rights_evidence": (
            "NASA NAIL metadata only. Verify item-specific copyright, third-party "
            "credits, logos, privacy/publicity restrictions and reuse terms before publication."
        ),
        "language": "en",
        "explicit": False,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def map_nasa_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Map the 'collection.items' array from a NASA NAIL search response."""
    collection = response.get("collection") or {}
    items = collection.get("items") or []
    mapped = []
    for item in items:
        if isinstance(item, dict):
            record = map_nasa_item(item)
            if record:
                mapped.append(record)
    return mapped
