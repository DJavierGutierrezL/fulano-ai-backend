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

    # Usaremos el modelo de Texto a Imagen que elegiste
    model_id = "prompthero/openjourney"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}

    try:
        response = requests.post(
            api_url, 
            headers=headers, 
            json={"inputs": request.prompt},
            timeout=120
        )

        if response.status_code != 200:
            print(f"Error de Hugging Face: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

        # Devolvemos la imagen directamente como una respuesta de streaming
        return StreamingResponse(io.BytesIO(response.content), media_type=response.headers['Content-Type'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))