from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from femcycle_companion.config import settings
from femcycle_companion.content import (
    ABOUT_CONTENT,
    CHATBOT_GUIDES,
    CHATBOT_STARTERS,
    CONTACT_CENTRE,
    DOCTOR_CONTACTS,
    EDUCATION_LIBRARY,
    RESOURCE_LINKS,
    SERVICE_ITEMS,
    SUPPORT_PROMISE,
)
from femcycle_companion.database import (
    count_chat_messages,
    count_cycle_logs,
    count_users,
    count_wellness_checkins,
    create_support_message,
    create_chatbot_log,
    create_cycle_log,
    create_password_reset_otp,
    create_user,
    create_wellness_checkin,
    get_latest_prediction,
    get_valid_password_reset_otp,
    get_user_by_email,
    get_user_by_id,
    init_db,
    list_chatbot_logs,
    list_cycle_logs,
    list_notifications,
    list_support_messages,
    list_support_messages_for_user,
    list_users,
    list_wellness_checkins,
    mark_password_reset_otp_used,
    replace_notifications,
    save_prediction,
    update_user_account,
    update_user_password,
)
from femcycle_companion.security import hash_password, verify_password
from femcycle_companion.services.chatbot import generate_response
from femcycle_companion.services.emailer import send_otp_email
from femcycle_companion.services.notifications import build_notifications
from femcycle_companion.services.prediction import build_prediction
from femcycle_companion.services.reporting import build_dashboard_report
from femcycle_companion.services.seed_demo import seed_demo_dataset
from femcycle_companion.services.support import build_support_profile, build_wellbeing_prompt
from femcycle_companion.services.web_research import google_search_available, search_google_context


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
init_db()


def ensure_superuser() -> None:
    admin_email = "admin@femcycle.local"
    if get_user_by_email(admin_email):
        return
    create_user(
        full_name="FemCycle Administrator",
        email=admin_email,
        age=30,
        average_cycle_length=28,
        password_hash=hash_password("Admin@12345"),
        is_superuser=True,
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    ensure_superuser()
    seed_demo_dataset()


def current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    last_seen = request.session.get("last_seen_at")
    if last_seen:
        last_seen_dt = datetime.fromisoformat(last_seen)
        if datetime.utcnow() - last_seen_dt > timedelta(minutes=settings.session_timeout_minutes):
            request.session.clear()
            request.session["flash"] = {
                "message": f"Your session expired after {settings.session_timeout_minutes} minutes of inactivity. Please log in again.",
                "category": "info",
            }
            return None
    request.session["last_seen_at"] = datetime.utcnow().isoformat()
    return get_user_by_id(int(user_id))


def require_superuser(request: Request):
    admin_user_id = request.session.get("admin_user_id")
    if not admin_user_id:
        return None
    last_seen = request.session.get("admin_last_seen_at")
    if last_seen:
        last_seen_dt = datetime.fromisoformat(last_seen)
        if datetime.utcnow() - last_seen_dt > timedelta(minutes=settings.session_timeout_minutes):
            request.session.pop("admin_user_id", None)
            request.session.pop("admin_last_seen_at", None)
            request.session["flash"] = {
                "message": f"Admin session expired after {settings.session_timeout_minutes} minutes of inactivity. Please log in again.",
                "category": "info",
            }
            return None
    request.session["admin_last_seen_at"] = datetime.utcnow().isoformat()
    user = get_user_by_id(int(admin_user_id))
    if not user or not user.get("is_superuser"):
        return None
    return user


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


def set_flash(request: Request, message: str, category: str = "info") -> None:
    request.session["flash"] = {"message": message, "category": category}


def pop_flash(request: Request):
    return request.session.pop("flash", None)


def search_catalog(query: str) -> list[dict[str, str]]:
    query_lower = query.lower()
    items: list[dict[str, str]] = []

    for service in SERVICE_ITEMS:
        haystack = f"{service['title']} {service['description']}".lower()
        if query_lower in haystack:
            items.append(
                {
                    "title": service["title"],
                    "description": service["description"],
                    "url": f"/#service-{service['slug']}",
                    "type": "Service",
                }
            )

    for resource in RESOURCE_LINKS:
        haystack = f"{resource['label']} {resource['note']}".lower()
        if query_lower in haystack:
            items.append(
                {
                    "title": resource["label"],
                    "description": resource["note"],
                    "url": resource["url"],
                    "type": "Resource",
                }
            )

    for item in EDUCATION_LIBRARY:
        haystack = f"{item['title']} {item['summary']}".lower()
        if query_lower in haystack:
            items.append(
                {
                    "title": item["title"],
                    "description": item["summary"],
                    "url": "/#education-centre",
                    "type": "Education",
                }
            )

    for contact in DOCTOR_CONTACTS:
        haystack = f"{contact['name']} {contact['details']}".lower()
        if query_lower in haystack:
            items.append(
                {
                    "title": contact["name"],
                    "description": contact["details"],
                    "url": contact["url"],
                    "type": "Doctor Support",
                }
            )

    return items


def common_context(request: Request, user, **context):
    base = {
        "request": request,
        "user": user,
        "flash": pop_flash(request),
        "about": ABOUT_CONTENT,
        "services_menu": SERVICE_ITEMS,
        "resource_links": RESOURCE_LINKS,
        "doctor_contacts": DOCTOR_CONTACTS,
        "contact_centre": CONTACT_CENTRE,
        "education_library": EDUCATION_LIBRARY,
        "support_promise": SUPPORT_PROMISE,
        "chatbot_guides": CHATBOT_GUIDES,
        "chatbot_starters": CHATBOT_STARTERS,
        "google_search_enabled": google_search_available(),
        "session_timeout_minutes": settings.session_timeout_minutes,
    }
    base.update(context)
    return base


@app.get("/")
def home(request: Request):
    user = current_user(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=common_context(request, user),
    )


@app.get("/chatbot")
def chatbot_page(request: Request):
    user = current_user(request)
    cycle_logs = list_cycle_logs(user["id"]) if user else []
    wellness_checkins = list_wellness_checkins(user["id"]) if user else []
    prediction = get_latest_prediction(user["id"]) if user else None
    chat_history = list(reversed(list_chatbot_logs(user["id"], limit=12))) if user else []
    support_profile = build_support_profile(cycle_logs, wellness_checkins, prediction)

    return templates.TemplateResponse(
        request=request,
        name="chatbot.html",
        context=common_context(
            request,
            user,
            prediction=prediction,
            chat_history=chat_history,
            support_profile=support_profile,
            latest_cycle=(cycle_logs[0] if cycle_logs else None),
            latest_checkin=(wellness_checkins[0] if wellness_checkins else None),
            chatbot_research_notice=(
                "Web research mode is active and will use Google Custom Search when configured."
                if google_search_available()
                else "Web research mode is available in the interface, but Google search will only run after API credentials are configured."
            ),
        ),
    )


@app.get("/register")
def register_page(request: Request):
    if current_user(request):
        return redirect("/dashboard")
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context=common_context(request, None),
    )


