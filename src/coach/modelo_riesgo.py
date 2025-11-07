"""
modelo_riesgo.py — Cálculo del riesgo de deserción usando un modelo ML entrenado.
Puedes reemplazar el modelo base (dummy) con tu modelo real Logistic Regression / XGBoost.
"""

import numpy as np
import joblib
import os

# Carga opcional del modelo entrenado
# (ajusta la ruta si tu modelo está en otra carpeta, por ejemplo "models/modelo_riesgo.pkl")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_riesgo.pkl")

# Verificamos si existe un modelo entrenado
modelo_ml = None
if os.path.exists(MODEL_PATH):
    try:
        modelo_ml = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"⚠️ No se pudo cargar el modelo ML: {e}")
else:
    print("ℹ️ No se encontró modelo_riesgo.pkl, se usará el cálculo heurístico base.")


def predecir_riesgo(asistencia: float, promedio: float, edad: int) -> tuple:
    """
    Retorna (nivel_riesgo, probabilidad)
    Si no hay modelo entrenado, usa una heurística simple.
    """
    # Si hay modelo entrenado, usamos predicción real
    if modelo_ml is not None:
        X = np.array([[asistencia, promedio, edad]])
        prob = modelo_ml.predict_proba(X)[0][1]  # probabilidad de deserción
        nivel = (
            "Alto" if prob >= 0.75 else
            "Medio" if prob >= 0.45 else
            "Bajo"
        )
        return nivel, round(float(prob), 2)

    # Si no hay modelo, usamos regla básica
    if asistencia < 85 and promedio < 5.0:
        return "Alto", 0.85
    elif asistencia < 90 or promedio < 5.3:
        return "Medio", 0.55
    else:
        return "Bajo", 0.25
