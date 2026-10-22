from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.application_manager import (
    create_application,
    get_user_applications,
    get_all_applications
)
import uvicorn
import os
import json

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "web", "templates")
templates = Jinja2Templates(directory=templates_dir)

# --- Существующая логика для пользователей (вход) ---
USERS_FILE = os.path.join(BASE_DIR, "data", "users.json")
def get_users():
    if not os.path.exists(USERS_FILE): return []
    with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)

@app.get("/")
def read_root():
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    users = get_users()
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    if user:
        # Упрощенно: просто перенаправляем, в реальном проекте нужны сессии
        if user["role"] == "admin":
            return RedirectResponse(url="/admin", status_code=303)
        else:
            return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверное имя пользователя или пароль"})

# --- Новая логика для кредитных заявок ---

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, full_name: str = ""):
    # Если имя не передано, показываем страницу с формой
    if not full_name:
        return templates.TemplateResponse("loan_form.html", {"request": request})
    # Если имя передано, показываем заявки этого пользователя
    user_apps = get_user_applications(full_name)
    return templates.TemplateResponse(
        "my_applications.html",
        {"request": request, "applications": user_apps, "full_name": full_name}
    )

@app.post("/submit-application")
async def submit_application(
    request: Request,
    full_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    amount: float = Form(...),
    term: int = Form(...),
    purpose: str = Form(...)
):
    data = {
        "full_name": full_name, "phone": phone, "email": email,
        "amount": amount, "term": term, "purpose": purpose
    }
    create_application(data)
    # После отправки перенаправляем на страницу со списком заявок этого пользователя
    return RedirectResponse(url=f"/dashboard?full_name={full_name}", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, search: str = ""):
    apps = get_all_applications()
    # Простой поиск по ФИО
    if search:
        apps = [app for app in apps if search.lower() in app["full_name"].lower()]
    # Сортируем по дате создания (новые сверху)
    apps.sort(key=lambda x: x["created_at"], reverse=True)
    return templates.TemplateResponse(
        "admin_panel.html",
        {"request": request, "applications": apps, "search": search}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)