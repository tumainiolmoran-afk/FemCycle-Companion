from __future__ import annotations


ABOUT_CONTENT = {
    "summary": (
        "FemCycle Companion is a supportive web-based menstrual health system focused on cycle "
        "tracking, education, reminders, and access to trusted reproductive health support."
    ),
    "vision": (
        "To make menstrual and reproductive health guidance easier to access, more private, "
        "and more empowering for every user."
    ),
    "mission": (
        "To combine practical cycle tracking, compassionate digital support, and trusted "
        "health information in one accessible platform."
    ),
}


SERVICE_ITEMS = [
    {
        "slug": "cycle-tracking",
        "title": "Cycle Tracking",
        "description": "Log start dates, end dates, flow levels, moods, symptoms, and notes.",
    },
    {
        "slug": "wellbeing-checkins",
        "title": "Daily Wellbeing Check-ins",
        "description": "Track pain, stress, energy, sleep, feelings, and the kind of support you need today.",
    },
    {
        "slug": "predictions",
        "title": "Predictions",
        "description": "Estimate next period dates, ovulation timing, and fertile windows.",
    },
    {
        "slug": "personalized-care-guidance",
        "title": "Personalized Care Guidance",
        "description": "Receive care ideas and support plans based on both physical symptoms and emotional check-ins.",
    },
    {
        "slug": "chatbot-support",
        "title": "Chatbot Support",
        "description": "Ask questions about symptoms, moods, timing, self-care, and menstrual health habits.",
    },
    {
        "slug": "reminders",
        "title": "Reminders",
        "description": "See upcoming period alerts, fertile-window reminders, and wellbeing self-check prompts.",
    },
    {
        "slug": "reports",
        "title": "Reports & Insights",
        "description": "Review symptom trends, mood patterns, stress signals, and personal wellness patterns.",
    },
    {
        "slug": "health-education",
        "title": "Health Education",
        "description": "Access private, stigma-free information on menstrual health, comfort care, and when to seek help.",
    },
]


RESOURCE_LINKS = [
    {
        "label": "Kenya Ministry of Health",
        "url": "https://health.go.ke/",
        "note": "Official Ministry of Health website and public health updates.",
    },
    {
        "label": "Kenya Reproductive Health Policy",
        "url": "https://familyhealth.go.ke/wp-content/uploads/2022/07/The-National-Reproductive-Health-Policy-2022-2032.pdf",
        "note": "National reproductive health policy reference.",
    },
    {
        "label": "WHO Menstrual Health",
        "url": "https://www.who.int/news/item/22-06-2022-who-statement-on-menstrual-health-and-rights",
        "note": "Trusted global guidance on menstrual health and rights.",
    },
    {
        "label": "Marie Stopes Kenya Services",
        "url": "https://mariestopes.or.ke/services",
        "note": "Sexual and reproductive health services and clinic support.",
    },
]


DOCTOR_CONTACTS = [
    {
        "name": "Aga Khan Obstetrics & Gynaecology Clinic",
        "details": "+254 20 366 2876 | +254 711 092 876 | patient.referral@aku.edu",
        "url": "https://hospitals.aku.edu/nairobi/Departments/Pages/Maternity-and-women-services.aspx",
    },
    {
        "name": "Marie Stopes Obstetrician/Gynaecologist Services",
        "details": "Appointments and reproductive health support through official clinics.",
        "url": "https://mariestopes.or.ke/services/obstetrician-gynaecologist-services/",
    },
    {
        "name": "Aga Khan Gynaecology Consultation",
        "details": "Consultations Monday to Saturday, with specialist women’s health support.",
        "url": "https://hospitals.aku.edu/nairobi/Departments/Pages/gynaecology-consultation.aspx",
    },
]


CONTACT_CENTRE = {
    "hotline": "0800 720005",
    "whatsapp": "0709 819001",
    "hours": "Mon-Fri 7:00am-9:00pm | Weekends/Public Holidays 8:00am-9:00pm",
    "support_line": "+254-20-2717077",
    "email": "ps.medical@health.go.ke",
}


