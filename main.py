# main.py - VERSIÓN DE DIAGNÓSTICO (CHAT SIMPLIFICADO)

import os
import requests
from datetime import datetime
import pytz 
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuración de APIs ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- Definición de Herramientas (las mantenemos para el futuro) ---
def get_current_time(timezone: str = "America/Caracas"):
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def get_weather(city: str):
    if not weather_api_key:
        return {"error": "El servicio del clima no está configurado"}
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = { "city": data["location"]["name"], "temperature": f"{data['current']['temp_c']}°C", "description": data["current"]["condition"]["text"] }
        return weather
    except requests.exceptions.RequestException as e:
        return {"error": f"No se pudo obtener el clima para {city}"}

# --- Configuración de FastAPI ---
app = FastAPI(title="Asistente Virtual con Herramientas")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos ---
class Message(BaseModel):
    id: str; text: str; sender: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] | None = None

class ImageRequest(BaseModel):
    prompt: str

# --- Endpoint del Chat (SIMPLIFICADO PARA LA PRUEBA) ---
@app.post("/api/chat")
def chat(request: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    
    try:
        # Usamos el modelo sin herramientas por ahora
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        history = []
        if request.history:
            for msg in request.history:
                role = 'user' if msg.sender == 'user' else 'model'
                history.append({"role": role, "parts": [{"text": msg.text}]})

        history.append({"role": "user", "parts": [{"text": request.message}]})
        
        # Hacemos una llamada simple, sin sesión ni herramientas
        response = model.generate_content(history)
        
        return JSONResponse(content=[{"generated_text": response.text}])
        
    except Exception as e:
        print(f"Error en el endpoint de chat simplificado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint de Generación de Imágenes (sin cambios) ---
@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    try:
        # Este endpoint puede necesitar ajustes, pero lo dejamos para diagnosticar el chat primero
        model = genai.GenerativeModel('imagen-2')
        response = model.generate_content(request.prompt)
        return JSONResponse(content={"raw_response": str(response)})
    except Exception as e:
        print(f"ERROR DETALLADO DE GENERACIÓN DE IMAGEN: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de imágenes: {e}")