from __future__ import annotations

from typing import Any

from femcycle_companion.content import CHATBOT_GUIDES


def detect_intent(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ("next period", "late", "due", "ovulation", "fertile", "cycle")):
        return "prediction_support"
    if any(word in lowered for word in ("cramp", "pain", "headache", "bloating", "fatigue", "symptom")):
        return "symptom_support"
    if any(word in lowered for word in ("sad", "angry", "mood", "stressed", "emotional", "anxious", "overwhelmed")):
        return "emotional_support"
    if any(word in lowered for word in ("tips", "hygiene", "health", "learn", "education", "product", "pad", "cup")):
        return "health_education"
    if any(word in lowered for word in ("private", "privacy", "safe", "confidential", "stigma")):
        return "privacy_support"
    if any(word in lowered for word in ("how to use", "feature", "dashboard", "check-in", "reminder", "chatbot")):
        return "app_guidance"
    return "general_support"


def knowledge_matches(message: str) -> list[dict[str, str]]:
    lowered = message.lower()
    matches: list[dict[str, str]] = []
    for item in CHATBOT_GUIDES:
        if any(keyword in lowered for keyword in item["keywords"]):
            matches.append(item)
    return matches


def build_context_summary(
    prediction: dict[str, Any] | None,
    latest_cycle: dict[str, Any] | None,
    latest_checkin: dict[str, Any] | None,
    support_profile: dict[str, Any] | None,
) -> str:
    parts: list[str] = []

    if prediction:
        parts.append(
            f"From your logs, the next predicted period is {prediction['next_period_date']} and ovulation is near {prediction['ovulation_date']}."
        )

    if latest_cycle:
        symptoms = ", ".join(latest_cycle["symptoms"]) if latest_cycle.get("symptoms") else "no symptoms recorded"
        parts.append(
            f"Your latest cycle record shows {latest_cycle['flow_level'].lower()} flow, mood {latest_cycle['mood'].lower()}, and {symptoms}."
        )

    if latest_checkin:
        parts.append(
            f"Your latest wellbeing check-in shows pain {latest_checkin['pain_level']}/10, stress {latest_checkin['stress_level']}/10, energy {latest_checkin['energy_level']}/10, and feeling {latest_checkin['feelings'].lower()}."
        )

    if support_profile and support_profile.get("focus_areas"):
        parts.append(
            "Your current support plan is focused on "
            + ", ".join(area.lower() for area in support_profile["focus_areas"][:2])
            + "."
        )

    return " ".join(parts)


