import json
import random
from io import BytesIO
from typing import Dict, Any, List, Tuple

import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="Tutor Virtual Adaptativo - Demo", page_icon="🎓", layout="centered")

# ---------- Guardrails visibles (B3)
st.title("🎓 Tutor Virtual Adaptativo — Demo (Chatbot)")
st.warning(
    "Este sistema ofrece orientación educativa **no diagnóstica** basada en la información que entregas. "
    "Para evaluaciones formales o apoyo especializado, consulta a profesionales de la educación o salud.",
    icon="⚠️",
)

# =========================
# ESTADO DE LA APLICACIÓN
# =========================
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []
    if "stage" not in st.session_state:
        # stages: collect -> confirm -> predicted -> coaching
        st.session_state.stage = "collect"
    if "profile_json" not in st.session_state:
        st.session_state.profile_json: Dict[str, Any] = {}
    if "score" not in st.session_state:
        st.session_state.score = None
    if "drivers" not in st.session_state:
        st.session_state.drivers: List[str] = []
    if "plan_text" not in st.session_state:
        st.session_state.plan_text = ""
    if "share_token" not in st.session_state:
        st.session_state.share_token = None

init_state()

# =========================
# UTILIDADES UI
# =========================
def add_assistant(msg: str):
    # lenguaje inclusivo y no-diagnóstico
    st.session_state.messages.append({"role": "assistant", "content": msg})

def add_user(msg: str):
    st.session_state.messages.append({"role": "user", "content": msg})

def render_chat():
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# =========================
# EXTRACCIÓN NL → JSON (SIMULADA)
# =========================
def extract_profile_from_text(text: str) -> Dict[str, Any]:
    """
    Heurística simple: busca patrones de edad, sexo, promedio (1-7), asistencia (%)
    y asignatura 'que me cuesta' en lenguaje natural.
    Si no encuentra, deja campos como None.
    """
    import re

    # Normalización simple
    t = text.lower()

    # Edad
    edad = None
    m_edad = re.search(r"(\d{1,2})\s*(años|anios|edad)", t) or re.search(r"edad\s*[:=]?\s*(\d{1,2})", t)
    if m_edad:
        # si grupo 1; si hay dos grupos toma el num
        for g in m_edad.groups():
            if g and g.isdigit():
                edad = int(g); break

    # Sexo
    sexo = None
    if "masculino" in t or "hombre" in t or "varón" in t or "varon" in t:
        sexo = "Masculino"
    elif "femenino" in t or "mujer" in t:
        sexo = "Femenino"
    elif "no binario" in t or "nobinario" in t or "nb" in t:
        sexo = "No binario"

    # Promedio (1.0 a 7.0)
    promedio = None
    m_prom = re.search(r"(promedio|nota[s]?\s*promedio)\s*[:=]?\s*([1-7](?:[.,]\d{1,2})?)", t)
    if m_prom:
        promedio = float(m_prom.group(2).replace(",", "."))

    # Asistencia (%)
    asistencia = None
    m_asist = re.search(r"(asistencia|presencia)\s*[:=]?\s*(\d{1,3})\s*%?", t)
    if m_asist:
        asistencia = min(100, max(0, int(m_asist.group(2))))

    # Asignatura que cuesta
    asignatura = None
    # frases tipo "me cuesta X", "dificultad en X"
    m_asig = re.search(
        r"(me\s+cuesta|dificultad\s+en|complica\s+|problema\s+con)\s+([a-záéíóúñ ]{3,})",
        t
    )
    if m_asig:
        asignatura = m_asig.group(2).strip().title()

    return {
        "edad": edad,
        "sexo": sexo,
        "promedio": promedio,         # escala 1–7 asumida (Chile)
        "asistencia_pct": asistencia, # 0–100
        "asignatura_dificil": asignatura,
    }

# =========================
# SIMULACIÓN DE API (FastAPI)
# =========================
USE_REQUESTS = False  # pon True si ya tienes endpoints reales
API_BASE = "http://localhost:8000"

