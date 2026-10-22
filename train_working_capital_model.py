import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from catboost import CatBoostClassifier


def train_model():
    print("--- Запуск обучения CatBoost для Оборотного кредита ---")

    # 1. Загружаем датасет
    df = pd.read_csv("data/working_capital_training.csv")
    print(f"Загружено строк: {len(df)}")
    print(f"Баланс классов (доли дефолтов): {df['target_default_12m'].mean() * 100:.2f}%\n")

    # 2. Разделяем на признаки (X) и целевую переменную (y)
    X = df.drop(columns=["target_default_12m"])
    y = df["target_default_12m"]

    # 3. Делим на тренировочную и тестовую выборки (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Инициализируем и обучаем CatBoostClassifier
    model = CatBoostClassifier(
        iterations=500,
        learning_rate=0.05,
        depth=5,
        eval_metric='AUC',
        random_seed=42,
        verbose=100  # Выводить лог каждые 100 итераций
    )

    print("Обучение модели...")
    model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=50,
        use_best_model=True
    )

    # 5. Оцениваем качество на тестовой выборке
    print("\n--- Оценка качества модели ---")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"ROC-AUC Score: {roc_auc:.4f}\n")

    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # 6. Смотрим важность признаков (Feature Importance)
    print("\n--- Важность признаков (Feature Importance) ---")
    feature_importances = pd.DataFrame({
        'feature': X.columns,
        'importance': model.get_feature_importance()
    }).sort_values(by='importance', ascending=False)

    print(feature_importances.to_string(index=False))

    # 7. Сохраняем модель
    model_filename = "models/catboost_working_capital.cbm"
    model.save_model(model_filename)
    print(f"\n[УСПЕХ] Модель успешно сохранена в файл: {model_filename}")


if __name__ == "__main__":
    train_model()