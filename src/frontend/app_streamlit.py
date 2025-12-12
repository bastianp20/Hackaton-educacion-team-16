"""
App Streamlit - Tutor Virtual Adaptativo con IA Híbrida
-------------------------------------------------------
Interfaz visual para el motor de riesgo + coach RAG-LLM.
Permite ingresar texto libre o datos estructurados y obtener un plan personalizado.
"""

# --- Add project root to sys.path so "src" is importable ---
import os, sys, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# -----------------------------------------------------------

import streamlit as st
from src.extractor.extractor_llm import parse_nl_to_json_llm
from src.coach.coach_llm import PerfilAlumno, coach_plan
from src.coach.modelo_riesgo import predecir_riesgo


# -----------------------------
# 🎨 CONFIGURACIÓN DE LA APP
# -----------------------------
st.set_page_config(
    page_title="Tutor Virtual Adaptativo - Team 16",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Tutor Virtual Adaptativo con IA Híbrida")
st.markdown("""
Este sistema utiliza **Machine Learning + LLM + RAG local**  
para estimar riesgo y generar planes personalizados basados en evidencia educativa.
""")

st.divider()

# -----------------------------
# 🧠 ENTRADA DE DATOS
# -----------------------------
st.subheader("🗒️ Ingreso de información del estudiante")

modo = st.radio("Selecciona modo de ingreso:", ["Texto libre (IA)", "Manual"])

if modo == "Texto libre (IA)":
    texto = st.text_area(
        "Escribe una descripción del estudiante:",
        placeholder="Ejemplo: Alumno de 14 años, asistencia 82%, promedio 5.2, género masculino...",
        height=150
    )
else:
    col1, col2 = st.columns(2)
    with col1:
        asistencia = st.number_input("Asistencia (%)", 0, 100, 82)
        promedio = st.number_input("Promedio general", 1.0, 7.0, 5.2, step=0.1)
    with col2:
        edad = st.number_input("Edad del alumno", 5, 25, 14)
        genero = st.selectbox("Género", ["Masculino", "Femenino"])
    texto = None

# -----------------------------
# ⚙️ BOTÓN DE EJECUCIÓN
# -----------------------------
if st.button("🚀 Generar plan personalizado"):
    with st.spinner("Analizando información... ⏳"):
        try:
            # 🧩 Si se usa modo IA → procesar texto con extractor LLM
            if modo == "Texto libre (IA)" and texto:
                data = parse_nl_to_json_llm(texto)
                asistencia = data.get("ASISTENCIA", 85)
                promedio = data.get("PROM_GRAL", 5.0)
                edad = int(data.get("EDAD_ALU", 15))
                genero = "Masculino" if data.get("GEN_ALU", 1) == 1 else "Femenino"

            # 🧱 Crear perfil estructurado
            perfil = PerfilAlumno(
                asistencia=float(asistencia),
                promedio=float(promedio),
                edad=int(edad),
                genero=1 if genero == "Masculino" else 2
            )

            # 📊 Calcular riesgo de deserción
            nivel_riesgo, prob_riesgo = predecir_riesgo(asistencia, promedio, edad)

            # 🤖 Generar plan personalizado
            resultado = coach_plan(perfil)

            # -----------------------------
            # 🎯 RESULTADOS VISUALES
            # -----------------------------
            st.success("✅ Plan personalizado generado exitosamente.")

            # 🔥 Sección de riesgo con colores según nivel
            color = {"Bajo": "🟢", "Medio": "🟡", "Alto": "🔴"}.get(nivel_riesgo, "⚪")
            st.subheader("📊 Nivel de riesgo de deserción")
            st.markdown(f"""
            **Nivel:** {color} **{nivel_riesgo}**  
            **Probabilidad estimada:** {prob_riesgo * 100:.1f} %
            """)

            # -----------------------------
            # 🧾 Plan estructurado
            # -----------------------------
            st.subheader("📋 Plan de Acción Personalizado")

            # Reemplazar y formatear los checkboxes para mayor legibilidad
            plan_markdown = resultado["plan"].replace("- [ ]", "☑️")
            plan_markdown = re.sub(r"(☑️.*?)\s(?=☑️|$)", r"\1\n\n", plan_markdown)

            st.markdown(plan_markdown, unsafe_allow_html=True)

            # -----------------------------
            # 📚 Fuentes
            # -----------------------------
            st.subheader("📚 Fuentes consultadas")
            st.write(", ".join([f"📄 {src}" for src in resultado["fuentes"]]))

            # -----------------------------
            # ⚠️ Derivación
            # -----------------------------
            if resultado["guardrail_derivacion"]:
                st.warning("⚠️ Se recomienda derivación al Orientador Escolar.")
            else:
                st.info("💬 Sin necesidad de derivación por ahora.")

            st.divider()
            st.caption("Team 16 - Hackathon IA Duoc UC 2025")

        except Exception as e:
            st.error(f"❌ Error al generar el plan: {e}")