def simulate_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simula POST /predict
    Regla simple: menor promedio y menor asistencia => mayor score
    Drivers según umbrales.
    """
    prom = payload.get("promedio")
    asis = payload.get("asistencia_pct")
    asign = payload.get("asignatura_dificil")

    # Normalización de score (heurística didáctica)
    # promedio 1–7 -> inverting scale to risk: lower avg => higher risk
    prom_component = 0.0
    if isinstance(prom, (int, float)):
        prom_component = (7.0 - max(1.0, min(7.0, float(prom)))) / 6.0  # 0..1

    asis_component = 0.0
    if isinstance(asis, (int, float)):
        asis_f = max(0.0, min(100.0, float(asis)))
        asis_component = (100.0 - asis_f) / 100.0  # 0..1

    base = 0.35 * prom_component + 0.5 * asis_component + 0.1
    # ruido leve para variabilidad
    score = max(0.0, min(1.0, base + random.uniform(-0.03, 0.03)))

    drivers = []
    if isinstance(asis, (int, float)) and asis < 85:
        drivers.append("Asistencia menor a 85%")
    if isinstance(prom, (int, float)) and prom < 4.5:
        drivers.append("Promedio académico bajo")
    if asign:
        drivers.append(f"Dificultad en {asign}")

    if not drivers:
        drivers = ["Hábitos a fortalecer (sueño, estudio, apoyo)"]

    return {"score": round(score, 2), "drivers": drivers}

def simulate_coach(payload: Dict[str, Any]) -> str:
    """
    Simula POST /coach -> plan de hábitos en texto.
    Personaliza según drivers.
    """
    drivers = payload.get("drivers", [])
    recomendaciones = [
        "Establecer horarios consistentes de estudio (bloques de 25–40 min + pausas breves).",
        "Planificar repasos semanales con foco en contenidos clave.",
        "Dormir 7–9 horas, manteniendo higiene del sueño.",
        "Solicitar retroalimentación breve al/la docente tras evaluaciones.",
        "Usar un registro semanal de asistencia y motivos de ausencias."
    ]
    extra = []
    for d in drivers:
        d_low = d.lower()
        if "asistencia" in d_low:
            extra.append("Coordinar recordatorios y transporte para llegar a tiempo; conversar con tutor/a sobre barreras de asistencia.")
        if "promedio" in d_low:
            extra.append("Practicar 3 ejercicios diarios de la asignatura con mayor dificultad y resolver dudas en tutorías.")
        if "dificultad" in d_low:
            extra.append("Realizar mapas conceptuales y ejercicios guiados para la asignatura desafiadora, 3 veces por semana.")

    plan = "Plan Personalizado de Hábitos (no diagnóstico)\n\n"
    plan += "Objetivo: fortalecer hábitos y apoyo oportuno para mejorar el proceso de aprendizaje.\n\n"
    plan += "Recomendaciones generales:\n"
    for i, r in enumerate(recomendaciones, 1):
        plan += f"  {i}. {r}\n"
    if extra:
        plan += "\nEnfoques específicos según necesidades:\n"
        for i, r in enumerate(extra, 1):
            plan += f"  {i}. {r}\n"
    plan += "\nRecursos sugeridos: calendario semanal, app de recordatorios, guía de estudio por asignatura."
    return plan

def call_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    if USE_REQUESTS:
        import requests
        r = requests.post(f"{API_BASE}/predict", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    return simulate_predict(payload)

def call_coach(payload: Dict[str, Any]) -> str:
    if USE_REQUESTS:
        import requests
        r = requests.post(f"{API_BASE}/coach", json=payload, timeout=10)
        r.raise_for_status()
        # asume {"plan": "..."}
        return r.json().get("plan", "")
    return simulate_coach(payload)

# =========================
# FUNCIÓN: DESCARGA SIMULADA PDF
# =========================
def make_fake_pdf_bytes(text: str) -> bytes:
    """
    Simula un PDF: empaqueta el texto en bytes.
    (Para demo; en producción usar reportlab/fpdf para PDF real)
    """
    content = f"--- PLAN PERSONALIZADO (SIMULADO PDF) ---\n\n{text}\n"
    return content.encode("utf-8")

# =========================
# FUNCIÓN: LINK COMPARTIBLE
# =========================
def build_share_link(score: float, drivers: List[str], token: str) -> str:
    qp = st.query_params
    qp["score"] = str(score)
    qp["drivers"] = json.dumps(drivers, ensure_ascii=False)
    qp["ref"] = token
    # Streamlit muestra la URL actual con esos parámetros
    return st.experimental_get_query_params() or {}  # mantener compatibilidad

def get_current_url() -> str:
    # Método aproximado para recuperar la URL visible (Streamlit no provee url absoluta estándar)
    # Instruimos al usuario a copiar desde la barra del navegador.
    return "Copia esta URL desde tu navegador; incluye los parámetros actuales."

# =========================
# ARRANQUE DEL CHATBOT
# =========================
if len(st.session_state.messages) == 0:
    add_assistant(
        "¡Hola! Estoy aquí para ofrecer orientación **no diagnóstica** y apoyarte en tu proceso de aprendizaje. "
        "Para comenzar, por favor cuéntame tu perfil en texto libre. "
        "Por ejemplo: *“Tengo 16 años, masculino, promedio 5.1, asistencia 82%, me cuesta matemáticas.”*"
    )

# Render historial
render_chat()

# =========================
# INPUT DEL USUARIO
# =========================
user_input = st.chat_input("Escribe aquí (edad, sexo, promedio, asistencia, asignatura que te cuesta)…")

if user_input:
    add_user(user_input)

    if st.session_state.stage == "collect":
        profile = extract_profile_from_text(user_input)
        st.session_state.profile_json = profile

        # Respuesta del asistente con los datos estructurados
        pretty = json.dumps(profile, indent=2, ensure_ascii=False)
        add_assistant(
            "Gracias por la información. Esto es lo que interpreté (puedes corregir si algo no es exacto):\n\n"
            f"```json\n{pretty}\n```\n"
            "Si está bien, presiona **Confirmar datos** para estimar tu nivel de riesgo (no diagnóstico)."
        )
        st.session_state.stage = "confirm"

# =========================
# PANELES DE ACCIÓN POR ETAPA
# =========================
with st.sidebar:
    st.subheader("Flujo de la demo")
    st.markdown(
        "- ✅ Recolección (texto libre)\n"
        "- ✅ Mostrar NL→JSON (confirmación)\n"
        "- ✅ Predicción con drivers\n"
        "- ✅ Umbral de derivación\n"
        "- ✅ Plan personalizado\n"
        "- ✅ Exportar y compartir"
    )
    st.caption("Simulación educativa — No diagnóstico.")

# --- Etapa: Confirmación de datos y predicción
if st.session_state.stage == "confirm":
    st.markdown("### 📦 Datos interpretados (simulados NL→JSON)")
    st.json(st.session_state.profile_json)

    cols = st.columns(2)
    with cols[0]:
        if st.button("✔️ Confirmar datos y predecir", use_container_width=True):
            # Llamada a /predict (simulada o real)
            result = call_predict(st.session_state.profile_json)
            st.session_state.score = result["score"]
            st.session_state.drivers = result["drivers"]

            # Mensajes al chat
            add_assistant(
                f"Gracias por confirmar. Estimación **no diagnóstica**:\n\n"
                f"- **Riesgo estimado:** `{st.session_state.score}` (0 a 1)\n"
                f"- **Factores influyentes (drivers):** {', '.join(st.session_state.drivers)}\n\n"
                "Recuerda: estos resultados son orientativos y no reemplazan el apoyo profesional."
            )
            st.session_state.stage = "predicted"

    with cols[1]:
        if st.button("↩️ Volver a ingresar datos", use_container_width=True):
            st.session_state.stage = "collect"
            add_assistant("Claro, puedes ingresar nuevamente tu perfil en texto libre cuando quieras.")

# --- Etapa: Resultado de predicción
if st.session_state.stage == "predicted":
    st.markdown("### 🔎 Estimación y orientación")
    score = st.session_state.score
    drivers = st.session_state.drivers

    # Feedback inmediato
    st.metric(label="Riesgo estimado (0–1)", value=score)

    # Drivers accesibles
    st.markdown("**Factores influyentes identificados** (en lenguaje simple):")
    for d in drivers:
        st.write(f"• {d}")

    # Umbral de derivación
    THRESHOLD = 0.75
    if score is not None and score > THRESHOLD:
        st.error(
            "El nivel estimado sugiere **priorizar apoyo**. "
            "Considera conversar con tu docente/tutor/a u orientador/a para un acompañamiento oportuno.",
            icon="🚩"
        )
    else:
        st.info(
            "Sugerencia: fortalece hábitos y solicita retroalimentación formativa. "
            "Si sientes que necesitas apoyo adicional, conversa con tus docentes.",
            icon="💡"
        )

    # Botón para coaching
    if st.button("📝 Generar Plan Personalizado", use_container_width=True):
        payload = {
            "profile": st.session_state.profile_json,
            "score": st.session_state.score,
            "drivers": st.session_state.drivers,
        }
        plan = call_coach(payload)
        st.session_state.plan_text = plan
        add_assistant("He generado un plan personalizado con recomendaciones prácticas (no diagnósticas).")
        st.session_state.stage = "coaching"

# --- Etapa: Coaching + Entregables
if st.session_state.stage == "coaching":
    st.markdown("### 🗂️ Plan Personalizado de Hábitos (no diagnóstico)")
    st.text(st.session_state.plan_text)

    c1, c2 = st.columns(2)

    with c1:
        # Exportar "PDF" simulado
        pdf_bytes = make_fake_pdf_bytes(st.session_state.plan_text)
        st.download_button(
            label="📄 Exportar Plan (PDF simulado)",
            data=pdf_bytes,
            file_name="plan_personalizado.pdf",
            mime="application/octet-stream",
            use_container_width=True,
        )

    with c2:
        # Link compartible (coloca parámetros en la URL actual)
        token = st.session_state.share_token or hex(random.getrandbits(32))[2:]
        st.session_state.share_token = token
        _ = build_share_link(st.session_state.score, st.session_state.drivers, token)
        st.success("🔗 Parámetros agregados a la URL. Copia el enlace desde tu navegador para compartir.")

    st.caption("Comparte de forma responsable. Este contenido es orientativo y no constituye diagnóstico.")

# Render final del chat (con los nuevos mensajes)
render_chat()

# Pie de página
st.markdown("---")
st.caption(
    "Demo educativa en Streamlit. Si integras FastAPI real, pon `USE_REQUESTS=True` y ajusta `API_BASE`."
)
