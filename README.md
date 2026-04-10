# FemCycle Companion

`FemCycle Companion` is a web-based menstrual health tracking system built in Python from your proposal, "Period Tracking App with an AI Chat Bot." This first version turns the proposal into a working prototype with browser pages instead of a mobile app.

## What Is Implemented

The system follows the five modules described in the proposal:

1. User Management
   Secure registration and login with hashed passwords and session-based authentication.
2. Period Tracking and Data Management
   Users can log cycle dates, moods, symptoms, flow level, and notes.
3. AI Chatbot Interaction
   A health-support chatbot responds with personalized guidance using the user's cycle history and predictions.
4. Notifications and Reminders
   The app generates reminders for upcoming periods, fertile windows, and self-checks.
5. Reporting and Insights
   The dashboard shows cycle summaries, symptom trends, recent logs, and prediction insights.

## Tech Stack

- Python 3.12
- FastAPI for the web server
- Jinja2 templates for the web interface
- SQLite for local data storage
- Standard-library password hashing and session handling

## Run The Project

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Start the server:

```bash
python -m uvicorn femcycle_companion.main:app --reload
```

Recommended on Windows for faster reloads:

```bash
python -m uvicorn femcycle_companion.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir femcycle_companion --reload-dir templates --reload-dir static
```

Or run the helper script:

```powershell
.\start_femcycle_companion.ps1
```

3. Open the browser:

```text
http://127.0.0.1:8000
```

## Demo And Admin Accounts

The app seeds demo data automatically on startup.

- Admin login: `admin@femcycle.local`
- Admin password: `Admin@12345`
- Demo user password: `DemoUser@123`
- Example demo user: `amina.demo@femcycle.local`

## Environment Variables

These are optional for local setup unless you want email OTP or Google-backed chatbot research:

- `FEMCYCLE_COMPANION_SECRET_KEY`
- `FEMCYCLE_COMPANION_SESSION_TIMEOUT_MINUTES`
- `FEMCYCLE_COMPANION_SMTP_HOST`
- `FEMCYCLE_COMPANION_SMTP_PORT`
- `FEMCYCLE_COMPANION_SMTP_USERNAME`
- `FEMCYCLE_COMPANION_SMTP_PASSWORD`
- `FEMCYCLE_COMPANION_SMTP_SENDER`
- `FEMCYCLE_COMPANION_GOOGLE_API_KEY`
- `FEMCYCLE_COMPANION_GOOGLE_CSE_ID`

If SMTP is not configured, password reset OTPs are written to `otp_outbox.log` for development.

## Tests

Run tests with:

```bash
python -m unittest discover -s femcycle_companion\tests -v
```

## Share On GitHub

Repository:

```text
https://github.com/tumainiolmoran-afk/FemCycle-Companion.git
```

1. Open terminal in the project folder.
2. Run:

```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tumainiolmoran-afk/FemCycle-Companion.git
git push -u origin main
```

If Git asks for your identity first, set it with:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

After pushing, the other person can download with:

```bash
git clone https://github.com/tumainiolmoran-afk/FemCycle-Companion.git
cd FemCycle-Companion
python -m pip install -r requirements.txt
python -m uvicorn femcycle_companion.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir femcycle_companion --reload-dir templates --reload-dir static
```

## Notes About The Proposal

- The original proposal describes a mobile app, but this implementation is intentionally web-based as requested.
- The chatbot is a smart prototype built around user data and health-support rules. It is structured so we can later plug in a more advanced AI model or external NLP service.
- The proposal has a few copy-paste sections referring to file management and document management. I kept the implementation aligned to the actual period tracking objectives instead.