@app.get("/admin/login")
def admin_login_page(request: Request):
    if require_superuser(request):
        return redirect("/admin")
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context=common_context(request, None),
    )


@app.post("/admin/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_email(email)
    if not user or not user.get("is_superuser") or not verify_password(password, user["password_hash"]):
        set_flash(request, "Invalid admin credentials.", "error")
        return redirect("/admin/login")

    request.session["admin_user_id"] = user["id"]
    request.session["admin_last_seen_at"] = datetime.utcnow().isoformat()
    set_flash(request, "Admin login successful.", "success")
    return redirect("/admin")


@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context=common_context(request, current_user(request)),
    )


@app.post("/forgot-password")
def forgot_password_request(
    request: Request,
    email: str = Form(...),
):
    user = get_user_by_email(email)
    if user:
        otp_code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        create_password_reset_otp(user["id"], otp_code, expires_at)
        success, message = send_otp_email(user["email"], otp_code)
        request.session["reset_email"] = user["email"]
        set_flash(request, message, "success" if success else "info")
    else:
        set_flash(request, "If that email exists, a reset OTP has been prepared.", "info")
    return redirect("/reset-password")


@app.get("/reset-password")
def reset_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context=common_context(
            request,
            current_user(request),
            reset_email=request.session.get("reset_email", ""),
        ),
    )


@app.post("/reset-password")
def reset_password_submit(
    request: Request,
    email: str = Form(...),
    otp_code: str = Form(...),
    new_password: str = Form(...),
):
    user = get_user_by_email(email)
    if not user:
        set_flash(request, "Invalid reset request.", "error")
        return redirect("/reset-password")

    otp_record = get_valid_password_reset_otp(user["id"], otp_code.strip())
    if not otp_record:
        set_flash(request, "Invalid OTP code.", "error")
        return redirect("/reset-password")

    if datetime.utcnow() > datetime.fromisoformat(otp_record["expires_at"]):
        mark_password_reset_otp_used(otp_record["id"])
        set_flash(request, "That OTP has expired. Please request a new one.", "error")
        return redirect("/forgot-password")

    if len(new_password) < 6:
        set_flash(request, "New password must be at least 6 characters long.", "error")
        return redirect("/reset-password")

    update_user_password(user["id"], hash_password(new_password))
    mark_password_reset_otp_used(otp_record["id"])
    request.session.pop("reset_email", None)
    set_flash(request, "Password updated successfully. You can now log in.", "success")
    return redirect("/login")


