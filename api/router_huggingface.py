# api/router_huggingface.py - VERSIÓN DE PRUEBA SIMPLIFICADA

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

router = APIRouter()

# --- Modelos de Datos (sin cambios) ---
class Message(BaseModel):
    id: str; text: str; sender: str

class HFChatRequest(BaseModel):
    message: str
    model_id: str
    history: list[Message] | None = None

# --- Endpoint de Hugging Face ---
@router.post("/chat/huggingface")
def chat_with_huggingface(request: HFChatRequest):
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise HTTPException(status_code=500, detail="Token de Hugging Face no configurado.")
    
    try:
        api_url = f"https://api-inference.huggingface.co/models/{request.model_id}"
        headers = {"Authorization": f"Bearer {hf_token}"}

        # =================================================================
        # CAMBIO CLAVE: IGNORAMOS EL HISTORIAL Y ENVIAMOS SOLO EL MENSAJE NUEVO
        # =================================================================
        payload = {
            "inputs": request.message,
            "parameters": {
                "return_full_text": False,
                # Añadimos un parámetro para evitar que el modelo se repita
                "repetition_penalty": 1.1 
            }
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
             # Imprimimos el error en los logs para tener más detalles
             print(f"Error de Hugging Face: {response.status_code} - {response.text}")
             raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="La solicitud al modelo de IA tardó demasiado en responder (timeout). Inténtalo de nuevo.")
    except Exception as e:
        print(f"Error inesperado en el enrutador de Hugging Face: {e}")
        raise HTTPException(status_code=500, detail=str(e))