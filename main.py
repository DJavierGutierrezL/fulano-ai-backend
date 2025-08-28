# main.py - VERSIÓN CON PERSONALIDAD VENEZOLANA

import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuración de la API de Gemini ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error grave al configurar la API de Gemini: {e}")

# --- Configuración de la Aplicación FastAPI ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos Pydantic ---
class Message(BaseModel):
    id: str
    text: str
    sender: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] | None = None
    model_id: str | None = None

# --- Endpoint del Chat con Personalidad ---
@app.post("/chat")
def chat(request: ChatRequest):
    if not genai.api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado correctamente en el servidor.")
    
    try:
        # ==============================================================================
        # AQUÍ DEFINIMOS LA PERSONALIDAD VENEZOLANA
        # ==============================================================================
        
        # 1. INSTRUCCIÓN DE SISTEMA: Define la personalidad base y las reglas.
        system_instruction = """
        Eres un asistente virtual llamado 'Fulano', y tu personalidad está basada en Javier.
        Tu estilo de comunicación es amigable y pana, como si hablaras con un chamo.
        Usas algunas jergas venezolanas de vez en cuando (ej: 'chévere', 'mi pana','mamaguebo', 'qué fino', 'dale pues','tonto','becerro', 'gafo').
        Siempre respondes en español. Evita ser demasiado formal o robótico.
        Tu objetivo es ser útil y servicial, pero con un toque personal y cercano.
        """

        # 2. EJEMPLOS (FEW-SHOT): Le mostramos ejemplos para guiar su estilo.
        few_shot_examples = [
            {"role": "user", "parts": [{"text": "Hola, ¿quién eres?"}]},
            {"role": "model", "parts": [{"text": "¡Epa, mi pana! Soy Fulano, tu asistente virtual. ¿Todo fino? Dime en qué te puedo ayudar."}]},
            {"role": "user", "parts": [{"text": "Gracias por la ayuda"}]},
            {"role": "model", "parts": [{"text": "¡Chévere! Estamos a la orden. ¡Dale pues, cualquier otra cosa me avisas!"}]}
        ]

        # 3. CONSTRUCCIÓN DEL HISTORIAL: Unimos todo para darle el contexto completo a la IA.
        gemini_history = []
        
        if request.history:
            for msg in request.history:
                role = 'user' if msg.sender == 'user' else 'model'
                gemini_history.append({"role": role, "parts": [{"text": msg.text}]})
        
        final_history = few_shot_examples + gemini_history
        
        final_history.append({"role": "user", "parts": [{"text": request.message}]})

        # ==============================================================================
        # LLAMADA A LA API DE GEMINI CON TODO EL CONTEXTO
        # ==============================================================================
        
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=system_instruction
        )
        
        response = model.generate_content(final_history)
        
        return [{"generated_text": response.text}]
        
    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de IA: {e}")