# main.py - VERSIÓN FINAL CON TODAS LAS HERRAMIENTAS

import os
import requests
from datetime import datetime
import pytz 
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json

# --- Configuración de APIs ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- Definición de Herramientas ---

def get_current_time(timezone: str = "America/Caracas"):
    """Devuelve la hora actual en una zona horaria específica."""
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def get_weather(city: str):
    """Obtiene el clima actual para una ciudad específica usando WeatherAPI.com."""
    if not weather_api_key: return {"error": "El servicio del clima no está configurado"}
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = { "city": data["location"]["name"], "temperature": f"{data['current']['temp_c']}°C", "description": data["current"]["condition"]["text"] }
        return weather
    except requests.exceptions.RequestException:
        return {"error": f"No se pudo obtener el clima para {city}"}

def get_news(query: str):
    """Busca las 3 noticias más recientes sobre un tema específico."""
    if not news_api_key: return {"error": "El servicio de noticias no está configurado"}
    try:
        url = f"https://newsapi.org/v2/top-headlines?q={query}&language=es&pageSize=3&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        headlines = [{"title": article["title"], "url": article["url"]} for article in data["articles"]]
        return {"headlines": headlines}
    except requests.exceptions.RequestException:
        return {"error": f"No se pudieron obtener noticias sobre {query}"}

def google_search(query: str):
    """Realiza una búsqueda en Google para obtener una respuesta rápida a una pregunta."""
    if not serper_api_key: return {"error": "El servicio de búsqueda no está configurado"}
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_api_key, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "answerBox" in data:
            return {"result": data["answerBox"].get("answer") or data["answerBox"].get("snippet")}
        if "organic" in data and len(data["organic"]) > 0:
            return {"result": data["organic"][0].get("snippet")}
        return {"result": "No se encontró una respuesta directa."}
    except requests.exceptions.RequestException:
        return {"error": f"La búsqueda de '{query}' falló."}

def translate_text(text: str, target_language: str, source_language: str = "auto"):
    """Traduce un texto de un idioma a otro."""
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"translated_text": data["responseData"]["translatedText"]}
    except requests.exceptions.RequestException:
        return {"error": "El servicio de traducción falló."}


# --- Configuración de FastAPI (sin cambios) ---
app = FastAPI(title="Asistente Virtual con Herramientas")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Modelos de Datos (sin cambios) ---
class Message(BaseModel):
    id: str; text: str; sender: str

class ChatRequest(BaseModel):
    message: str; history: list[Message] | None = None

# --- Endpoint del Chat (ACTUALIZADO CON TODAS LAS HERRAMIENTAS) ---
@app.post("/api/chat")
def chat(request: ChatRequest):
    if not api_key: raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    
    try:
        system_instruction = "Eres un asistente virtual llamado 'Fulano', con personalidad venezolana..." # Mantenemos la personalidad
        
        # Le presentamos TODAS las herramientas disponibles a Gemini
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=system_instruction,
            tools=[get_current_time, get_weather, get_news, google_search, translate_text]
        )
        
        history = []
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
            # Ejecutamos la herramienta que Gemini haya elegido
            if tool_name == "get_current_time": tool_result = get_current_time(**tool_args)
            elif tool_name == "get_weather": tool_result = get_weather(**tool_args)
            elif tool_name == "get_news": tool_result = get_news(**tool_args)
            elif tool_name == "google_search": tool_result = google_search(**tool_args)
            elif tool_name == "translate_text": tool_result = translate_text(**tool_args)
            
            response = chat_session.send_message(
                genai.Part(function_response=genai.protos.FunctionResponse(name=tool_name, response=tool_result))
            )

        final_text = "".join(part.text for part in response.parts)
        return JSONResponse(content=[{"generated_text": final_text}])
        
    except Exception as e:
        print(f"Error en el endpoint de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# El endpoint de generación de imágenes se mantiene igual, lo eliminamos de aquí por brevedad.
# Si quieres mantenerlo, solo copia y pega la función /api/generate-image del código anterior.