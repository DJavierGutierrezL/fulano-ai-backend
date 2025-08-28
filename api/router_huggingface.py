# api/router_huggingface.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

router = APIRouter()

# --- Modelos de Datos ---
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
        
        # Formateamos el historial para que los modelos Instruct lo entiendan mejor
        prompt = ""
        if request.history:
            for msg in request.history:
                role = "User" if msg.sender == 'user' else "Assistant"
                prompt += f"{role}: {msg.text}\n"
        prompt += f"User: {request.message}\nAssistant:"

        payload = {"inputs": prompt, "parameters": {"return_full_text": False}}
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code != 200:
             raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))