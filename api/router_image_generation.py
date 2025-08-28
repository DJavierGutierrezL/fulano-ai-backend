# api/router_image_generation.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import os
import io

router = APIRouter()

class ImageRequest(BaseModel):
    prompt: str

@router.post("/generate-image")
def generate_image(request: ImageRequest):
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise HTTPException(status_code=500, detail="Token de Hugging Face no configurado.")
    
    # =================================================================
    # CAMBIO: Usaremos un modelo estándar de Stable Diffusion para la prueba
    # =================================================================
    model_id = "runwayml/stable-diffusion-v1-5"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        response = requests.post(
            api_url, 
            headers=headers, 
            json={"inputs": request.prompt},
            timeout=180 # Aumentamos la paciencia a 3 minutos
        )

        if response.status_code != 200:
            print(f"Error de Hugging Face: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return StreamingResponse(io.BytesIO(response.content), media_type=response.headers['Content-Type'])

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="El modelo de imágenes tardó demasiado en responder. Inténtalo de nuevo en un minuto.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))