@app.post("/register")
def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    average_cycle_length: int = Form(28),
    password: str = Form(...),
):
    if get_user_by_email(email):
        set_flash(request, "An account with that email already exists.", "error")
        return redirect("/register")

    if len(password) < 6:
        set_flash(request, "Password must be at least 6 characters long.", "error")
        return redirect("/register")

    user_id = create_user(
        full_name=full_name.strip(),
        email=email.strip(),
        age=age,
        average_cycle_length=average_cycle_length,
        password_hash=hash_password(password),
    )
    request.session["user_id"] = user_id
    set_flash(
        request,
        "Account created successfully. You can start logging your cycle.",
        "success",
    )
    return redirect("/dashboard")


@app.get("/login")
def login_page(request: Request):
    if current_user(request):
        return redirect("/dashboard")
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=common_context(request, None),
    )


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        set_flash(request, "Invalid email or password.", "error")
        return redirect("/login")

    request.session["user_id"] = user["id"]
    request.session["last_seen_at"] = datetime.utcnow().isoformat()
    set_flash(request, "Welcome back.", "success")
    return redirect("/dashboard")


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    set_flash(request, "You have been signed out.", "info")
    return redirect("/")


@app.post("/admin/logout")
def admin_logout(request: Request):
    request.session.pop("admin_user_id", None)
    request.session.pop("admin_last_seen_at", None)
    set_flash(request, "Admin signed out.", "info")
    return redirect("/admin/login")


@app.get("/admin")
def admin_page(request: Request):
    admin_user = require_superuser(request)
    if not admin_user:
        return redirect("/admin/login")

    selected_user_id = request.query_params.get("user_id")
    managed_user = (
        get_user_by_id(int(selected_user_id))
        if selected_user_id and selected_user_id.isdigit()
        else None
    )

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context=common_context(
            request,
            admin_user,
            admin_stats={
                "users": count_users(),
                "cycle_logs": count_cycle_logs(),
                "checkins": count_wellness_checkins(),
                "chat_messages": count_chat_messages(),
            },
            admin_users=list_users(),
            managed_user=managed_user,
            support_messages=list_support_messages(),
        ),
    )


@app.get("/dashboard")
def dashboard(request: Request):
    user = current_user(request)
    if not user:
        set_flash(request, "Please log in first.", "error")
        return redirect("/login")

    cycle_logs = list_cycle_logs(user["id"])
    wellness_checkins = list_wellness_checkins(user["id"])
    prediction = get_latest_prediction(user["id"])
    notifications = list_notifications(user["id"])
    support_messages = list_support_messages_for_user(user["id"])
    chat_history = list(reversed(list_chatbot_logs(user["id"])))
    report = build_dashboard_report(cycle_logs, prediction)
    support_profile = build_support_profile(cycle_logs, wellness_checkins, prediction)
    wellbeing_prompt = build_wellbeing_prompt(wellness_checkins)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=common_context(
            request,
            user,
            cycle_logs=cycle_logs,
            prediction=prediction,
            notifications=notifications,
            chat_history=chat_history,
            report=report,
            wellness_checkins=wellness_checkins,
            support_profile=support_profile,
            wellbeing_prompt=wellbeing_prompt,
            support_messages=support_messages,
        ),
    )


@app.post("/cycles")
def add_cycle_log(
    request: Request,
    start_date: str = Form(...),
    end_date: str = Form(...),
    flow_level: str = Form(...),
    mood: str = Form(...),
    symptoms: str = Form(""),
    notes: str = Form(""),
):
    user = current_user(request)
    if not user:
        set_flash(request, "Please log in first.", "error")
        return redirect("/login")

    if end_date < start_date:
        set_flash(request, "End date cannot be earlier than start date.", "error")
        return redirect("/dashboard")

    symptom_items = [item.strip() for item in symptoms.split(",") if item.strip()]
    create_cycle_log(
        user_id=user["id"],
        start_date=start_date,
        end_date=end_date,
        flow_level=flow_level,
        mood=mood,
        symptoms=symptom_items,
        notes=notes.strip(),
    )

    cycle_logs = list_cycle_logs(user["id"])
    prediction = build_prediction(cycle_logs, user["average_cycle_length"])
    if prediction:
        save_prediction(user["id"], prediction)
        replace_notifications(user["id"], build_notifications(prediction))

    set_flash(request, "Cycle data saved and insights updated.", "success")
    return redirect("/dashboard")


