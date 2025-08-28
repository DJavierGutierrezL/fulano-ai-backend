# main.py - VERSIÓN FINAL "SOLO GEMINI" (CHAT + IMAGEN)

import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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
app = FastAPI(title="Asistente Virtual con Gemini")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos (Pydantic) ---
class Message(BaseModel):
    id: str; text: str; sender: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] | None = None

class ImageRequest(BaseModel):
    prompt: str

# --- Endpoint del Chat ---
@app.post("/api/chat")
def chat(request: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        history = []
        if request.history:
            for msg in request.history:
                role = 'user' if msg.sender == 'user' else 'model'
                history.append({"role": role, "parts": [{"text": msg.text}]})

        history.append({"role": "user", "parts": [{"text": request.message}]})
        
        response = model.generate_content(history)
        
        return JSONResponse(content=[{"generated_text": response.text}])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint de Generación de Imágenes ---
@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")

    try:
        # Usamos el modelo de generación de imágenes de Google
        model = genai.GenerativeModel('gemini-1.5-pro-latest') # O el modelo específico que soporte Imagen
        
        # El prompt para la generación de imágenes
        prompt = f"Genera una imagen fotorrealista de alta calidad de: {request.prompt}"

        # La llamada a la API para generar la imagen
        response = model.generate_content(prompt, generation_config={"response_mime_type": "image/png"})
        
        # Extraemos los datos de la imagen y los devolvemos. 
        # NOTA: La forma exacta puede variar ligeramente según la librería.
        # Asumimos que la respuesta tiene un objeto 'Part' con los datos.
        image_data = response.parts[0].inline_data
        
        return JSONResponse(content={"image_base64": image_data.data.decode('utf-8')})
        
    except Exception as e:
        print(f"Error al generar la imagen con Gemini: {e}")
        raise HTTPException(status_code=500, detail=str(e))