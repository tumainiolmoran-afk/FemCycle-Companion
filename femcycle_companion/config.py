from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    app_name: str = "FemCycle Companion"
    database_path: Path = Path(
        os.getenv("FEMCYCLE_COMPANION_DB_PATH", BASE_DIR / "femcycle_companion.db")
    )
    secret_key: str = os.getenv(
        "FEMCYCLE_COMPANION_SECRET_KEY", "change-this-secret-key-for-production"
    )
    google_search_api_key: str = os.getenv("FEMCYCLE_COMPANION_GOOGLE_API_KEY", "")
    google_search_engine_id: str = os.getenv("FEMCYCLE_COMPANION_GOOGLE_CSE_ID", "")
    session_timeout_minutes: int = int(os.getenv("FEMCYCLE_COMPANION_SESSION_TIMEOUT_MINUTES", "5"))
    smtp_host: str = os.getenv("FEMCYCLE_COMPANION_SMTP_HOST", "")
    smtp_port: int = int(os.getenv("FEMCYCLE_COMPANION_SMTP_PORT", "587"))
    smtp_username: str = os.getenv("FEMCYCLE_COMPANION_SMTP_USERNAME", "")
    smtp_password: str = os.getenv("FEMCYCLE_COMPANION_SMTP_PASSWORD", "")
    smtp_sender_email: str = os.getenv("FEMCYCLE_COMPANION_SMTP_SENDER", "no-reply@femcyclecompanion.local")
    smtp_use_tls: bool = os.getenv("FEMCYCLE_COMPANION_SMTP_USE_TLS", "true").lower() == "true"


settings = Settings()