def generate_response(
    *,
    message: str,
    prediction: dict[str, Any] | None,
    latest_cycle: dict[str, Any] | None,
    latest_checkin: dict[str, Any] | None = None,
    support_profile: dict[str, Any] | None = None,
    web_research: dict[str, Any] | None = None,
) -> tuple[str, str]:
    intent = detect_intent(message)
    lowered = message.lower()
    context_summary = build_context_summary(prediction, latest_cycle, latest_checkin, support_profile)
    research_summary = (web_research or {}).get("summary", "").strip()
    research_results = (web_research or {}).get("results", [])
    research_unavailable = web_research is not None and not (web_research or {}).get("enabled", False)

    def finalize(answer: str) -> str:
        if research_unavailable:
            answer += "\n\nYou asked for web research, but Google search is not configured yet in this deployment. The answer above is based on the chatbot's built-in menstrual health knowledge and your own logged data."
        return answer

    urgent_flags = ("fainting", "very heavy bleeding", "severe pain", "fever")
    if any(flag in lowered for flag in urgent_flags):
        return (
            "medical_caution",
            finalize("That sounds serious.\n\nPlease seek help from a licensed healthcare professional as soon as possible, especially if the pain is severe, bleeding is unusually heavy, or you feel faint. FemCycle Companion can support you with information, but symptoms like those need medical attention rather than self-care alone."),
        )

    if intent == "prediction_support" and prediction:
        return (
            intent,
            finalize(
                (
                f"Based on your recent logs, your next period is expected around {prediction['next_period_date']}. "
                f"Your fertile window is {prediction['fertile_start']} to {prediction['fertile_end']}, with ovulation near {prediction['ovulation_date']}.\n\n"
                "What makes this more useful than a basic tracker is that FemCycle Companion can combine timing with your symptoms, energy, stress, and emotional check-ins. "
                "That means future answers can become more personal, not just more calendar-based.\n\n"
                "A good next step is to keep logging both cycle dates and daily wellbeing so the predictions and support stay connected."
                )
            ),
        )

    if intent == "symptom_support":
        answer = (
            "For common menstrual symptoms, a helpful starting plan is hydration, rest, a warm compress, gentle movement, regular meals, and consistent sleep.\n\n"
            "It also helps to notice whether the symptom is staying the same, getting worse, or showing up together with emotional strain such as stress or low mood. "
            "That is one of the key goals of this project: to support the broader menstrual experience, not only period dates.\n\n"
        )
        if context_summary:
            answer += context_summary + "\n\n"
        answer += (
            "If symptoms become severe, unusually intense, or disruptive to daily life, please contact a healthcare professional."
        )
        if research_summary:
            answer += "\n\nI also reviewed web research and the strongest themes were: " + research_summary
        return (intent, finalize(answer))

    if intent == "emotional_support":
        answer = (
            "Mood changes can happen around the menstrual cycle, and they deserve attention just as much as physical symptoms do.\n\n"
            "Try low-pressure support first: rest, food, hydration, slower routines, journaling, gentle movement, and reaching out to someone you trust if you need emotional grounding. "
            "FemCycle Companion is designed to treat emotional wellbeing as part of menstrual health, not something separate.\n\n"
        )
        if context_summary:
            answer += context_summary + "\n\n"
        answer += "Keep using wellbeing check-ins so the app can notice patterns in both body symptoms and emotional strain over time."
        if research_summary:
            answer += "\n\nI also reviewed web research and found related guidance pointing toward: " + research_summary
        return (intent, finalize(answer))

    if intent == "privacy_support":
        return (
            intent,
            finalize(
                "FemCycle Companion is meant to be a stigma-free support space.\n\n"
            "It is designed to help users privately track physical symptoms, moods, stress, and support needs instead of focusing only on dates and reminders. "
            "That directly answers the project problem statement, which points out that many people feel uncomfortable discussing menstrual health openly and still need accurate, personalized help."
            ),
        )

    if intent == "app_guidance":
        return (
            intent,
            finalize(
                "FemCycle Companion works best when you use all the connected features together: cycle logs, wellbeing check-ins, chatbot questions, reminders, and health education.\n\n"
            "That combination is what makes the support more personal than a basic tracker. Instead of only telling you when a period may start, the system can begin to understand what your body and emotions are going through around that time.",
            )
        )

    matches = knowledge_matches(message)
    if matches:
        selected = matches[:2]
        answer = " ".join(item["answer"] for item in selected)
        if context_summary:
            answer += "\n\n" + context_summary
        if research_summary:
            answer += "\n\nI also reviewed web research and pulled these useful themes into the answer: " + research_summary
        if research_results:
            answer += "\n\nThis response was strengthened with external search results that were summarized and blended with the app's own menstrual support knowledge."
        return ("knowledge_support", finalize(answer))

    if intent == "health_education":
        return (
            intent,
            finalize(
                "A strong menstrual health habit is to log your start date, end date, symptoms, mood, stress, and energy.\n\n"
            "That gives the system enough context to provide practical and emotional support, not just timing predictions. "
            "Good menstrual education also includes hygiene, comfort care, recognizing warning signs, understanding emotional shifts, and knowing when to seek clinical care."
            ),
        )

    if prediction or latest_cycle or latest_checkin:
        return (
            intent,
            finalize(
                "I can help with cycle timing, cramps, heavy flow, low energy, stress, emotional wellbeing, hygiene, comfort care, warning signs, and how to use FemCycle Companion better.\n\n"
            + context_summary
            + (
                "\n\nI can also blend in web research when that feature is enabled and configured."
                if web_research is not None
                else ""
                )
            ),
        )

    return (
        intent,
        finalize(
            "I can answer questions about periods, symptoms, moods, hygiene, fertility timing, comfort care, and when to seek help.\n\n"
            "For the best results, add cycle logs and wellbeing check-ins so I can personalize the support instead of giving only general information."
        ),
    )
