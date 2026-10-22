import json
import random
from datetime import datetime, timedelta

# Фиксируем seed для воспроизводимости
random.seed(42)


def generate_raw_data(n_companies=1000):
    print(f"--- Генерация сырых данных для {n_companies} компаний в JSON ---")

    companies = []
    financial_statements = []
    credit_history = []

    regions = ["77", "50", "78", "66", "23", "54", "16"]
    opfs = ["ООО «Вектор»", "ООО «Альфа»", "ООО «ТехноПром»", "ООО «СтройРесурс»", "ООО «Торговый Дом»",
            "ООО «СофтЛайн»"]
    okveds = ["62.01", "46.90", "41.20", "56.10", "45.20"]

    base_date = datetime.now()

    for i in range(1, n_companies + 1):
        # Генерируем уникальный ИНН (10 цифр)
        inn = f"77{i:08d}"

        # Название и реквизиты
        name = f"{random.choice(opfs)} №{i}"
        opf = "Общество с ограниченной ответственностью"
        okved = random.choice(okveds)
        region = random.choice(regions)

        # Дата регистрации (от 3 месяцев до 5 лет назад)
        days_ago = random.randint(90, 1825)
        reg_date = base_date - timedelta(days=days_ago)
        reg_date_str = reg_date.strftime("%Y-%m-%d")

        # 1. Заполняем companies.json
        companies.append({
            "inn": inn,
            "name": name,
            "opf": opf,
            "okved": okved,
            "registration_date": reg_date_str,
            "region": region,
            "is_synthetic": True
        })

        # 2. Заполняем financial_statements.json (4 квартала)
        # Базовая квартальная выручка от 150 тыс. до 4 млн рублей
        base_quarterly_rev = random.uniform(150_000, 4_000_000)
        statements = []

        quarters = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
        for q_idx, period in enumerate(quarters):
            # Добавим немного тренда и случайных колебаний от квартала к кварталу
            trend_factor = random.uniform(0.85, 1.15)
            revenue = round(base_quarterly_rev * trend_factor, 2)

            # Расходы составляют 60-95% от выручки
            expense_ratio = random.uniform(0.60, 0.95)
            expenses = round(revenue * expense_ratio, 2)

            operating_profit = round(revenue - expenses, 2)

            statements.append({
                "period": period,
                "revenue": revenue,
                "expenses": expenses,
                "operating_profit": operating_profit
            })

        financial_statements.append({
            "inn": inn,
            "is_synthetic": True,
            "statements": statements
        })

        # 3. Заполняем credit_history.json
        # В 75% случаев кредитной нагрузки нет или она маленькая, в 25% — есть активный долг и просрочки
        has_loans = random.random() < 0.5
        active_monthly_loan_payments = round(random.uniform(20_000, 300_000), 2) if has_loans else 0.0

        delinquency_count_12m = 0
        max_delinquency_days_12m = 0
        if has_loans and random.random() < 0.3:
            delinquency_count_12m = random.randint(1, 3)
            max_delinquency_days_12m = random.choice([10, 30, 60, 90])

        credit_history.append({
            "inn": inn,
            "is_synthetic": True,
            "active_monthly_loan_payments": active_monthly_loan_payments,
            "delinquency_count_12m": delinquency_count_12m,
            "max_delinquency_days_12m": max_delinquency_days_12m
        })

    # Сохраняем всё в три JSON файла
    with open("data/companies.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    with open("data/financial_statements.json", "w", encoding="utf-8") as f:
        json.dump(financial_statements, f, ensure_ascii=False, indent=2)

    with open("data/credit_history.json", "w", encoding="utf-8") as f:
        json.dump(credit_history, f, ensure_ascii=False, indent=2)

    print("[УСПЕХ] Шаг 1 завершен! Созданы файлы:")
    print("  - data/companies.json")
    print("  - data/financial_statements.json")
    print("  - data/credit_history.json")


if __name__ == "__main__":
    generate_raw_data(1000)