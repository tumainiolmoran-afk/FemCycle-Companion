import unittest

from femcycle_companion.services.chatbot import generate_response
from femcycle_companion.services.prediction import build_prediction
from femcycle_companion.services.reporting import build_dashboard_report
from femcycle_companion.services.support import build_support_profile


class ServiceTests(unittest.TestCase):
    def test_prediction_uses_cycle_history(self):
        logs = [
            {
                "start_date": "2026-01-01",
                "end_date": "2026-01-05",
                "mood": "Calm",
                "flow_level": "Medium",
                "symptoms": ["cramps"],
            },
            {
                "start_date": "2026-01-29",
                "end_date": "2026-02-02",
                "mood": "Tired",
                "flow_level": "Heavy",
                "symptoms": ["bloating"],
            },
            {
                "start_date": "2026-02-26",
                "end_date": "2026-03-02",
                "mood": "Happy",
                "flow_level": "Light",
                "symptoms": ["headache"],
            },
        ]
        prediction = build_prediction(logs, 28)
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction["next_period_date"], "2026-03-26")
        self.assertEqual(prediction["cycle_length"], 28)

    def test_chatbot_prediction_response(self):
        intent, response = generate_response(
            message="When is my next period due?",
            prediction={
                "next_period_date": "2026-03-26",
                "fertile_start": "2026-03-07",
                "fertile_end": "2026-03-13",
                "ovulation_date": "2026-03-12",
            },
            latest_cycle=None,
        )
        self.assertEqual(intent, "prediction_support")
        self.assertIn("2026-03-26", response)

    def test_chatbot_knowledge_support(self):
        intent, response = generate_response(
            message="How do I manage stress and privacy during my cycle?",
            prediction=None,
            latest_cycle=None,
            latest_checkin=None,
            support_profile=None,
        )
        self.assertIn(intent, {"knowledge_support", "privacy_support", "emotional_support"})
        self.assertTrue("private" in response.lower() or "stress" in response.lower())

    def test_reporting_counts_top_symptoms(self):
        logs = [
            {
                "start_date": "2026-03-01",
                "end_date": "2026-03-05",
                "mood": "Calm",
                "flow_level": "Medium",
                "symptoms": ["cramps", "fatigue"],
            },
            {
                "start_date": "2026-02-01",
                "end_date": "2026-02-05",
                "mood": "Low",
                "flow_level": "Heavy",
                "symptoms": ["cramps"],
            },
        ]
        report = build_dashboard_report(logs, {"confidence": 0.8})
        self.assertEqual(report["total_logs"], 2)
        self.assertEqual(report["top_symptoms"][0][0], "cramps")

    def test_support_profile_prioritizes_physical_and_emotional_needs(self):
        logs = [
            {
                "start_date": "2026-03-01",
                "end_date": "2026-03-05",
                "mood": "Low",
                "flow_level": "Heavy",
                "symptoms": ["cramps", "fatigue"],
            }
        ]
        checkins = [
            {
                "checkin_date": "2026-03-04",
                "pain_level": 8,
                "energy_level": 3,
                "stress_level": 8,
                "support_needed": True,
                "feelings": "Emotionally drained",
                "care_preference": "Talk to someone",
            }
        ]
        profile = build_support_profile(logs, checkins, None)
        self.assertIn("Physical symptom relief", profile["focus_areas"])
        self.assertIn("Emotional support and stress care", profile["focus_areas"])
        self.assertGreaterEqual(len(profile["medical_flags"]), 1)


if __name__ == "__main__":
    unittest.main()
