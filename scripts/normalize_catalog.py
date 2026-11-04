#!/usr/bin/env python3
"""Normalize provider exports into one catalog; never assumes media rights."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "catalog-policy.yml"
INPUT_DIR = ROOT / "data" / "incoming"
OUTPUT = ROOT / "dist" / "catalog.json"
REVIEW = ROOT / "dist" / "catalog-review.json"


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def key_text(value):
    text = unicodedata.normalize("NFKD", clean(value).lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def valid_https(value):
    parsed = urlparse(clean(value))
    return parsed.scheme == "https" and bool(parsed.netloc)


def load_records():
    records = []
    if not INPUT_DIR.exists():
        return records
    for path in sorted(INPUT_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            records.extend(raw)
        elif isinstance(raw, dict):
            records.extend(raw.get("items", []))
    return records


def main():
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    rules = policy["moderation"]
    seen = set()
    approved, review = [], []

    for item in load_records():
        item = dict(item)
        source = clean(item.get("source"))
        source_id = clean(item.get("source_id"))
        title = clean(item.get("title"))
        creator = clean(item.get("creator"))
        source_url = clean(item.get("source_url"))
        media_url = clean(item.get("media_url"))
        rights = clean(item.get("rights_status") or rules["default_rights_status"])
        duration = item.get("duration_seconds")
        reason = []

        if rules["require_title"] and not title:
            reason.append("missing_title")
        if rules["require_source_id"] and not source_id:
            reason.append("missing_source_id")
        if not source:
            reason.append("missing_source")
        if rules["require_source_url"] and not valid_https(source_url):
            reason.append("invalid_source_url")
        if media_url and not valid_https(media_url):
            reason.append("media_url_not_https")
        thumbnail_url = clean(item.get("thumbnail_url"))
        if thumbnail_url and not valid_https(thumbnail_url):
            reason.append("thumbnail_url_not_https")
        license_url = clean(item.get("license_url"))
        if license_url and not valid_https(license_url):
            reason.append("license_url_not_https")
        if rules["require_duration_for_video"] and item.get("media_type") == "video":
            if not isinstance(duration, (int, float)) or duration < rules["min_duration_seconds"] or duration > rules["max_duration_seconds"]:
                reason.append("invalid_video_duration")
        if rules["reject_explicit_flags"] and item.get("explicit") is True:
            reason.append("explicit_content")
        if rights not in rules["rights_status_allowed"]:
            reason.append("rights_not_verified")
        if item.get("rights_status") == "review_required":
            reason.append("rights_review_required")

        dedupe_key = (source, source_id) if source_id else (key_text(title), key_text(creator))
        if dedupe_key in seen:
            reason.append("duplicate")
        else:
            seen.add(dedupe_key)

        normalized = {
            "id": f"{source}:{source_id}" if source and source_id else None,
            "source": source,
            "source_id": source_id,
            "title": title,
            "creator": creator or None,
            "description": clean(item.get("description")) or None,
            "category": clean(item.get("category")) or "uncategorized",
            "media_type": clean(item.get("media_type")) or "unknown",
            "source_url": source_url or None,
            "media_url": media_url or None,
            "thumbnail_url": clean(item.get("thumbnail_url")) or None,
            "duration_seconds": duration,
            "license": clean(item.get("license")) or None,
            "license_url": license_url or None,
            "rights_status": rights,
            "rights_evidence": clean(item.get("rights_evidence")) or None,
            "language": clean(item.get("language")) or None,
            "explicit": bool(item.get("explicit", False)),
            "moderation_status": "approved" if not reason else "review",
            "moderation_reasons": reason
        }
        (review if reason else approved).append(normalized)

    max_items = int(policy["catalog"].get("max_items_per_source", 500))
    counts = {}
    limited = []
    for item in approved:
        source = item["source"]
        counts[source] = counts.get(source, 0) + 1
        if counts[source] <= max_items:
            limited.append(item)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"schema_version": 1, "count": len(limited), "items": limited}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text(json.dumps({"schema_version": 1, "count": len(review), "items": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Catálogo aprovado: {len(limited)} | revisão: {len(review)}")


if __name__ == "__main__":
    main()
