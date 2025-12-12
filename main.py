"""
main.py - Ejecución completa del Motor de Riesgo
Hackathon Duoc UC 2025 - Equipo Team 16
"""

# Importaciones desde los módulos
from src.load import cargar_csv, preparar_dataset
from src.model import split_temporal, entrenar_modelo
from src.eval import evaluar_modelo, calibracion, fairness

# ================================================
# 🚀 PIPELINE COMPLETO
# ================================================

# 1️⃣ Cargar dataset
df = cargar_csv("data/rendimiento-data.csv")

# 2️⃣ Preparar datos
df_model = preparar_dataset(df)

# 3️⃣ División temporal (anti-fuga)
X_train, X_test, y_train, y_test = split_temporal(df_model)

# 4️⃣ Entrenar modelo
pipeline = entrenar_modelo(X_train, y_train)

# 5️⃣ Evaluar modelo
evaluar_modelo(pipeline, X_test, y_test)

# 6️⃣ Calibración
calibracion(pipeline, X_test, y_test)

# 7️⃣ Fairness
fairness(pipeline, X_test.assign(RIESGO=y_test))

print("\n✅ Proceso completado correctamente. Resultados generados.")
