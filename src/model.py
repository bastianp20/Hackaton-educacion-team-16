"""
model.py - Entrenamiento del modelo Logistic Regression (Motor de Riesgo)
Parte del proyecto Hackathon Duoc UC 2025
"""

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pandas as pd

def split_temporal(df_model):
    """Realiza validación temporal o split 80/20 si solo hay datos 2024."""
    if "AGNO" not in df_model.columns:
        raise ValueError("El dataset no contiene la columna AGNO")

    if df_model["AGNO"].nunique() == 1:
        print("⚠️ Solo existe un año, aplicando 80/20 aleatorio.")
        train, test = train_test_split(df_model, test_size=0.2, random_state=42)
    else:
        train = df_model[df_model["AGNO"] < df_model["AGNO"].max()]
        test = df_model[df_model["AGNO"] == df_model["AGNO"].max()]

    X_train = train[["PROM_GRAL", "ASISTENCIA", "GEN_ALU", "EDAD_ALU"]]
    y_train = train["RIESGO"]
    X_test = test[["PROM_GRAL", "ASISTENCIA", "GEN_ALU", "EDAD_ALU"]]
    y_test = test["RIESGO"]

    print(f"📊 Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    return X_train, X_test, y_train, y_test

def entrenar_modelo(X_train, y_train):
    """Crea y entrena el pipeline base (scaler + logistic regression)."""
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000, random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    print("✅ Modelo entrenado correctamente.")
    return pipeline
