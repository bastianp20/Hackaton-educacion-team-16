"""
derivacion.py — Lógica de derivación y alertas
"""

def evaluar_derivacion(asistencia: float, promedio: float) -> tuple[bool, str]:
    """
    Determina si el estudiante requiere derivación.
    Retorna (derivar, motivo)
    """
    derivar = False
    motivo = ""

    if asistencia < 85:
        derivar = True
        motivo += "Asistencia menor al 85%. "
    if promedio < 5.0:
        derivar = True
        motivo += "Promedio académico bajo (menor a 5.0). "

    if derivar:
        motivo = motivo.strip()
        motivo += " Se sugiere seguimiento con orientador escolar."
    return derivar, motivo
