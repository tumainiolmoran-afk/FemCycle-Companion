from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Any

from femcycle_companion.config import settings


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def column_exists(connection: sqlite3.Connection, table: str, column: str) -> bool:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def init_db() -> None:
    with closing(get_connection()) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL,
                average_cycle_length INTEGER NOT NULL DEFAULT 28,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cycle_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                flow_level TEXT NOT NULL,
                mood TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                next_period_date TEXT NOT NULL,
                ovulation_date TEXT NOT NULL,
                fertile_start TEXT NOT NULL,
                fertile_end TEXT NOT NULL,
                cycle_length INTEGER NOT NULL,
                period_length INTEGER NOT NULL,
                confidence REAL NOT NULL,
                variability_days INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS chatbot_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                intent TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                scheduled_for TEXT NOT NULL,
                kind TEXT NOT NULL,
                delivered INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS wellness_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                checkin_date TEXT NOT NULL,
                pain_level INTEGER NOT NULL,
                energy_level INTEGER NOT NULL,
                stress_level INTEGER NOT NULL,
                sleep_hours REAL NOT NULL,
                feelings TEXT NOT NULL,
                care_preference TEXT NOT NULL,
                support_needed INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS password_reset_otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                otp_code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (admin_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )

        if not column_exists(connection, "users", "is_superuser"):
            connection.execute(
                "ALTER TABLE users ADD COLUMN is_superuser INTEGER NOT NULL DEFAULT 0"
            )

        if not column_exists(connection, "users", "is_demo"):
            connection.execute(
                "ALTER TABLE users ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0"
            )

        connection.commit()


def create_user(
    *,
    full_name: str,
    email: str,
    age: int,
    average_cycle_length: int,
    password_hash: str,
    is_superuser: bool = False,
    is_demo: bool = False,
) -> int:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (full_name, email, age, average_cycle_length, password_hash, created_at, is_superuser, is_demo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                email.lower().strip(),
                age,
                average_cycle_length,
                password_hash,
                utc_now(),
                1 if is_superuser else 0,
                1 if is_demo else 0,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),),
        ).fetchone()
        return row_to_dict(row)


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return row_to_dict(row)


def update_user_password(user_id: int, password_hash: str) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )
        connection.commit()


def update_user_account(
    *,
    user_id: int,
    full_name: str,
    email: str,
    age: int,
    average_cycle_length: int,
) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            UPDATE users
            SET full_name = ?, email = ?, age = ?, average_cycle_length = ?
            WHERE id = ?
            """,
            (
                full_name.strip(),
                email.lower().strip(),
                age,
                average_cycle_length,
                user_id,
            ),
        )
        connection.commit()


def list_users(limit: int = 100) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT id, full_name, email, age, average_cycle_length, created_at, is_superuser, is_demo
            FROM users
            ORDER BY id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def count_users() -> int:
    with closing(get_connection()) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM users").fetchone()
        return int(row["total"])


def create_cycle_log(
    *,
    user_id: int,
    start_date: str,
    end_date: str,
    flow_level: str,
    mood: str,
    symptoms: list[str],
    notes: str,
) -> int:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO cycle_logs (user_id, start_date, end_date, flow_level, mood, symptoms, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                start_date,
                end_date,
                flow_level,
                mood,
                json.dumps(symptoms),
                notes,
                utc_now(),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_cycle_logs(user_id: int) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM cycle_logs
            WHERE user_id = ?
            ORDER BY start_date DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
        items = [row_to_dict(row) for row in rows]
        for item in items:
            item["symptoms"] = json.loads(item["symptoms"])
        return items


def save_prediction(user_id: int, prediction: dict[str, Any]) -> None:
    with closing(get_connection()) as connection:
        connection.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        connection.execute(
            """
            INSERT INTO predictions (
                user_id, next_period_date, ovulation_date, fertile_start, fertile_end,
                cycle_length, period_length, confidence, variability_days, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                prediction["next_period_date"],
                prediction["ovulation_date"],
                prediction["fertile_start"],
                prediction["fertile_end"],
                prediction["cycle_length"],
                prediction["period_length"],
                prediction["confidence"],
                prediction["variability_days"],
                utc_now(),
            ),
        )
        connection.commit()


