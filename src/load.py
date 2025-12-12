"""
load.py - Carga y preprocesamiento de datos MINEDUC
Parte del proyecto Hackathon Duoc UC 2025 (Tutor Virtual Adaptativo IA Híbrida)
"""

import pandas as pd
import numpy as np

def cargar_csv(ruta="data/rendimiento-data.csv"):
    """Lee el CSV de rendimiento escolar probando separadores y codificaciones comunes."""
    intentos = [
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin1"},
        {"sep": ",", "encoding": "utf-8"},
    ]
    for cfg in intentos:
        try:
            df = pd.read_csv(ruta, low_memory=False, **cfg)
            print(f"✅ Cargado con sep='{cfg['sep']}', encoding='{cfg['encoding']}'")
            return df
        except Exception:
            continue
    raise RuntimeError("❌ No se pudo leer el CSV con los separadores y codificaciones probados.")

def preparar_dataset(df):
    """Filtra columnas necesarias, convierte tipos, crea variable RIESGO y devuelve df_model listo para ML."""
    columnas_usadas = ["AGNO", "SIT_FIN", "PROM_GRAL", "ASISTENCIA", "GEN_ALU", "EDAD_ALU"]
    df_model = df[columnas_usadas].copy()

    # Limpieza y conversión
    df_model = df_model.dropna(subset=["SIT_FIN", "PROM_GRAL", "ASISTENCIA"])
    for c in ["PROM_GRAL", "ASISTENCIA", "EDAD_ALU"]:
        df_model[c] = pd.to_numeric(df_model[c], errors="coerce")

    # Mapeo de variable objetivo
    df_model = df_model[df_model["SIT_FIN"].isin(["P", "R", "Y"])]
    df_model["RIESGO"] = df_model["SIT_FIN"].map({"P": 0, "R": 1, "Y": 1})
    df_model = df_model.dropna()

    print("📊 Distribución de clases RIESGO (0=Promovido, 1=Riesgo):")
    print(df_model["RIESGO"].value_counts(normalize=True).round(3) * 100)
    return df_model
