# main.py - VERSIÓN FINAL CON FACE SWAP

import os
import requests
from datetime import datetime
import pytz 
import google.generativeai as genai
import google.generativeai.protos as protos
import cohere
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json
from asteval import Interpreter
import time
import hashlib
import pokebase as pb

# --- Configuración de APIs ---
# ... (todas tus claves de API existentes)
rapidapi_key = os.getenv("RAPIDAPI_KEY") # <-- NUEVA VARIABLE

# --- (Todas las funciones de herramientas existentes no cambian) ---
# ... (get_current_time, get_weather, get_pokemon_info, etc.)

# --- Configuración de FastAPI ---
app = FastAPI(title="Asistente Virtual con Herramientas")
# ... (Middleware y Modelos de Datos existentes)
class FaceSwapRequest(BaseModel):
    source_image_url: str
    target_image_url: str

# --- Endpoint del Chat (sin cambios) ---
@app.post("/api/chat")
def chat(request: ChatRequest):
    # ... (El código de tu chat con Gemini y sus herramientas no cambia)
    
# --- Endpoint de Generación de Imágenes (sin cambios) ---
@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    # ... (El código de generación de imágenes de Gemini no cambia)

# --- NUEVO ENDPOINT: FACE SWAP ---
@app.post("/api/face-swap")
def face_swap(request: FaceSwapRequest):
    if not rapidapi_key:
        raise HTTPException(status_code=500, detail="El servicio de RapidAPI no está configurado.")
    
    try:
        # 1. Descargar y codificar las imágenes a base64
        source_response = requests.get(request.source_image_url, timeout=20)
        source_response.raise_for_status()
        source_base64 = f"data:image/jpeg;base64,{base64.b64encode(source_response.content).decode('utf-8')}"

        target_response = requests.get(request.target_image_url, timeout=20)
        target_response.raise_for_status()
        target_base64 = f"data:image/jpeg;base64,{base64.b64encode(target_response.content).decode('utf-8')}"

        # 2. Configurar y llamar a la API de RapidAPI
        url = "https://deepfake-face-swap.p.rapidapi.com/swap"
        payload = {
            "source": source_base64,
            "target": target_base64
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "deepfake-face-swap.p.rapidapi.com"
        }

        api_response = requests.post(url, json=payload, headers=headers, timeout=120)
        api_response.raise_for_status()
        
        data = api_response.json()
        # La respuesta contiene la imagen en base64, la extraemos
        result_base64 = data.get("image")
        if not result_base64:
             raise HTTPException(status_code=500, detail="La API de face swap no devolvió una imagen.")

        return JSONResponse(content={"image_base64": result_base64.split(',')[1]}) # Quitamos el prefijo 'data:...'

    except Exception as e:
        print(f"ERROR DETALLADO DE FACE SWAP: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de face swap: {e}")