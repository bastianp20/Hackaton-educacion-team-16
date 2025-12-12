import json
import random
from typing import Dict, Any, List
import os

import joblib
import numpy as np
import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Tutor Virtual Adaptativo - Demo",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 Tutor Virtual Adaptativo — Demo (Chatbot)")
st.warning(
    "Este sistema ofrece orientación educativa **no diagnóstica** basada en la información que entregas. "
    "Para evaluaciones formales o apoyo especializado, consulta a profesionales de la educación o salud.",
    icon="⚠️",
)

# =========================
# CARGA DEL MODELO ENTRENADO
# =========================
MODEL_PATH = os.path.join("modelo-regresion/modelo_riesgo_desercion.pkl")

try:
    modelo = joblib.load(MODEL_PATH)
except Exception as e:
    st.error(
        "❌ No se pudo cargar el modelo entrenado.\n\n"
        f"Ruta esperada: `{MODEL_PATH}`\n\n"
        "Verifica que el archivo exista y que se haya guardado correctamente "
        "con `joblib.dump(pipeline, 'modelo_logistic_regression.pkl')`.",
        icon="🚫",
    )
    st.stop()

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
        st.session_state.profile_json: Dict[str, Any] = {
            "edad": None,
            "sexo": None,
            "promedio": None,
            "asistencia_pct": None,
            "asignatura_dificil": None,
        }
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
# EXTRACCIÓN NL → JSON (HEURÍSTICA)
# =========================
def extract_profile_from_text(text: str) -> Dict[str, Any]:
    """
    Heurística simple: busca patrones de edad, sexo, promedio (1-7), asistencia (%)
    y asignatura 'que me cuesta' en lenguaje natural.
    Si no encuentra, deja campos como None.
    """
    import re

    t = text.lower()

    # Edad
    edad = None
    m_edad = re.search(r"(\d{1,2})\s*(años|anios|edad)", t) or re.search(
        r"edad\s*[:=]?\s*(\d{1,2})", t
    )
    if m_edad:
        for g in m_edad.groups():
            if g and g.isdigit():
                edad = int(g)
                break

    # Sexo
    sexo = None
    if any(w in t for w in ["masculino", "hombre", "varón", "varon"]):
        sexo = "Masculino"
    elif any(w in t for w in ["femenino", "mujer"]):
        sexo = "Femenino"
    elif any(w in t for w in ["no binario", "nobinario", "nb"]):
        sexo = "No binario"

    # Promedio (1.0 a 7.0)
    promedio = None
    m_prom = re.search(
        r"(promedio|nota[s]?\s*promedio)\s*[:=]?\s*([1-7](?:[.,]\d{1,2})?)", t
    )
    if m_prom:
        promedio = float(m_prom.group(2).replace(",", "."))

    # Asistencia (%)
    asistencia = None
    m_asist = re.search(r"(asistencia|presencia)\s*[:=]?\s*(\d{1,3})\s*%?", t)
    if m_asist:
        asistencia = min(100, max(0, int(m_asist.group(2))))

    # Asignatura que cuesta
    asignatura = None
    m_asig = re.search(
        r"(me\s+cuesta|dificultad\s+en|complica\s+|problema\s+con)\s+([a-záéíóúñ ]{3,})",
        t,
    )
    if m_asig:
        asignatura = m_asig.group(2).strip().title()

    return {
        "edad": edad,
        "sexo": sexo,
        "promedio": promedio,          # escala 1–7
        "asistencia_pct": asistencia,  # 0–100
        "asignatura_dificil": asignatura,
    }

