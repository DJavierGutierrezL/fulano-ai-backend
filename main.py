# main.py - VERSIÓN CON HERRAMIENTA DE CLIMA HISTÓRICO (METEOSTAT)

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

# --- (El inicio del archivo y las variables de API no cambian) ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
marvel_public_key = os.getenv("MARVEL_PUBLIC_KEY")
marvel_private_key = os.getenv("MARVEL_PRIVATE_KEY")
rapidapi_key = os.getenv("RAPIDAPI_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- (Las herramientas existentes no cambian, se omiten por brevedad) ---
def get_current_time(timezone: str = "America/Caracas"):
    # ...
def get_weather(city: str):
    # ...
# ... y las demás ...

# --- NUEVA HERRAMIENTA: Clima Histórico con Meteostat ---
def get_historical_weather(latitude: float, longitude: float, start_date: str, end_date: str):
    """
    Obtiene datos climáticos históricos (mensuales) para un punto geográfico (latitud y longitud)
    dentro de un rango de fechas. Las fechas deben estar en formato YYYY-MM-DD.
    """
    if not rapidapi_key:
        return {"error": "El servicio de Meteostat no está configurado."}
    
    # Usaremos el endpoint de datos mensuales que se muestra en tu captura
    url = "https://meteostat.p.rapidapi.com/point/monthly"
    
    querystring = {
        "lat": str(latitude),
        "lon": str(longitude),
        "start": start_date,
        "end": end_date
    }
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json().get("data", [])
        if not data:
            return {"result": "No se encontraron datos para ese período o ubicación."}
        
        # Procesamos los datos para dar un resumen
        summary = []
        for month_data in data:
            summary.append(f"Mes: {month_data['month']}, Temp. Media: {month_data['tavg']}°C, Precipitación: {month_data['prcp']}mm")
        
        return {"summary": ", ".join(summary)}
        
    except Exception as e:
        return {"error": f"La consulta a Meteostat falló: {e}"}


# --- (El resto de la app FastAPI no cambia, solo actualizamos la lista de herramientas) ---
app = FastAPI(title="Asistente Virtual con Herramientas")
# ... (Middleware y Modelos de Datos)

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not api_key: raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    
    try:
        system_instruction = "Eres un asistente virtual llamado 'Fulano', con personalidad venezolana..."
        
        # AÑADIMOS LA NUEVA HERRAMIENTA A LA LISTA DE GEMINI
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=system_instruction,
            tools=[get_current_time, get_weather, get_news, google_search, translate_text, calculate, rerank_documents, get_pokemon_info, search_marvel_character, get_historical_weather]
        )
        
        history = [{"role": "user" if msg.sender == 'user' else "model", "parts": [{"text": msg.text}]} for msg in request.history] if request.history else []
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(request.message)
        
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            tool_name = function_call.name
            tool_args = {key: value for key, value in function_call.args.items()}
            tool_result = None
            
            # AÑADIMOS LA LÓGICA PARA EJECUTAR LA NUEVA HERRAMIENTA
            if tool_name == "get_current_time": tool_result = get_current_time(**tool_args)
            # ... (elif para las otras herramientas)
            elif tool_name == "search_marvel_character": tool_result = search_marvel_character(**tool_args)
            elif tool_name == "get_historical_weather": tool_result = get_historical_weather(**tool_args)
            
            response = chat_session.send_message(
                protos.FunctionResponse(name=tool_name, response=tool_result)
            )

        final_text = "".join(part.text for part in response.parts)
        return JSONResponse(content=[{"generated_text": final_text}])
        
    except Exception as e:
        print(f"Error en el endpoint de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ... (El endpoint de /api/generate-image no cambia)