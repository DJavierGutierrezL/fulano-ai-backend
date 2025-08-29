# main.py - VERSIÓN FINAL CON BÚSQUEDA DE IMÁGENES GRATUITAS

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
# ... (otras keys) ...
rapidapi_key = os.getenv("RAPIDAPI_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- (Las herramientas existentes no cambian, se omiten por brevedad) ---
def get_current_time(timezone: str = "America/Caracas"):
    # ...
# ... y las demás ...

# --- NUEVA HERRAMIENTA: Búsqueda de Imágenes Gratuitas ---
def search_free_images(search_query: str):
    """
    Busca imágenes gratuitas y sin derechos de autor sobre un tema específico.
    """
    if not rapidapi_key:
        return {"error": "El servicio de búsqueda de imágenes no está configurado."}
    
    # La API usa el término de búsqueda directamente en la URL (Path Param)
    url = f"https://free-images-api.p.rapidapi.com/v1/search"
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "free-images-api.p.rapidapi.com"
    }
    
    params = {
        "query": search_query
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get("results", [])
        if not data:
            return {"result": f"No se encontraron imágenes gratuitas para '{search_query}'."}
        
        # Extraemos las URLs de las primeras 3 imágenes
        image_urls = [img.get("url") for img in data[:3]]
        
        return {"image_urls": image_urls}
        
    except Exception as e:
        return {"error": f"La búsqueda de imágenes falló: {e}"}


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
            tools=[get_current_time, get_weather, get_news, google_search, translate_text, calculate, rerank_documents, get_pokemon_info, search_marvel_character, search_free_images]
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
            elif tool_name == "search_free_images": tool_result = search_free_images(**tool_args)
            
            response = chat_session.send_message(
                protos.FunctionResponse(name=tool_name, response=tool_result)
            )

        final_text = "".join(part.text for part in response.parts)
        return JSONResponse(content=[{"generated_text": final_text}])
        
    except Exception as e:
        print(f"Error en el endpoint de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ... (El endpoint de /api/generate-image no cambia)