def get_latest_prediction(user_id: int) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT * FROM predictions
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        return row_to_dict(row)


def replace_notifications(user_id: int, notifications: list[dict[str, Any]]) -> None:
    with closing(get_connection()) as connection:
        connection.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
        connection.executemany(
            """
            INSERT INTO notifications (user_id, title, body, scheduled_for, kind, delivered, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            [
                (
                    user_id,
                    item["title"],
                    item["body"],
                    item["scheduled_for"],
                    item["kind"],
                    utc_now(),
                )
                for item in notifications
            ],
        )
        connection.commit()


def list_notifications(user_id: int, limit: int = 6) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY scheduled_for ASC, id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def create_wellness_checkin(
    *,
    user_id: int,
    checkin_date: str,
    pain_level: int,
    energy_level: int,
    stress_level: int,
    sleep_hours: float,
    feelings: str,
    care_preference: str,
    support_needed: bool,
    notes: str,
) -> int:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO wellness_checkins (
                user_id, checkin_date, pain_level, energy_level, stress_level, sleep_hours,
                feelings, care_preference, support_needed, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                checkin_date,
                pain_level,
                energy_level,
                stress_level,
                sleep_hours,
                feelings,
                care_preference,
                1 if support_needed else 0,
                notes,
                utc_now(),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_wellness_checkins(user_id: int, limit: int = 8) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM wellness_checkins
            WHERE user_id = ?
            ORDER BY checkin_date DESC, id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        items = [row_to_dict(row) for row in rows]
        for item in items:
            item["support_needed"] = bool(item["support_needed"])
        return items


def create_chatbot_log(user_id: int, message: str, response: str, intent: str) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO chatbot_logs (user_id, message, response, intent, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, message, response, intent, utc_now()),
        )
        connection.commit()


def list_chatbot_logs(user_id: int, limit: int = 8) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM chatbot_logs
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def create_password_reset_otp(user_id: int, otp_code: str, expires_at: str) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            "UPDATE password_reset_otps SET used = 1 WHERE user_id = ? AND used = 0",
            (user_id,),
        )
        connection.execute(
            """
            INSERT INTO password_reset_otps (user_id, otp_code, expires_at, used, created_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (user_id, otp_code, expires_at, utc_now()),
        )
        connection.commit()


def get_valid_password_reset_otp(user_id: int, otp_code: str) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT * FROM password_reset_otps
            WHERE user_id = ? AND otp_code = ? AND used = 0
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id, otp_code),
        ).fetchone()
        return row_to_dict(row)


def mark_password_reset_otp_used(otp_id: int) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            "UPDATE password_reset_otps SET used = 1 WHERE id = ?",
            (otp_id,),
        )
        connection.commit()


def count_cycle_logs() -> int:
    with closing(get_connection()) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM cycle_logs").fetchone()
        return int(row["total"])


def count_wellness_checkins() -> int:
    with closing(get_connection()) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM wellness_checkins").fetchone()
        return int(row["total"])


def count_chat_messages() -> int:
    with closing(get_connection()) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM chatbot_logs").fetchone()
        return int(row["total"])


def create_support_message(
    *,
    admin_user_id: int,
    target_user_id: int,
    subject: str,
    message: str,
) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO support_messages (admin_user_id, target_user_id, subject, message, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (admin_user_id, target_user_id, subject.strip(), message.strip(), utc_now()),
        )
        connection.commit()


def list_support_messages_for_user(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT sm.*, u.full_name AS admin_name
            FROM support_messages sm
            JOIN users u ON sm.admin_user_id = u.id
            WHERE sm.target_user_id = ?
            ORDER BY sm.created_at DESC, sm.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def list_support_messages(limit: int = 50) -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT sm.*, admin.full_name AS admin_name, target.full_name AS target_name, target.email AS target_email
            FROM support_messages sm
            JOIN users admin ON sm.admin_user_id = admin.id
            JOIN users target ON sm.target_user_id = target.id
            ORDER BY sm.created_at DESC, sm.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]
