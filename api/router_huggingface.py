# api/router_huggingface.py - VERSIÓN FINAL CON REPLICATE

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import replicate
import os

router = APIRouter()

# --- Modelos de Datos ---
class Message(BaseModel):
    id: str; text: str; sender: str

class HFChatRequest(BaseModel):
    message: str
    model_id: str # Aquí irá el ID del modelo en Replicate
    history: list[Message] | None = None

# --- Endpoint de Replicate ---
@router.post("/chat/huggingface")
def chat_with_replicate(request: HFChatRequest):
    # La librería de Replicate leerá el token automáticamente de las variables de entorno
    if not os.getenv("REPLICATE_API_TOKEN"):
        raise HTTPException(status_code=500, detail="Token de Replicate no configurado.")
    
    try:
        # Formateamos el historial y el mensaje en un solo prompt
        prompt = ""
        if request.history:
            for msg in request.history:
                role = "User" if msg.sender == 'user' else "Assistant"
                prompt += f"{role}: {msg.text}\n"
        prompt += f"User: {request.message}\nAssistant:"

        # Hacemos la llamada a Replicate
        output = replicate.run(
            request.model_id,
            input={"prompt": prompt}
        )
        
        # La respuesta de Replicate es un generador, así que unimos las partes
        full_response = "".join(output)
        
        # Devolvemos la respuesta en el formato que nuestro frontend espera
        return [{"generated_text": full_response}]
        
    except Exception as e:
        print(f"Error al llamar a la API de Replicate: {e}")
        raise HTTPException(status_code=500, detail=str(e))