# api/router_gemini.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os

router = APIRouter()

# --- Modelos de Datos ---
class Message(BaseModel):
    id: str; text: str; sender: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] | None = None

# --- Endpoint de Gemini ---
@router.post("/chat/gemini")
def chat_with_gemini(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key de Gemini no configurada.")
    
    try:
        genai.configure(api_key=api_key)

        system_instruction = """
        Eres un asistente virtual llamado 'Fulano', y tu personalidad está basada en Javier.
        Tu estilo de comunicación es amigable y pana, como si hablaras con un chamo.
        Usas algunas jergas venezolanas de vez en cuando (ej: 'chévere', 'mi pana', 'qué fino', 'dale pues').
        Siempre respondes en español. Evita ser demasiado formal o robótico.
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_instruction)

        history = []
        if request.history:
            for msg in request.history:
                role = 'user' if msg.sender == 'user' else 'model'
                history.append({"role": role, "parts": [{"text": msg.text}]})

        history.append({"role": "user", "parts": [{"text": request.message}]})
        
        response = model.generate_content(history)
        
        return [{"generated_text": response.text}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))