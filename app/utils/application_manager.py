import json
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
APPLICATIONS_FILE = os.path.join(DATA_DIR, "..", "data", "applications.json")


def load_applications():
    if not os.path.exists(APPLICATIONS_FILE):
        return []
    with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_applications(apps):
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=4)


def create_application(data: dict):
    apps = load_applications()
    new_id = max([app["id"] for app in apps], default=0) + 1
    now = datetime.now()

    new_app = {
        "id": new_id,
        "full_name": data["full_name"],
        "phone": data["phone"],
        "email": data["email"],
        "amount": data["amount"],
        "term": data["term"],
        "purpose": data["purpose"],
        "status": "В обработке",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "history": [{"status": "В обработке", "timestamp": now.isoformat()}]
    }

    apps.append(new_app)
    save_applications(apps)
    return new_app


def get_user_applications(full_name: str):
    apps = load_applications()
    # Простой поиск по ФИО (можно улучшить)
    return [app for app in apps if full_name.lower() in app["full_name"].lower()]


def update_application_status(app_id: int, new_status: str):
    apps = load_applications()
    for app in apps:
        if app["id"] == app_id:
            now = datetime.now().isoformat()
            app["status"] = new_status
            app["updated_at"] = now
            app["history"].append({"status": new_status, "timestamp": now})
            save_applications(apps)
            return app
    return None


def get_all_applications():
    return load_applications()