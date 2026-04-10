from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def build_notifications(prediction: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not prediction:
        return []

    next_period = datetime.strptime(prediction["next_period_date"], "%Y-%m-%d").date()
    fertile_start = datetime.strptime(prediction["fertile_start"], "%Y-%m-%d").date()
    ovulation = datetime.strptime(prediction["ovulation_date"], "%Y-%m-%d").date()

    return [
        {
            "title": "Upcoming period reminder",
            "body": "Your next period is approaching. Prepare supplies and monitor any early symptoms.",
            "scheduled_for": (next_period - timedelta(days=2)).isoformat(),
            "kind": "period",
        },
        {
            "title": "Fertile window starts soon",
            "body": "Your fertile window is about to begin. Check your calendar and cycle goals.",
            "scheduled_for": fertile_start.isoformat(),
            "kind": "fertility",
        },
        {
            "title": "Ovulation reminder",
            "body": "Ovulation is expected around today based on your current cycle history.",
            "scheduled_for": ovulation.isoformat(),
            "kind": "ovulation",
        },
    ]

