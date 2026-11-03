#!/usr/bin/env python3
"""Build a deterministic 7-day broadcast schedule from YAML templates."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "programming.yml"
OUTPUT = ROOT / "dist" / "schedule.json"

DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_clock(value: str) -> time:
    hour, minute = (int(part) for part in value.split(":"))
    if hour == 24 and minute == 0:
        return time(0, 0)
    return time(hour, minute)


def minutes(value: str) -> int:
    hour, minute = (int(part) for part in value.split(":"))
    return hour * 60 + minute


def choose_template(day: date, templates: dict) -> str:
    name = DAY_NAMES[day.weekday()]
    if name == "saturday":
        return "saturday"
    if name == "sunday":
        return "sunday"
    return "weekdays"


def build_day(day: date, template_name: str, slots: list[dict], tz: ZoneInfo) -> list[dict]:
    output = []
    previous_end = 0
    for index, slot in enumerate(slots):
        start_min = minutes(slot["start"])
        end_min = minutes(slot["end"])
        if end_min == 1440:
            pass
        if start_min != previous_end:
            raise ValueError(
                f"Grade {template_name}, {day}: lacuna/sobreposição antes de {slot['start']}"
            )
        if end_min <= start_min:
            raise ValueError(f"Intervalo inválido em {template_name}: {slot}")
        start_dt = datetime.combine(day, parse_clock(slot["start"]), tzinfo=tz)
        if slot["end"] == "24:00":
            end_dt = datetime.combine(day + timedelta(days=1), time(0, 0), tzinfo=tz)
        else:
            end_dt = datetime.combine(day, parse_clock(slot["end"]), tzinfo=tz)
        output.append({
            "id": f"{day.isoformat()}-{index + 1:02d}",
            "date": day.isoformat(),
            "day_template": template_name,
            "program_id": slot["program_id"],
            "title": slot["title"],
            "category": slot["category"],
            "selector": slot["selector"],
            "start_local": start_dt.isoformat(),
            "end_local": end_dt.isoformat(),
            "start_utc": start_dt.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z"),
            "end_utc": end_dt.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z"),
            "timezone": str(tz),
            "playback_mode": "continuous",
            "content_ids": []
        })
        previous_end = end_min
    if previous_end != 1440:
        raise ValueError(f"Grade {template_name}, {day}: termina em {previous_end}, deveria terminar em 1440")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", help="Data inicial YYYY-MM-DD; padrão: hoje em São Paulo")
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    tz = ZoneInfo(config.get("timezone", "America/Sao_Paulo"))
    start = date.fromisoformat(args.start_date) if args.start_date else datetime.now(tz).date()
    horizon = args.days or int(config.get("horizon_days", 7))
    if horizon < 1 or horizon > 31:
        raise ValueError("--days precisa estar entre 1 e 31")

    schedule = []
    for offset in range(horizon):
        day = start + timedelta(days=offset)
        template_name = choose_template(day, config["templates"])
        schedule.extend(build_day(day, template_name, config["templates"][template_name], tz))

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z"),
        "timezone": str(tz),
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=horizon - 1)).isoformat(),
        "days": horizon,
        "entries": schedule
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Grade gerada: {len(schedule)} blocos / {horizon} dias -> {output}")


if __name__ == "__main__":
    main()
