# 🎓 Desafío Educación – Tutor Virtual Adaptativo con IA Híbrida

La educación siempre ha sido un espacio donde la tecnología puede marcar una gran diferencia. Este proyecto nace con una idea simple pero poderosa: **apoyar a estudiantes en riesgo de deserción mediante inteligencia artificial**, de una forma ética, empática y verdaderamente útil.

El desafío consiste en construir un **Tutor Virtual Adaptativo**, una herramienta impulsada por IA capaz de **detectar brechas de aprendizaje**, **predecir el riesgo de abandono** y **generar recomendaciones personalizadas** que acompañen a cada estudiante según su situación particular.

---

## 🧭 ¿De qué trata el proyecto?

La misión es diseñar un sistema que combine lo mejor de dos mundos:

1. **Machine Learning (IA tradicional)** para analizar datos educativos, detectar patrones y calcular el nivel de riesgo de deserción.
2. **Modelos de Lenguaje (IA generativa)** para interpretar, explicar y comunicar los resultados en un lenguaje claro, cercano y motivador.

En conjunto, forman una **IA híbrida** que no solo predice, sino que también **entiende y acompaña**.

El sistema debe recibir información de cada estudiante (como su edad, rendimiento, tipo de establecimiento, asignaturas y asistencia) y, con base en eso, realizar tres tareas esenciales:

1. **Calcular el riesgo de deserción**: generar un puntaje entre 0 y 1 que indique la probabilidad de abandono.
2. **Explicar el resultado**: mostrar de forma comprensible qué factores influyeron en ese riesgo.
3. **Sugerir un plan de acción personalizado**: entregar consejos concretos y realistas que ayuden a mejorar el rendimiento o el compromiso académico.

---

## 🧠 La arquitectura híbrida

El proyecto se construye sobre una arquitectura modular que combina algoritmos de predicción con modelos de lenguaje. En términos simples, se compone de cinco grandes piezas:

| Componente | Función | Descripción breve |
| :-- | :-- | :-- |
| **1. Motor de riesgo (ML tabular)** | Predice el riesgo de deserción. | Usa modelos como *Logistic Regression* o *XGBoost* para calcular el puntaje de riesgo, aplicando validación temporal y evitando fuga de datos. |
| **2. Extractor NL→JSON (LLM)** | Interpreta lenguaje natural. | Convierte texto libre en datos estructurados; por ejemplo, “soy estudiante de 16 años con promedio 5.1” se traduce a un JSON con edad, notas y asistencia. |
| **3. Coach (LLM + RAG)** | Genera el plan de acción. | Crea recomendaciones personalizadas basadas en una pequeña base de conocimiento local (/kb), asegurando que las respuestas estén respaldadas y sean útiles. |
| **4. Guardrails & Safety** | Cuida el lenguaje y la ética. | Asegura que las respuestas sean respetuosas, inclusivas y sin diagnósticos inapropiados. También deriva casos críticos al equipo de apoyo. |
| **5. App & API** | Conecta todo en una demo interactiva. | Usa *FastAPI* para el backend (/predict y /coach) y *Streamlit* o *Gradio* para la interfaz visual del tutor. |

---

## 💡 Qué hace único a este tutor virtual

El verdadero valor de este proyecto está en su enfoque humano. No se trata solo de calcular probabilidades, sino de **dar sentido a los datos educativos** y ofrecer una **respuesta empática y constructiva**.

Este tutor no “etiqueta” estudiantes, sino que **detecta oportunidades de apoyo** y sugiere acciones realistas como reforzamiento académico, orientación o hábitos de estudio.

Además, la arquitectura fue pensada para ser **abierta y escalable**: puede integrarse en plataformas educativas, usarse como asistente docente o servir de apoyo para orientadores y equipos psicoeducativos.

---

## 📂 Estructura del proyecto

El repositorio está organizado para mantener la lógica del flujo de datos y el procesamiento por módulos:

