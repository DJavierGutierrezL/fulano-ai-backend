# main.py - VERSIÓN CORREGIDA (Clima, Personalidad, Imágenes)

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
weather_api_key = os.getenv("WEATHER_API_KEY") # Usamos la nueva variable
genai.configure(api_key=api_key)

# --- Definición de Herramientas ---

def get_current_time(timezone: str = "America/Caracas"): # Cambiado a zona horaria de Venezuela
    """Devuelve la hora actual en una zona horaria específica."""
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def get_weather(city: str):
    """Obtiene el clima actual para una ciudad específica usando WeatherAPI.com."""
    if not weather_api_key:
        return {"error": "El servicio del clima no está configurado"}
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = {
            "city": data["location"]["name"],
            "temperature": f"{data['current']['temp_c']}°C",
            "description": data["current"]["condition"]["text"]
        }
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

# --- Endpoint del Chat ---
@app.post("/api/chat")
def chat(request: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    
    try:
        # CORRECCIÓN DE PERSONALIDAD: Inyectamos la personalidad al inicio del historial
        system_prompt = {
            "role": "user",
            "parts": [{"text": """
            Quiero que actúes como un asistente virtual llamado 'Fulano', con personalidad venezolana.
            Tu estilo debe ser amigable y pana, como si hablaras con un chamo.
            Usa jergas como 'chévere', 'mi pana', 'qué fino', 'dale pues'.
            Evita ser robótico. Sé útil, pero con un toque personal y cercano.
            """}]
        }
        model_ack = {"role": "model", "parts": [{"text": "¡Chévere, mi pana! Entendido. Estoy listo para ayudar con ese estilo."}]}

        model = genai.GenerativeModel('gemini-1.5-pro-latest', tools=[get_current_time, get_weather])
        
        history = [system_prompt, model_ack]
        if request.history:
            for msg in request.history:
                role = 'user' if msg.sender == 'user' else 'model'
                history.append({"role": role, "parts": [{"text": msg.text}]})
        
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(request.message)
        
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            tool_name = function_call.name
            tool_args = {key: value for key, value in function_call.args.items()}
            
            tool_result = None
            if tool_name == "get_current_time":
                tool_result = get_current_time(**tool_args)
            elif tool_name == "get_weather":
                tool_result = get_weather(**tool_args)
            
            response = chat_session.send_message(
                genai.Part(function_response=genai.protos.FunctionResponse(name=tool_name, response={"result": tool_result}))
            )

        return JSONResponse(content=[{"generated_text": response.text}])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint de Generación de Imágenes ---
@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    try:
        model = genai.GenerativeModel('imagen-2')
        response = model.generate_content(request.prompt)
        # Asumiendo que la respuesta directa es una URL o datos de imagen
        # Este endpoint puede requerir ajustes según la respuesta exacta de la API
        # Vamos a devolver la respuesta cruda para depurar
        return JSONResponse(content={"raw_response": str(response)})
    except Exception as e:
        # Imprimimos el error detallado en los logs de Render
        print(f"ERROR DETALLADO DE GENERACIÓN DE IMAGEN: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de imágenes: {e}")