@app.post("/checkins")
def add_wellbeing_checkin(
    request: Request,
    checkin_date: str = Form(...),
    pain_level: int = Form(...),
    energy_level: int = Form(...),
    stress_level: int = Form(...),
    sleep_hours: float = Form(...),
    feelings: str = Form(...),
    care_preference: str = Form(...),
    support_needed: str = Form("no"),
    notes: str = Form(""),
):
    user = current_user(request)
    if not user:
        set_flash(request, "Please log in first.", "error")
        return redirect("/login")

    create_wellness_checkin(
        user_id=user["id"],
        checkin_date=checkin_date,
        pain_level=max(0, min(10, pain_level)),
        energy_level=max(1, min(10, energy_level)),
        stress_level=max(0, min(10, stress_level)),
        sleep_hours=max(0, sleep_hours),
        feelings=feelings.strip(),
        care_preference=care_preference.strip(),
        support_needed=support_needed == "yes",
        notes=notes.strip(),
    )

    set_flash(request, "Wellbeing check-in saved. Personalized support has been refreshed.", "success")
    return redirect("/dashboard")


@app.post("/chat")
def chatbot_message(
    request: Request,
    message: str = Form(...),
    source: str = Form("dashboard"),
    use_web_research: str = Form("no"),
):
    user = current_user(request)
    if not user:
        set_flash(request, "Please log in first.", "error")
        return redirect("/login")

    cleaned_message = message.strip()
    if not cleaned_message:
        set_flash(request, "Please enter a message for the chatbot.", "error")
        return redirect("/chatbot" if source == "chatbot" else "/dashboard")

    prediction = get_latest_prediction(user["id"])
    cycle_logs = list_cycle_logs(user["id"])
    wellness_checkins = list_wellness_checkins(user["id"])
    latest_cycle = cycle_logs[0] if cycle_logs else None
    latest_checkin = wellness_checkins[0] if wellness_checkins else None
    support_profile = build_support_profile(cycle_logs, wellness_checkins, prediction)
    web_research = None
    if use_web_research == "yes":
        web_research = search_google_context(cleaned_message)
    intent, response = generate_response(
        message=cleaned_message,
        prediction=prediction,
        latest_cycle=latest_cycle,
        latest_checkin=latest_checkin,
        support_profile=support_profile,
        web_research=web_research,
    )
    create_chatbot_log(user["id"], cleaned_message, response, intent)
    set_flash(request, "Chatbot response updated.", "success")
    return redirect("/chatbot" if source == "chatbot" else "/dashboard")


@app.post("/admin/users/update")
def admin_update_user(
    request: Request,
    user_id: int = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    average_cycle_length: int = Form(...),
    new_password: str = Form(""),
):
    admin_user = require_superuser(request)
    if not admin_user:
        return redirect("/admin/login")

    target_user = get_user_by_id(user_id)
    if not target_user:
        set_flash(request, "User not found.", "error")
        return redirect("/admin")

    update_user_account(
        user_id=user_id,
        full_name=full_name,
        email=email,
        age=age,
        average_cycle_length=average_cycle_length,
    )
    if new_password.strip():
        update_user_password(user_id, hash_password(new_password.strip()))

    set_flash(request, "User login details and profile updated.", "success")
    return redirect(f"/admin?user_id={user_id}")


@app.post("/admin/support")
def admin_send_support(
    request: Request,
    target_user_id: int = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
):
    admin_user = require_superuser(request)
    if not admin_user:
        return redirect("/admin/login")

    target_user = get_user_by_id(target_user_id)
    if not target_user:
        set_flash(request, "Target user not found.", "error")
        return redirect("/admin")

    create_support_message(
        admin_user_id=admin_user["id"],
        target_user_id=target_user_id,
        subject=subject,
        message=message,
    )
    set_flash(request, "Support message sent successfully.", "success")
    return redirect(f"/admin?user_id={target_user_id}")


@app.get("/search")
def search(request: Request, q: str = ""):
    query = q.strip()
    results = search_catalog(query) if query else []
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context=common_context(
            request,
            current_user(request),
            query=query,
            results=results,
        ),
    )
