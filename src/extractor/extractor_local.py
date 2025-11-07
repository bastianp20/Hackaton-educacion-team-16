"""
extractor_local.py - Extractor NL→JSON local basado en expresiones regulares
Hackathon Duoc UC 2025 - Equipo Team 16
-------------------------------------------------------
Convierte texto libre en un JSON estructurado con validadores de negocio.
"""

import re
import json

def parse_nl_to_json(texto: str) -> dict:
    """
    Extrae información numérica y categórica desde texto libre.
    Detecta: asistencia (%), promedio (1.0–7.0), edad (años) y género (masculino/femenino).
    Retorna un diccionario validado y compatible con el modelo ML.
    """

    

    # Patrones base mejorados
    patrones = {
        "ASISTENCIA": re.search(
            r"(?:asistencia\s*(?:de\s*)?)?(\d{1,3})\s*(?:%|por\s*ciento)?",
            texto,
            re.IGNORECASE
        ),
        "PROM_GRAL": re.search(
            r"(?:promedio|nota)\s*(?:de\s*)?(\d+(?:[.,]\d+)?)",
            texto,
            re.IGNORECASE
        ),
        "EDAD_ALU": re.search(
            r"(\d{1,2})\s*(?:años|año)",
            texto,
            re.IGNORECASE
        ),
        "GEN_ALU": re.search(
            r"\b(masculin[oa]|feminin[oa])\b",
            texto,
            re.IGNORECASE
        )
    }


    

    # Valores encontrados
    data = {}

    # Conversión segura de cada valor encontrado
    for campo, match in patrones.items():
        if not match:
            data[campo] = None
            continue

        valor = match.group(1).replace(",", ".")
        if campo in ["PROM_GRAL", "EDAD_ALU", "ASISTENCIA"]:
            try:
                valor = float(valor)
            except ValueError:
                valor = None

        if campo == "GEN_ALU":
            data[campo] = 1 if "masculin" in match.group(1).lower() else 2
        else:
            data[campo] = valor

    # Validadores de rango
    errores = []
    if data.get("PROM_GRAL") is not None and not (1.0 <= data["PROM_GRAL"] <= 7.0):
        errores.append("PROM_GRAL fuera de rango (1.0–7.0)")
    if data.get("ASISTENCIA") is not None and not (0 <= data["ASISTENCIA"] <= 100):
        errores.append("ASISTENCIA fuera de rango (0–100)")
    if data.get("EDAD_ALU") is not None and not (5 <= data["EDAD_ALU"] <= 25):
        errores.append("EDAD_ALU fuera de rango (5–25)")

    data["_valido"] = len(errores) == 0
    data["_faltantes"] = [k for k, v in data.items() if v is None and not k.startswith("_")]
    data["_errores"] = errores

    return data


# Ejemplo de uso directo (solo para prueba local)
if __name__ == "__main__":
    ejemplo = "Alumno con asistencia de 85 por ciento, promedio 5,8. Edad 14 años, género masculino."
    resultado = parse_nl_to_json(ejemplo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
