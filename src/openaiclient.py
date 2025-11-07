from openai import OpenAI

#Reemplaza con tu clave de API de OpenAI
client = OpenAI(api_key="YOUR_API_KEY")

def generar_respuesta(prompt):
    """
    Envía un prompt al modelo de OpenAI y devuelve la respuesta generada.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "Eres un asistente educativo experto en análisis de riesgo de deserción."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

# Ejemplo de uso
if __name__ == "__main__":
    pregunta = "Explica cómo la IA puede ayudar a reducir la deserción estudiantil."
    print(generar_respuesta(pregunta))
