import json
import numpy as np
import pandas as pd

np.random.seed(42)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_annuity_payment(principal, annual_rate, months):
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return principal / months
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return payment


def build_investment_csv():
    print("--- Запуск сборщика датасета: Инвестиционный кредит (по данным applications.json) ---")

    # Загружаем оба файла
    features_list = load_json("../data/company_features.json")
    applications_list = load_json("../data/applications.json")

    if not features_list or not applications_list:
        print("[ОШИБКА] Проверьте наличие company_features.json и applications.json!")
        return

    # Создаем быстрый доступ к фичам компаний по ИНН (словарь)
    features_map = {comp["inn"]: comp for comp in features_list}

    dataset_rows = []

    for app in applications_list:
        # Берем только инвестиционные кредиты
        if app.get("product_type") != "investment":
            continue

        inn = app["inn"]

        # Если для заявки не нашлось фичей компании, пропускаем
        if inn not in features_map:
            continue

        comp = features_map[inn]

        # Бедем параметры строго из поданной заявки
        requested_amount = app["amount"]
        requested_term_months = app["term"]
        annual_interest_rate = 14.0  # Ставка 14%

        new_monthly_loan_payment = calculate_annuity_payment(
            requested_amount, annual_interest_rate, requested_term_months
        )

        # Денежный остаток
        net_cash_after_all_debts = comp["net_cash_base"] - new_monthly_loan_payment

        # СКОРИНГОВАЯ СИСТЕМА ДЛЯ ИНВЕСТИЦИЙ
        risk_score = 0

        if net_cash_after_all_debts < 0:
            risk_score += 4
        elif net_cash_after_all_debts < new_monthly_loan_payment * 1.3:
            risk_score += 2

        if comp["delinquency_count_12m"] > 0:
            risk_score += 3
        if comp["max_delinquency_days_12m"] > 30:
            risk_score += 3

        if comp["revenue_growth_rate"] < -0.1:
            risk_score += 2
        if comp["revenue_volatility_std"] > comp["avg_monthly_revenue_12m"] * 0.25:
            risk_score += 1

        # Порог дефолта, чтобы доля была ~15-20%
        noise = np.random.normal(0, 0.7)
        effective_score = risk_score + noise
        target_default_12m = 1 if effective_score >= 6.3 else 0

        dataset_rows.append({
            "application_id": app.get("application_id"),
            "inn": inn,
            "business_age_months": comp["business_age_months"],
            "avg_monthly_revenue_12m": comp["avg_monthly_revenue_12m"],
            "revenue_growth_rate": comp["revenue_growth_rate"],
            "revenue_volatility_std": comp["revenue_volatility_std"],
            "avg_monthly_expenses_12m": comp["avg_monthly_expenses_12m"],
            "existing_monthly_loan_payments": comp["monthly_loan_payments"],
            "delinquency_count_12m": comp["delinquency_count_12m"],
            "max_delinquency_days_12m": comp["max_delinquency_days_12m"],
            "requested_amount": round(requested_amount, 2),
            "requested_term_months": requested_term_months,
            "new_monthly_loan_payment": round(new_monthly_loan_payment, 2),
            "net_cash_after_all_debts": round(net_cash_after_all_debts, 2),
            "target_default_12m": target_default_12m
        })

    df = pd.DataFrame(dataset_rows)
    output_filename = "../data/investment_training.csv"
    df.to_csv(output_filename, index=False, encoding='utf-8')

    print(f"[УСПЕХ] Датасет для инвестиционного кредита сохранен: {output_filename}")
    print(f"Всего строк: {len(df)}")
    if not df.empty:
        print(f"Доля дефолтов: {df['target_default_12m'].mean() * 100:.2f}%\n")


if __name__ == "__main__":
    build_investment_csv()