"""
pipeline.py — Flujo principal del Coach híbrido ML + LLM + RAG
"""

from dataclasses import dataclass
from openai import OpenAI
from src.coach.rag import LocalRAG
from src.coach.prompt import PROMPT_TEMPLATE
from src.coach.derivacion import evaluar_derivacion
from dotenv import load_dotenv
import os


# --- 0. Cargar variables de entorno (.env)
load_dotenv()


@dataclass
class PerfilAlumno:
    asistencia: float
    promedio: float
    edad: int
    genero: int


def coach_plan(perfil: PerfilAlumno, verbose: bool = False) -> dict:
    """
    Genera un plan personalizado combinando RAG + LLM + reglas locales.
    """
    # 1. Preparar RAG
    rag = LocalRAG("kb")
    rag.load_kb()
    rag.build()
    contexto = rag.format_context(rag.retrieve("plan educativo", top_k=3))

    # 2. Preparar prompt
    prompt = PROMPT_TEMPLATE.format(
        context=contexto,
        asistencia=perfil.asistencia,
        promedio=perfil.promedio,
        edad=perfil.edad,
        genero="Masculino" if perfil.genero == 1 else "Femenino"
    )

    # 3. Ejecutar LLM (usa la API key del archivo .env)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un tutor educativo empático y analítico."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    plan_text = response.choices[0].message.content

    # 4. Evaluar derivación local
    derivar, motivo = evaluar_derivacion(perfil.asistencia, perfil.promedio)

    if verbose:
        print(plan_text)
        print(f"\n[Derivación sugerida] {motivo if derivar else 'No aplica.'}")

    # 5. Retornar estructura completa
    return {
        "plan": plan_text,
        "fuentes": [d.title for d, _ in rag.retrieve("plan educativo", top_k=3)],
        "guardrail_derivacion": derivar,
        "motivo_derivacion": motivo
    }
