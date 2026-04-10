from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from femcycle_companion.services.prediction import parse_date


def build_dashboard_report(
    cycle_logs: list[dict[str, Any]],
    prediction: dict[str, Any] | None,
) -> dict[str, Any]:
    if not cycle_logs:
        return {
            "total_logs": 0,
            "average_cycle_length": None,
            "top_symptoms": [],
            "latest_mood": None,
            "prediction_confidence": None,
        }

    ordered_logs = sorted(cycle_logs, key=lambda item: item["start_date"])
    cycle_lengths = []
    for previous, current in zip(ordered_logs, ordered_logs[1:]):
        cycle_lengths.append(
            (parse_date(current["start_date"]) - parse_date(previous["start_date"])).days
        )

    symptom_counter = Counter()
    for item in cycle_logs:
        symptom_counter.update([symptom.strip() for symptom in item["symptoms"] if symptom.strip()])

    return {
        "total_logs": len(cycle_logs),
        "average_cycle_length": round(mean(cycle_lengths)) if cycle_lengths else None,
        "top_symptoms": symptom_counter.most_common(3),
        "latest_mood": cycle_logs[0]["mood"],
        "prediction_confidence": prediction["confidence"] if prediction else None,
    }
