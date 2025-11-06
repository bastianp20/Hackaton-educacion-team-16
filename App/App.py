
import tempfile
from typing import List

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Tutor Virtual", layout="centered")

def generar_pdf(
    nombre: str,
    edad: int,
    sexo: str,
    curso: str,
    establecimiento: str,
    asignatura: str,
    asistencia: double,
    promedio: float,
    notas_libres: str,
    score: float,
    drivers: List[str],
    citations: List[str],
    plan_apoyo: str,
)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)
    w, h = A4

    y = h - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Tutor Virtual – Resumen del Caso")
    y -= 22


    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Datos del perfil"); y -= 16
    c.setFont("Helvetica", 10)
    for linea in [
        f"Nombre: {nombre or '—'}",
        f"Edad: {edad if edad else '—'}    Sexo: {sexo or '—'}    Curso: {curso or '—'}",
        f"Establecimiento: {establecimiento or '—'}",
        f"Asignatura: {asignatura or '—'}    Asistencia: {asistencia}%    Promedio: {promedio}",
    ]:
        c.drawString(50, y, linea); y -= 14


    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Notas libres"); y -= 16
    c.setFont("Helvetica", 10)
    for linea in (notas_libres or "(sin notas)").split("\n"):
        c.drawString(50, y, linea[:110]); y -= 14
        if y < 60: c.showPage(); y = h - 60; c.setFont("Helvetica", 10)


    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Resultado de riesgo"); y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Score (0–1): {score:.3f}" if isinstance(score, (int, float)) else "Score: —"); y -= 14
    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Drivers"); y -= 16
    c.setFont("Helvetica", 10)
    if drivers:
        for d in drivers[:10]:
            c.drawString(50, y, f"• {d}"); y -= 14
            if y < 60: c.showPage(); y = h - 60; c.setFont("Helvetica", 10)
    else:
        c.drawString(50, y, "(sin drivers)"); y -= 14


    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Plan de apoyo"); y -= 16
    c.setFont("Helvetica", 10)
    for linea in (plan_apoyo or "(sin plan)").split("\n"):
        c.drawString(50, y, linea[:110]); y -= 14
        if y < 60: c.showPage(); y = h - 60; c.setFont("Helvetica", 10)


    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Citas / fuentes"); y -= 16
    c.setFont("Helvetica", 10)
    if citations:
        for ref in citations[:12]:
            c.drawString(50, y, f"• {ref}"); y -= 14
            if y < 60: c.showPage(); y = h - 60; c.setFont("Helvetica", 10)
    else:
        c.drawString(50, y, "(sin citas)")

    c.save()
    return tmp.name



st.title("Tutor Virtual_Ingreso de Datos")

with st.form("form_tutor"):
    st.subheader("Datos del perfil")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre / Identificador", "")
        edad = st.number_input("Edad", min_value=5, max_value=100, value=16)
        sexo = st.selectbox("Sexo", ["F", "M", "Otro/Prefiero no decir"], index=0)
        curso = st.text_input("Curso/Grado", "2° Medio")
    with col2:
        establecimiento = st.text_input("Establecimiento", "")
        asignatura = st.text_input("Asignatura principal", "Matemáticas")
        asistencia = st.slider("Asistencia (%)", 0, 100, 85)
        promedio = st.slider("Promedio (1.0–7.0)", 1.0, 7.0, 5.0, step=0.1)

    st.subheader("Observaciones")
    notas_libres = st.text_area(
        "Notas (texto libre)",
        "Dificultad con álgebra, se distrae en clase, apoyo en casa limitado."
    )

    st.subheader("Resultado y recomendaciones")
    score = st.slider("Score de riesgo (0–1)", 0.0, 1.0, 0.45, step=0.01)
    drivers_text = st.text_input("Drivers (separados por coma)", "Baja asistencia,Dificultad en matemáticas")
    citations_text = st.text_input("Citas / fuentes (coma)", "kb: guia_aprendizaje,kb: estrategias_matematicas")
    plan_apoyo = st.text_area("Plan de apoyo", "1) Tutorias semanales.\n2) Refuerzo en álgebra.\n3) Coordinación con apoderado.")

    enviado = st.form_submit_button("Generar PDF")

if enviado:
    drivers = [d.strip() for d in drivers_text.split(",") if d.strip()]
    citations = [c.strip() for c in citations_text.split(",") if c.strip()]

    pdf_path = generar_pdf(
        nombre, edad, sexo, curso, establecimiento, asignatura,
        asistencia, promedio, notas_libres, score, drivers, citations, plan_apoyo
    )

    st.success("PDF generado. Puedes descargarlo aquí:")
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Descargar PDF",
            data=f,
            file_name=f"tutor_virtual_{nombre or 'resumen'}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.subheader("Vista previa")
    st.write(f"**Score:** {score:.3f}")
    st.write("**Drivers:**", ", ".join(drivers) if drivers else "(sin drivers)")
    st.write("**Citas:**", ", ".join(citations) if citations else "(sin citas)")
