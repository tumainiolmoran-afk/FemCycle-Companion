from __future__ import annotations

from datetime import date, timedelta

from femcycle_companion.database import (
    create_cycle_log,
    create_user,
    create_wellness_checkin,
    get_user_by_email,
)
from femcycle_companion.security import hash_password


DEMO_USERS = [
    ("Amina Njeri", "amina.demo@femcycle.local", 22, 28),
    ("Becky Atieno", "becky.demo@femcycle.local", 24, 29),
    ("Caroline Wanjiku", "caroline.demo@femcycle.local", 27, 27),
    ("Diana Chebet", "diana.demo@femcycle.local", 21, 30),
    ("Esther Jepkoech", "esther.demo@femcycle.local", 26, 28),
    ("Faith Wairimu", "faith.demo@femcycle.local", 23, 29),
    ("Grace Achieng", "grace.demo@femcycle.local", 25, 27),
    ("Hellen Jepchirchir", "hellen.demo@femcycle.local", 28, 30),
    ("Irene Nyambura", "irene.demo@femcycle.local", 29, 28),
    ("Joy Kemunto", "joy.demo@femcycle.local", 20, 27),
]


def seed_demo_dataset() -> None:
    base_start = date(2025, 4, 1)
    moods = ["Calm", "Happy", "Tired", "Low", "Irritable"]
    flows = ["Light", "Medium", "Heavy"]
    symptom_sets = [
        ["cramps", "fatigue"],
        ["bloating", "headache"],
        ["cramps", "low appetite"],
        ["fatigue", "back pain"],
        ["breast tenderness", "mood swings"],
    ]
    feelings = [
        "Calm",
        "Emotionally drained",
        "Anxious",
        "Low",
        "Irritable",
        "Hopeful",
    ]
    care_preferences = [
        "Rest and quiet",
        "Heat therapy and hydration",
        "Talking to someone",
        "Gentle movement and food",
        "Medical advice",
    ]

    for index, (name, email, age, cycle_length) in enumerate(DEMO_USERS):
        if get_user_by_email(email):
            continue

        user_id = create_user(
            full_name=name,
            email=email,
            age=age,
            average_cycle_length=cycle_length,
            password_hash=hash_password("DemoUser@123"),
            is_demo=True,
        )

        current_start = base_start + timedelta(days=index * 2)
        for month in range(13):
            period_length = 4 + ((index + month) % 3)
            flow_level = flows[(index + month) % len(flows)]
            mood = moods[(index + month) % len(moods)]
            symptoms = symptom_sets[(index + month) % len(symptom_sets)]
            end_date = current_start + timedelta(days=period_length - 1)
            create_cycle_log(
                user_id=user_id,
                start_date=current_start.isoformat(),
                end_date=end_date.isoformat(),
                flow_level=flow_level,
                mood=mood,
                symptoms=symptoms,
                notes=f"Demo cycle record for {name} in month {month + 1}.",
            )

            for offset in (0, 2, 5):
                checkin_day = current_start + timedelta(days=offset)
                create_wellness_checkin(
                    user_id=user_id,
                    checkin_date=checkin_day.isoformat(),
                    pain_level=min(10, 3 + ((index + month + offset) % 7)),
                    energy_level=max(1, 8 - ((index + month + offset) % 6)),
                    stress_level=min(10, 2 + ((index + month + offset) % 8)),
                    sleep_hours=6.0 + ((index + month + offset) % 4) * 0.5,
                    feelings=feelings[(index + month + offset) % len(feelings)],
                    care_preference=care_preferences[(index + month + offset) % len(care_preferences)],
                    support_needed=((index + month + offset) % 4 == 0),
                    notes=f"Demo wellbeing record for {name} on {checkin_day.isoformat()}.",
                )

            current_start = current_start + timedelta(days=cycle_length)
