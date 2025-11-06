import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

 st.set_page_config(page_title = "Tutor Virtual", layout = centered)
 
 def generar_pdf(plan_apoyo, score, drivers, citations):
    tmp = tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf")
    c = canvas.Canvas(tmp.name, pagesize = A4)
    w, h = A4

    y = h - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Tutor Virtual – Resumen")
    y -= 24

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Score: {score if isinstance(score, (int, float)) else '—'}")
    y -= 18

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Drivers:")
    y -= 16
    c.setFont("Helvetica", 10)
    if drivers:
        for d in drivers[:8]:
            c.drawString(50, y, f"• {d}")
            y -= 14
    else:
        c.drawString(50, y, "(sin drivers)")
        y -= 14

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Plan de apoyo:")
    y -= 16
    c.setFont("Helvetica", 10)
    for line in (plan_apoyo or "").split("\n"):
        c.drawString(50, y, line[:110])
        y -= 14
        if y < 60:
            c.showPage(); y = h - 60; c.setFont("Helvetica", 10)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Citas:")
    y -= 16
    c.setFont("Helvetica", 10)
    if citations:
        for ref in citations[:12]:
            c.drawString(50, y, f"• {ref}")
            y -= 14
            if y < 60:
                c.showPage(); y = h - 60; c.setFont("Helvetica", 10)
    else:
        c.drawString(50, y, "(sin citas)")
    c.save()
    return tmp.name