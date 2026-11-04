#!/usr/bin/env python3
"""Guarded NASA NAIL collector.

Network access is opt-in and always reserves the central rate-limit budget first.
No direct provider call is made if the gate is missing, disabled, or rejects.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from nasa import map_nasa_response

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "incoming" / "nasa_nail.json"
NASA_SEARCH_URL = "https://images-api.nasa.gov/search"


class CollectionBlocked(RuntimeError):
    pass


def reserve_rate_limit() -> None:
    base_url = os.environ.get("TVBRASIL_RATE_LIMIT_URL", "").strip().rstrip("/")
    token = os.environ.get("RATE_LIMIT_ADMIN_TOKEN", "").strip()
    if not base_url or not token:
        raise CollectionBlocked("Rate-limit endpoint/token missing; NASA request blocked.")

    payload = json.dumps({"source": "nasa-image-library"}).encode("utf-8")
    request = Request(
        base_url + "/api/rate-limit/consume",
        data=payload,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            body = json.loads(response.read().decode("utf-8"))
            if response.status != 200 or body.get("ok") is not True:
                raise CollectionBlocked("Central rate limiter did not authorize NASA request.")
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise CollectionBlocked("Central rate limiter unavailable; NASA request blocked.") from exc


def fetch_nasa_page(query: str, page_size: int) -> dict:
    params = urlencode({"q": query, "media_type": "image,video", "page_size": page_size})
    request = Request(
        NASA_SEARCH_URL + "?" + params,
        headers={"User-Agent": "TV-BRASIL-PLAY metadata collector"},
    )
    try:
        with urlopen(request, timeout=25) as response:
            if response.status != 200:
                raise CollectionBlocked("NASA NAIL returned a non-success status.")
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise CollectionBlocked("NASA NAIL request failed; no fallback request will be made.") from exc


def collect(query: str, page_size: int) -> int:
    # Reserve immediately before each provider request. Never bypass this call.
    reserve_rate_limit()
    response = fetch_nasa_page(query, page_size)
    records = map_nasa_response(response)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps({"source": "nasa_nail", "items": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-network", action="store_true",
                        help="Explicitly permit a live request after central rate-limit approval.")
    parser.add_argument("--query", default=os.environ.get("NASA_NAIL_QUERY", "earth"))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("NASA_NAIL_PAGE_SIZE", "10")))
    args = parser.parse_args(argv)

    if not args.allow_network:
        print("BLOCKED: live collection is disabled. Use --allow-network only after quota protection is configured.")
        return 2
    if not 1 <= args.page_size <= 100:
        print("ERROR: --page-size must be between 1 and 100.")
        return 2

    try:
        count = collect(args.query, args.page_size)
    except CollectionBlocked as exc:
        print(f"BLOCKED: {exc}")
        return 3

    print(f"NASA NAIL metadata collected: {count}; all records remain subject to rights review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