EDUCATION_LIBRARY = [
    {
        "title": "Understanding common menstrual symptoms",
        "summary": "Learn what cramps, bloating, fatigue, headaches, and mood changes can look like during the cycle.",
    },
    {
        "title": "Comfort and self-care options",
        "summary": "Simple ideas such as hydration, rest, gentle movement, warm compresses, and sleep support.",
    },
    {
        "title": "Emotional wellbeing during menstruation",
        "summary": "Explore how stress, low mood, and irritability may show up and how to build small support habits.",
    },
    {
        "title": "When to seek medical help",
        "summary": "Know warning signs such as severe pain, fainting, fever, or unusually heavy bleeding.",
    },
]


SUPPORT_PROMISE = {
    "title": "Private and supportive by design",
    "message": (
        "FemCycle Companion is built to address more than dates and reminders. It helps users record "
        "physical symptoms, emotional experiences, support needs, and menstrual health questions in one private place."
    ),
}


CHATBOT_GUIDES = [
    {
        "title": "Cycle and period timing",
        "keywords": ["period", "late", "cycle", "timing", "ovulation", "fertile", "next period"],
        "answer": (
            "The chatbot can explain period timing, fertile windows, and ovulation in simple language. "
            "If you have saved cycle logs, it also uses your own history to personalize the answer."
        ),
    },
    {
        "title": "Symptoms and comfort care",
        "keywords": ["cramps", "pain", "bloating", "fatigue", "headache", "symptom", "comfort"],
        "answer": (
            "For common menstrual symptoms, helpful support may include hydration, rest, a warm compress, "
            "light movement, regular meals, and sleep. Severe pain, fainting, fever, or very heavy bleeding should be checked by a clinician."
        ),
    },
    {
        "title": "Mood and emotional wellbeing",
        "keywords": ["mood", "sad", "anxious", "stress", "emotional", "irritable", "overwhelmed"],
        "answer": (
            "Menstrual experiences are not only physical. Mood changes, stress, emotional exhaustion, and irritability matter too. "
            "The chatbot supports emotional check-ins, gentle self-care ideas, and guidance on when extra support may be helpful."
        ),
    },
    {
        "title": "Menstrual hygiene and products",
        "keywords": ["pad", "tampon", "cup", "hygiene", "clean", "products", "sanitary"],
        "answer": (
            "Good menstrual hygiene includes changing products regularly, washing hands before and after product changes, "
            "keeping the body comfortable and clean, and choosing products that fit your flow and comfort level."
        ),
    },
    {
        "title": "Food, hydration, and energy",
        "keywords": ["food", "nutrition", "eat", "iron", "energy", "hydration", "water"],
        "answer": (
            "Low energy can feel worse during menstruation. Hydration, balanced meals, iron-rich foods, and enough rest can help. "
            "The app also lets users track low-energy days through wellbeing check-ins."
        ),
    },
    {
        "title": "Irregular cycles and warning signs",
        "keywords": ["irregular", "heavy", "warning", "danger", "doctor", "help", "abnormal"],
        "answer": (
            "Irregular cycles can happen for different reasons, but severe pain, very heavy bleeding, fainting, fever, "
            "or symptoms that disrupt daily life are signs to seek medical advice. FemCycle Companion offers support but does not replace professional care."
        ),
    },
    {
        "title": "Privacy and stigma-free support",
        "keywords": ["private", "privacy", "secret", "safe", "stigma", "confidential"],
        "answer": (
            "FemCycle Companion is designed as a private support space where users can track physical symptoms, emotional experiences, "
            "and menstrual questions without judgment. This directly responds to the proposal’s concern about menstrual health being a sensitive topic."
        ),
    },
    {
        "title": "Using FemCycle Companion features",
        "keywords": ["how to use", "dashboard", "check-in", "chatbot", "reminder", "feature", "app"],
        "answer": (
            "The platform works best when users combine cycle logging, wellbeing check-ins, reminders, education content, "
            "and chatbot questions. That gives more personalized support than a simple calendar-only tracker."
        ),
    },
]


CHATBOT_STARTERS = [
    "Why am I feeling emotionally drained during my period?",
    "What can help with cramps and low energy today?",
    "When should I worry about heavy bleeding?",
    "How do I track my symptoms and moods better?",
    "What does FemCycle Companion do beyond period reminders?",
    "How can I manage stress during my cycle?",
]
