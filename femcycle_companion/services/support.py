from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any

from femcycle_companion.services.prediction import parse_date


def build_support_profile(
    cycle_logs: list[dict[str, Any]],
    wellness_checkins: list[dict[str, Any]],
    prediction: dict[str, Any] | None,
) -> dict[str, Any]:
    if not cycle_logs and not wellness_checkins:
        return {
            "headline": "Start with one cycle log or wellbeing check-in",
            "focus_areas": ["Build your first private support record"],
            "recommendations": [
                "Add a cycle entry and a daily check-in so the app can begin personalizing support.",
                "Use the chatbot to ask about symptoms, mood changes, or menstrual health basics.",
            ],
            "care_prompt": "Your first goal is to make the app aware of both your body patterns and your feelings.",
            "medical_flags": [],
            "wellness_snapshot": {
                "checkin_count": 0,
                "average_pain": None,
                "average_stress": None,
                "average_energy": None,
                "support_requests": 0,
            },
        }

    recent_checkins = wellness_checkins[:5]
    latest_cycle = cycle_logs[0] if cycle_logs else None
    latest_checkin = wellness_checkins[0] if wellness_checkins else None

    average_pain = round(mean([item["pain_level"] for item in recent_checkins]), 1) if recent_checkins else None
    average_stress = round(mean([item["stress_level"] for item in recent_checkins]), 1) if recent_checkins else None
    average_energy = round(mean([item["energy_level"] for item in recent_checkins]), 1) if recent_checkins else None
    support_requests = sum(1 for item in recent_checkins if item["support_needed"])

    focus_areas: list[str] = []
    recommendations: list[str] = []
    medical_flags: list[str] = []

    if average_pain is not None and average_pain >= 7:
        focus_areas.append("Physical symptom relief")
        recommendations.append("Prioritize heat therapy, hydration, rest, and gentle movement for stronger pain days.")
    elif latest_cycle and latest_cycle["symptoms"]:
        focus_areas.append("Symptom-aware care")
        recommendations.append(
            "Your recent symptom history can guide support. Keep logging cramps, fatigue, headaches, or bloating for better guidance."
        )

    if average_stress is not None and average_stress >= 6:
        focus_areas.append("Emotional support and stress care")
        recommendations.append("Try low-pressure support habits such as journaling, breathing exercises, quiet time, or reaching out to a trusted person.")

    if average_energy is not None and average_energy <= 4:
        focus_areas.append("Rest and energy recovery")
        recommendations.append("Your recent check-ins suggest low energy. Aim for lighter schedules, hydration, iron-rich meals, and more rest where possible.")

    if latest_checkin and latest_checkin["support_needed"]:
        focus_areas.append("Active support request")
        recommendations.append("You marked that you need support. Consider contacting a doctor, clinic, trusted friend, or the contact centre listed below.")

    if prediction:
        next_period = parse_date(prediction["next_period_date"])
        if 0 <= (next_period - date.today()).days <= 4:
            focus_areas.append("Prepare for the next cycle")
            recommendations.append("Your next period is close. Prepare a comfort kit, pads or tampons, pain support, and some extra rest if possible.")

    if latest_cycle and latest_cycle["mood"] in {"Low", "Irritable", "Tired"}:
        recommendations.append("Recent cycle logs suggest you may benefit from a gentle emotional check-in routine during tougher days.")

    if latest_checkin and latest_checkin["pain_level"] >= 8:
        medical_flags.append("Recent pain level is very high. If pain is severe or disruptive, seek medical advice.")

    if latest_cycle and latest_cycle["flow_level"] == "Heavy":
        medical_flags.append("Heavy flow has been logged. Monitor this closely and seek care if it becomes unusually heavy or prolonged.")

    if latest_checkin and latest_checkin["stress_level"] >= 8:
        medical_flags.append("Stress levels are high in your recent check-in. Consider reaching out for emotional support and rest.")

    if not focus_areas:
        focus_areas.append("Balanced cycle support")

    if not recommendations:
        recommendations.append("Keep combining cycle logs with emotional and physical check-ins so your support stays personal.")

    if average_pain is not None and average_stress is not None and average_pain >= 6 and average_stress >= 6:
        headline = "Your recent pattern suggests both physical discomfort and emotional strain need attention."
    elif support_requests:
        headline = "Your recent check-ins suggest you may benefit from extra support right now."
    else:
        headline = "Your support plan is being shaped by both your body patterns and your daily wellbeing."

    care_prompt = (
        "This app is prioritizing both the physical and emotional parts of menstruation so the support feels more personal."
    )

    return {
        "headline": headline,
        "focus_areas": focus_areas[:4],
        "recommendations": recommendations[:5],
        "care_prompt": care_prompt,
        "medical_flags": medical_flags[:3],
        "wellness_snapshot": {
            "checkin_count": len(wellness_checkins),
            "average_pain": average_pain,
            "average_stress": average_stress,
            "average_energy": average_energy,
            "support_requests": support_requests,
        },
    }


def build_wellbeing_prompt(wellness_checkins: list[dict[str, Any]]) -> str:
    if not wellness_checkins:
        return "How are you feeling today, physically and emotionally?"

    latest = wellness_checkins[0]
    checkin_date = parse_date(latest["checkin_date"])
    if date.today() - checkin_date >= timedelta(days=2):
        return "It has been a little while since your last wellbeing check-in. A quick update can help keep support personal."

    if latest["support_needed"]:
        return "You recently asked for support. If you still feel overwhelmed, use the doctor contacts or contact centre below."

    return "Your recent wellbeing data is helping build better support. Keep checking in when your symptoms or mood change."
