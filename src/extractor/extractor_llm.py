"""
extractor_llm.py - Extractor NL→JSON usando LLM (GPT-4-Turbo)
Hackathon Duoc UC 2025 - Team 16
-------------------------------------------------------
Convierte texto libre en un JSON estructurado validado para el modelo ML,
usando la API de OpenAI con Function Calling y validadores de rango.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Cargar API Key desde .env o environment.yml
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Estructura esperada del JSON de salida
json_schema = {
    "type": "object",
    "properties": {
        "ASISTENCIA": {"type": "number", "description": "Porcentaje de asistencia (0-100)."},
        "PROM_GRAL": {"type": "number", "description": "Promedio general entre 1.0 y 7.0."},
        "EDAD_ALU": {"type": "number", "description": "Edad del estudiante (5-25 años)."},
        "GEN_ALU": {"type": "integer", "description": "Género del alumno (1=Masculino, 2=Femenino)."},
    },
    "required": ["ASISTENCIA", "PROM_GRAL", "EDAD_ALU", "GEN_ALU"]
}


def parse_nl_to_json_llm(texto: str) -> dict:
    """
    Usa un modelo LLM (GPT-4-Turbo) para extraer las variables requeridas desde texto libre.
    Retorna un JSON con validaciones y estructura fija.
    """
    prompt = f"""
    Eres un asistente que extrae información estructurada desde texto natural.
    Dado el siguiente texto sobre un estudiante, devuelve un JSON con las siguientes claves:
    - ASISTENCIA: número entre 0 y 100.
    - PROM_GRAL: número entre 1.0 y 7.0.
    - EDAD_ALU: número entre 5 y 25.
    - GEN_ALU: 1 si el texto menciona masculino, 2 si menciona femenino.

    Texto: "{texto}"

    Asegúrate de devolver solo JSON válido, sin texto adicional.
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)

    # Validaciones básicas
    errores = []
    if not (0 <= data["ASISTENCIA"] <= 100):
        errores.append("ASISTENCIA fuera de rango (0–100)")
    if not (1.0 <= data["PROM_GRAL"] <= 7.0):
        errores.append("PROM_GRAL fuera de rango (1.0–7.0)")
    if not (5 <= data["EDAD_ALU"] <= 25):
        errores.append("EDAD_ALU fuera de rango (5–25)")

    data["_valido"] = len(errores) == 0
    data["_errores"] = errores
    data["_fuente"] = "LLM"

    return data


# Ejemplo de uso directo
if __name__ == "__main__":
    ejemplo = "Una estudiante de 15 años con asistencia del 92%, promedio 5.8, género femenino."
    resultado = parse_nl_to_json_llm(ejemplo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
