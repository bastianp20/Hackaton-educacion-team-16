"""
utils.py - Funciones auxiliares
"""
import pandas as pd

def resumen_dataframe(df: pd.DataFrame):
    print(f"📋 Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    print(f"Nulos totales: {df.isna().sum().sum()}")
    return df.describe()
