import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Фиксируем seed, чтобы синтетические данные воспроизводились.
random.seed(42)

# Скрипт рассчитан на расположение в папке scripts/ проекта.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def save_json(filename, data):
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path


def generate_applications(companies, base_date):
    """Создаёт заявки только для компаний из сгенерированного EGRUL."""
    first_names = ["Александр", "Елена", "Дмитрий", "Ольга", "Максим", "Анна", "Сергей", "Татьяна"]
    last_names = ["Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров", "Соколов", "Михайлов"]
    middle_names = ["Иванович", "Петровна", "Сергеевич", "Александровна", "Владимирович", "Николаевна"]

    purposes_by_product = {
        "working_capital": [
            "Пополнение оборотных средств для закупки партии товаров",
            "Исполнение крупного государственного контракта",
        ],
        "investment": [
            "Приобретение нового производственного оборудования",
            "Расширение штата и открытие нового филиала",
            "Исполнение крупного государственного контракта",
        ],
        "modernization": [
            "Модернизация IT-инфраструктуры компании",
            "Приобретение нового производственного оборудования",
        ],
    }

    product_types = list(purposes_by_product)
    applications = []
    app_id = 1

    for company in companies:
        # 1–2 заявки на каждую компанию; ИНН всегда берётся из companies/egrul.
        for _ in range(random.choice([1, 2])):
            product_type = random.choice(product_types)

            # Строгое соответствие лимитам продуктов по сумме и сроку
            if product_type == "working_capital":
                amount = round(random.uniform(100_000, 3_000_000), -3)
                term = random.randint(3, 24)
            elif product_type == "investment":
                amount = round(random.uniform(1_000_000, 10_000_000), -3)
                term = random.randint(12, 60)
            else:  # modernization
                amount = round(random.uniform(1_000_000, 10_000_000), -3)
                term = random.randint(36, 120)

            created_at = (base_date - timedelta(days=random.randint(1, 15))).isoformat()
            full_name = (
                f"{random.choice(last_names)} {random.choice(first_names)} "
                f"{random.choice(middle_names)}"
            )
            phone = (
                f"+7({random.randint(900, 999)}){random.randint(100, 999)}-"
                f"{random.randint(10, 99)}-{random.randint(10, 99)}"
            )
            # Не используем название компании в email: оно может содержать кириллицу и кавычки.
            email = f"contact{app_id}@example.ru"
            status = "В обработке"

            applications.append({
                "id": app_id,
                "inn": company["inn"],
                "product_type": product_type,
                "full_name": full_name,
                "phone": phone,
                "email": email,
                "amount": float(amount),
                "term": term,
                "purpose": random.choice(purposes_by_product[product_type]),
                "status": status,
                "created_at": created_at,
                "updated_at": created_at,
                "history": [{"status": status, "timestamp": created_at}],
            })
            app_id += 1

    return applications


def generate_raw_data(n_companies=1000):
    print(f"--- Генерация сырых JSON-данных для {n_companies} компаний и заявок ---")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    companies = []
    financial_statements = []
    credit_history = []
    regions = ["77", "50", "78", "66", "23", "54", "16"]
    opfs = [
        "ООО «Вектор»", "ООО «Альфа»", "ООО «ТехноПром»",
        "ООО «СтройРесурс»", "ООО «Торговый Дом»", "ООО «СофтЛайн»",
    ]
    okveds = ["62.01", "46.90", "41.20", "56.10", "45.20"]
    base_date = datetime.now()
    quarters = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]

    for i in range(1, n_companies + 1):
        # Уникальный 10-значный синтетический ИНН.
        inn = f"77{i:08d}"
        name = f"{random.choice(opfs)} №{i}"
        days_ago = random.randint(90, 1825)
        registration_date = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        companies.append({
            "inn": inn,
            "name": name,
            "opf": "Общество с ограниченной ответственностью",
            "okved": random.choice(okveds),
            "registration_date": registration_date,
            "region": random.choice(regions),
            "is_synthetic": True,
        })

        base_quarterly_revenue = random.uniform(150_000, 4_000_000)
        statements = []
        for period in quarters:
            revenue = round(base_quarterly_revenue * random.uniform(0.85, 1.15), 2)
            expenses = round(revenue * random.uniform(0.60, 0.95), 2)
            statements.append({
                "period": period,
                "revenue": revenue,
                "expenses": expenses,
                "operating_profit": round(revenue - expenses, 2),
            })
        financial_statements.append({
            "inn": inn,
            "is_synthetic": True,
            "statements": statements,
        })

        has_loans = random.random() < 0.5
        monthly_payments = round(random.uniform(20_000, 300_000), 2) if has_loans else 0.0
        delinquency_count = 0
        max_delinquency_days = 0
        if has_loans and random.random() < 0.3:
            delinquency_count = random.randint(1, 3)
            max_delinquency_days = random.choice([10, 30, 60, 90])
        credit_history.append({
            "inn": inn,
            "is_synthetic": True,
            "active_monthly_loan_payments": monthly_payments,
            "delinquency_count_12m": delinquency_count,
            "max_delinquency_days_12m": max_delinquency_days,
        })

    applications = generate_applications(companies, base_date)

    egrul_path = save_json("egrul.json", companies)
    fns_path = save_json("fns.json", financial_statements)
    bki_path = save_json("bki.json", credit_history)
    applications_path = save_json("applications.json", applications)

    # Проверяем главную связь: каждая заявка относится к существующей компании.
    company_inns = {company["inn"] for company in companies}
    invalid_applications = [app for app in applications if app["inn"] not in company_inns]
    if invalid_applications:
        raise ValueError(f"Найдены заявки без компании в EGRUL: {len(invalid_applications)}")

    print("[УСПЕХ] Созданы файлы:")
    print(f"  - {egrul_path} ({len(companies)} компаний)")
    print(f"  - {fns_path} ({len(financial_statements)} финансовых записей)")
    print(f"  - {bki_path} ({len(credit_history)} кредитных историй)")
    print(f"  - {applications_path} ({len(applications)} заявок)")
    print("Проверка связей по ИНН пройдена.")


if __name__ == "__main__":
    generate_raw_data(1000)