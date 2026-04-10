from __future__ import annotations

from datetime import date, datetime, timedelta
from statistics import mean, pstdev
from typing import Any


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def iso(value: date) -> str:
    return value.isoformat()


def build_prediction(
    cycle_logs: list[dict[str, Any]],
    preferred_cycle_length: int = 28,
) -> dict[str, Any] | None:
    if not cycle_logs:
        return None

    ordered_logs = sorted(cycle_logs, key=lambda item: item["start_date"])
    start_dates = [parse_date(item["start_date"]) for item in ordered_logs]
    period_lengths = [
        max(1, (parse_date(item["end_date"]) - parse_date(item["start_date"])).days + 1)
        for item in ordered_logs
    ]

    if len(start_dates) >= 2:
        cycle_lengths = [
            (current - previous).days
            for previous, current in zip(start_dates, start_dates[1:])
        ]
        average_cycle = round(mean(cycle_lengths))
        variability_days = round(pstdev(cycle_lengths)) if len(cycle_lengths) > 1 else 0
    else:
        cycle_lengths = []
        average_cycle = preferred_cycle_length
        variability_days = 0

    average_cycle = max(21, min(35, average_cycle))
    average_period = max(3, min(8, round(mean(period_lengths))))

    last_start = start_dates[-1]
    next_period = last_start + timedelta(days=average_cycle)
    ovulation = next_period - timedelta(days=14)
    fertile_start = ovulation - timedelta(days=5)
    fertile_end = ovulation + timedelta(days=1)

    confidence = min(0.95, 0.45 + (0.1 * len(cycle_lengths)))

    return {
        "next_period_date": iso(next_period),
        "ovulation_date": iso(ovulation),
        "fertile_start": iso(fertile_start),
        "fertile_end": iso(fertile_end),
        "cycle_length": average_cycle,
        "period_length": average_period,
        "confidence": round(confidence, 2),
        "variability_days": variability_days,
    }

