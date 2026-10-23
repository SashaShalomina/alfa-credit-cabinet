import json
import numpy as np
from datetime import datetime


def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_feature_pipeline():
    print("--- Запуск пайплайна: JSON -> company_features.json ---")

    companies = load_json("../data/companies.json")
    statements_data = load_json("../data/financial_statements.json")
    credit_data = load_json("../data/credit_history.json")

    statements_map = {item["inn"]: item["statements"] for item in statements_data}
    credit_map = {item["inn"]: item for item in credit_data}

    all_features = []
    current_date = datetime.now()

    for comp in companies:
        inn = comp["inn"]

        # Стаж бизнеса в месяцах
        reg_date = datetime.strptime(comp["registration_date"], "%Y-%m-%d")
        business_age_months = (current_date.year - reg_date.year) * 12 + (current_date.month - reg_date.month)

        # Фильтр по стажу для оборотного кредита (>= 6 месяцев)
        if business_age_months < 6:
            continue

        periods = statements_map.get(inn, [])
        if not periods:
            continue

        revenues = [p["revenue"] for p in periods]
        expenses = [p["expenses"] for p in periods]
        profits = [p["operating_profit"] for p in periods]

        avg_monthly_revenue = sum(revenues) / 12.0
        revenue_growth_rate = (revenues[-1] - revenues[0]) / revenues[0] if revenues[0] > 0 else 0.0
        revenue_volatility_std = float(np.std(revenues))

        avg_monthly_expenses = sum(expenses) / 12.0
        total_operating_profit = sum(profits)

        cred = credit_map.get(inn, {})
        existing_loans = cred.get("active_monthly_loan_payments", 0.0)
        delinq_count = cred.get("delinquency_count_12m", 0)
        max_delinq_days = cred.get("max_delinquency_days_12m", 0)

        # Базовый чистый денежный остаток (без учета нового кредита)
        net_cash_base = avg_monthly_revenue - avg_monthly_expenses - existing_loans

        feature_record = {
            "inn": inn,
            "is_synthetic": comp.get("is_synthetic", True),
            "business_age_months": business_age_months,
            "avg_monthly_revenue_12m": round(avg_monthly_revenue, 2),
            "revenue_growth_rate": round(revenue_growth_rate, 4),
            "revenue_volatility_std": round(revenue_volatility_std, 2),
            "avg_monthly_expenses_12m": round(avg_monthly_expenses, 2),
            "total_operating_profit_12m": round(total_operating_profit, 2),
            "monthly_loan_payments": round(existing_loans, 2),
            "delinquency_count_12m": delinq_count,
            "max_delinquency_days_12m": max_delinq_days,
            "net_cash_base": round(net_cash_base, 2)
        }
        all_features.append(feature_record)

    save_json("../data/company_features.json", all_features)
    print(f"[УСПЕХ] Файл data/company_features.json успешно сформирован ({len(all_features)} записей).\n")


if __name__ == "__main__":
    run_feature_pipeline()