# =========================
# SIMULACIÓN COACH (PLAN)
# =========================
def simulate_coach(payload: Dict[str, Any]) -> str:
    """
    Genera un plan de hábitos en texto, personalizado según drivers y score.
    """
    profile = payload.get("profile", {})
    drivers = payload.get("drivers", [])
    score = payload.get("score", 0.0)

    edad = profile.get("edad")
    promedio = profile.get("promedio")
    asistencia = profile.get("asistencia_pct")
    asign = profile.get("asignatura_dificil")

    recomendaciones = []

    recomendaciones.append(
        "💡 **Organización suave pero constante:** elige 3 momentos fijos a la semana para estudiar, aunque sean 25–30 minutos. Lo importante es la constancia, no la perfección."
    )
    recomendaciones.append(
        "🧠 **Técnicas de estudio amigables:** subrayar, hacer resúmenes cortos y explicar el contenido en voz alta como si se lo contaras a un amigo."
    )
    recomendaciones.append(
        "😴 **Cuidar el descanso:** dormir entre 7 y 9 horas ayuda muchísimo a la memoria y al ánimo. Estudiar muerto de sueño casi nunca resulta."
    )

    if isinstance(asistencia, (int, float)) and asistencia < 85:
        recomendaciones.append(
            "📅 **Asistencia:** intenta identificar qué te está impidiendo ir a clases (ánimo, transporte, horarios, responsabilidades). "
            "Hablarlo con un/a profesor/a o tutor/a puede abrir opciones que quizás no has considerado."
        )

    if isinstance(promedio, (int, float)) and promedio < 4.5:
        recomendaciones.append(
            "📚 **Promedio bajo:** enfócate primero en pasar de 'no entiendo nada' a 'entiendo lo básico'. "
            "Escoge 2 o 3 contenidos clave y repásalos varias veces a la semana."
        )

    if asign:
        recomendaciones.append(
            f"📘 **Asignatura que más te cuesta ({asign}):** busca ejercicios resueltos paso a paso y videos explicativos. "
            "Luego intenta hacer tú mismo/a un ejercicio similar y compáralo."
        )

    if edad and edad < 18:
        recomendaciones.append(
            "🤝 **No estás solo/a:** si estás en enseñanza básica o media, apoyarte en tu familia, algún profe de confianza o un orientador puede marcar la diferencia. "
            "Pedir ayuda no es señal de debilidad, es una estrategia inteligente."
        )

    if score is not None and score >= 0.75:
        recomendaciones.append(
            "🚨 **Nivel de riesgo alto:** sería muy bueno que converses con alguien del establecimiento "
            "(profesor jefe, orientador, encargado de convivencia) y les muestres que te preocupa tu situación. "
            "No tienes que cargar todo esto solo/a."
        )
    elif score is not None and score >= 0.5:
        recomendaciones.append(
            "🟠 **Riesgo moderado:** estás a tiempo de ajustar hábitos. Cambios pequeños pero constantes (asistir más, aprovechar clases, preguntar dudas) "
            "pueden bajar mucho ese riesgo."
        )
    else:
        recomendaciones.append(
            "🟢 **Riesgo más bien bajo:** aun así, es buena idea mantener los hábitos positivos. "
            "Si en algún momento sientes que el estrés aumenta, vuelve a revisar este plan y ajusta lo que necesites."
        )

    plan = "### 🗂️ Plan Personalizado de Hábitos (no diagnóstico)\n\n"
    plan += "Este plan está pensado para acompañarte, no para juzgarte. Tómatelo como una guía flexible, "
    plan += "que puedes adaptar a tu realidad día a día.\n\n"

    for i, r in enumerate(recomendaciones, 1):
        plan += f"{i}. {r}\n\n"

    plan += (
        "Recuerda: avanzar lento también es avanzar. Y no tienes por qué hacerlo solo/a; "
        "buscar apoyo es parte del camino. 💛"
    )

    return plan

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
# PREDICCIÓN CON MODELO REAL
# =========================
def call_predict_with_model(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Usa el modelo real de regresión logística.
    Se asume que fue entrenado con las features:
    [promedio, asistencia_pct, edad, dependencia]
    De momento usamos dependencia fija = Municipal (1).
    """
    prom = profile.get("promedio")
    asis = profile.get("asistencia_pct")
    edad = profile.get("edad")

    # Defaults suaves si falta algo
    if prom is None:
        prom = 5.0
    if asis is None:
        asis = 85.0
    if edad is None:
        edad = 18

    dep = 1  # Municipal por defecto

    X = np.array([[float(prom), float(asis), float(edad), float(dep)]])
    prob_riesgo = float(modelo.predict_proba(X)[0][1])
    pred_clase = int(modelo.predict(X)[0])

    drivers = []
    if asis < 85:
        drivers.append("Asistencia menor a 85%")
    if prom < 4.5:
        drivers.append("Promedio académico bajo")
    asign = profile.get("asignatura_dificil")
    if asign:
        drivers.append(f"Dificultad en {asign}")
    if not drivers:
        drivers.append("Hábitos a fortalecer (sueño, estudio, apoyo)")

    return {
        "score": round(prob_riesgo, 2),
        "pred_class": pred_clase,
        "drivers": drivers,
    }

# =========================
# ARRANQUE DEL CHATBOT
# =========================
if len(st.session_state.messages) == 0:
    add_assistant(
        "💬 Hola, gracias por estar aquí. Este espacio es para acompañarte y mirar tu situación académica con calma.\n\n"
        "Para empezar, cuéntame un poco sobre ti: por ejemplo tu **edad**, tu **promedio**, tu **asistencia** "
        "y si hay alguna asignatura que te esté costando.\n\n"
        "Ejemplo: *“Tengo 17 años, promedio 5.1, asistencia 82%, y me cuesta matemáticas.”*"
    )

# Render historial
render_chat()

# =========================
# INPUT DEL USUARIO
# =========================
user_input = st.chat_input(
    "Escribe aquí (edad, promedio, asistencia, asignatura que te cuesta)…"
)

if user_input:
    add_user(user_input)

    # Unimos lo que ya teníamos con lo nuevo
    extracted = extract_profile_from_text(user_input)
    profile = st.session_state.profile_json.copy()
    for k, v in extracted.items():
        if v is not None:
            profile[k] = v
    st.session_state.profile_json = profile

    # Campos clave que necesitamos para el modelo
    needed_core = ["edad", "promedio", "asistencia_pct"]
    missing = [k for k in needed_core if st.session_state.profile_json.get(k) is None]

    if missing and st.session_state.stage == "collect":
        # Preguntamos de forma amable por lo que falta
        etiquetas = {
            "edad": "tu edad",
            "promedio": "tu promedio general (entre 1.0 y 7.0)",
            "asistencia_pct": "tu porcentaje de asistencia aproximado",
        }
        faltantes_txt = ", ".join(etiquetas[m] for m in missing)
        resumen = json.dumps(st.session_state.profile_json, indent=2, ensure_ascii=False)

        add_assistant(
            "Gracias por compartir 💛. Esto es lo que llevo entendido hasta ahora:\n\n"
            f"```json\n{resumen}\n```\n"
            f"Para poder orientarte mejor, aún necesito que me cuentes un poco más sobre: **{faltantes_txt}**.\n\n"
            "Puedes responder en lenguaje natural, como si estuviéramos conversando."
        )
    else:
        # Ya tenemos lo clave → pasamos a confirmación
        pretty = json.dumps(st.session_state.profile_json, indent=2, ensure_ascii=False)
        add_assistant(
            "Perfecto, con esta información ya puedo hacer una estimación inicial.\n\n"
            "Esto es lo que interpreté de tu perfil (si algo no está bien, puedes corregirlo escribiendo de nuevo):\n\n"
            f"```json\n{pretty}\n```\n"
            "Si estás de acuerdo, aprieta el botón **Confirmar datos y estimar riesgo** en la parte principal."
        )
        st.session_state.stage = "confirm"

# =========================
# PANELES DE ACCIÓN POR ETAPA
# =========================
with st.sidebar:
    st.subheader("Flujo de la demo")
    st.markdown(
        "- ✅ Conversación y recolección de datos\n"
        "- ✅ Perfil estructurado NL→JSON\n"
        "- ✅ Predicción de riesgo (modelo real)\n"
        "- ✅ Mensaje de acompañamiento\n"
        "- ✅ Plan personalizado\n"
        "- ✅ Exportar (PDF simulado)"
    )
    st.caption("Simulación educativa — No diagnóstico.")

# --- Etapa: Confirmación de datos y predicción
if st.session_state.stage == "confirm":
    st.markdown("### 📦 Perfil interpretado")
    st.json(st.session_state.profile_json)

    cols = st.columns(2)
    with cols[0]:
        if st.button("✔️ Confirmar datos y estimar riesgo", use_container_width=True):
            result = call_predict_with_model(st.session_state.profile_json)
            st.session_state.score = result["score"]
            st.session_state.drivers = result["drivers"]
            pred_class = result["pred_class"]

            mensaje_riesgo = (
                "⚠️ Según el modelo, actualmente **apareces con riesgo de deserción/reprobación**. "
                "Esto **no es un diagnóstico**, pero sí una señal para cuidar tu proceso y buscar apoyo."
                if pred_class == 1
                else "✅ Según el modelo, **no apareces con un riesgo alto en este momento**, "
                     "pero siempre es buena idea revisar tus hábitos y tus emociones."
            )

            add_assistant(
                "Gracias por confirmar 💚.\n\n"
                f"{mensaje_riesgo}\n\n"
                f"- **Riesgo estimado (0 a 1):** `{st.session_state.score}`\n"
                f"- **Factores que parecen influir:** {', '.join(st.session_state.drivers)}\n\n"
                "Si te parece, ahora puedo generar un **plan de acción personalizado** para que no tengas que enfrentar esto solo/a."
            )
            st.session_state.stage = "predicted"

    with cols[1]:
        if st.button("↩️ Volver a ingresar datos", use_container_width=True):
            st.session_state.stage = "collect"
            add_assistant(
                "Sin problema, cuéntame de nuevo tu situación o actualiza la información que quieras 💬."
            )

# --- Etapa: Resultado de predicción
if st.session_state.stage == "predicted":
    st.markdown("### 🔎 Estimación y orientación inicial")
    score = st.session_state.score
    drivers = st.session_state.drivers

    st.metric(label="Riesgo estimado (0–1)", value=score)

    st.markdown("**Factores que parecen influir en tu situación:**")
    for d in drivers:
        st.write(f"• {d}")

    THRESHOLD = 0.75
    if score is not None and score > THRESHOLD:
        st.error(
            "El nivel estimado sugiere **priorizar apoyo y acompañamiento**. "
            "No tienes que cargar esto solo/a. Hablar con un profesor/a, tutor/a u orientador/a puede ser un muy buen paso.",
            icon="🚩",
        )
    else:
        st.info(
            "Tu riesgo no aparece extremo, pero tu experiencia igual importa. "
            "Cuidar tus hábitos y hablar cuando algo te sobrepasa sigue siendo muy importante 💛.",
            icon="💡",
        )

    if st.button("📝 Generar Plan Personalizado", use_container_width=True):
        payload = {
            "profile": st.session_state.profile_json,
            "score": st.session_state.score,
            "drivers": st.session_state.drivers,
        }
        plan = simulate_coach(payload)
        st.session_state.plan_text = plan
        add_assistant(
            "Listo, armé un **plan de acción personalizado** pensado para acompañarte paso a paso. "
            "Revísalo con calma, puedes tomar lo que te haga sentido y adaptarlo a tu realidad."
        )
        st.session_state.stage = "coaching"

# --- Etapa: Coaching + Entregables
if st.session_state.stage == "coaching":
    st.markdown("### 🗂️ Plan Personalizado de Hábitos (no diagnóstico)")
    st.markdown(st.session_state.plan_text)

    c1, c2 = st.columns(2)

    with c1:
        pdf_bytes = make_fake_pdf_bytes(st.session_state.plan_text)
        st.download_button(
            label="📄 Exportar Plan (PDF simulado)",
            data=pdf_bytes,
            file_name="plan_personalizado.pdf",
            mime="application/octet-stream",
            use_container_width=True,
        )

    with c2:
        token = st.session_state.share_token or hex(random.getrandbits(32))[2:]
        st.session_state.share_token = token
        st.success(
            "🔗 Puedes copiar la URL de tu navegador para compartir esta vista del plan (si lo consideras apropiado)."
        )

    st.caption(
        "Comparte y usa este contenido con cariño y responsabilidad. Es una guía, no un diagnóstico."
    )

# Render final del chat (con los nuevos mensajes)
render_chat()

# Pie de página
st.markdown("---")
st.caption(
    "Demo educativa en Streamlit. Modelo de riesgo basado en datos históricos. "
    "Esta herramienta es de acompañamiento, no reemplaza apoyo profesional."
)
