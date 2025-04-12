import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables desde el .env
load_dotenv()

# Obtener la clave API
LLM_API = os.getenv("LLM_API")
if LLM_API:
    genai.configure(api_key=LLM_API)
    
model = genai.GenerativeModel('gemini-1.5-flash')

def generar_flashcards(texto):
    prompt = (
        "Generate flashcards strictly in the following format:\n"
        "'question1:answer1$question2:answer2$question3:answer3'.\n\n"
        "Do not add explanations, headers, or any other text.\n"
        "Here is the information to generate flashcards from.\n"
        "If there is not enough information to create flashcards, return nothing (black string):\n\n"
        f"{texto}"
    )
    
    response = model.generate_content(prompt).text.replace('*', '').strip()
    if not response or ':' not in response or '$' not in response:
        return []

    if ':' not in response or '$' not in response:
        raise ValueError(f"Formato incorrecto: {response}")

    flash = []
    for r in response.split('$'):
        parts = r.split(':', 1)  
        if len(parts) == 2:
            flash.append({'question': parts[0].strip(), 'answer': parts[1].strip()})
        else:
            raise ValueError(f"Entrada malformada: {r}")

    return flash
