# main.py - VERSIÓN CON CORRECCIÓN FINAL DE IMPORTACIÓN

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
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
marvel_public_key = os.getenv("MARVEL_PUBLIC_KEY")
marvel_private_key = os.getenv("MARVEL_PRIVATE_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- Definición de Herramientas ---
def get_current_time(timezone: str = "America/Caracas"):
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def get_weather(city: str):
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
    if not news_api_key: return {"error": "El servicio de noticias no está configurado"}
    try:
        url = f"https://newsapi.org/v2/top-headlines?q={query}&language=es&pageSize=5&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        headlines = [{"title": article["title"], "url": article["url"]} for article in data["articles"]]
        return {"headlines": headlines}
    except requests.exceptions.RequestException:
        return {"error": f"No se pudieron obtener noticias sobre {query}"}

def google_search(query: str):
    if not serper_api_key: return {"error": "El servicio de búsqueda no está configurado"}
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_api_key, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "answerBox" in data: return {"result": data["answerBox"].get("answer") or data["answerBox"].get("snippet")}
        if "organic" in data and len(data["organic"]) > 0: return {"result": data["organic"][0].get("snippet")}
        return {"result": "No se encontró una respuesta directa."}
    except requests.exceptions.RequestException:
        return {"error": f"La búsqueda de '{query}' falló."}

def translate_text(text: str, target_language: str, source_language: str = "auto"):
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"translated_text": data["responseData"]["translatedText"]}
    except requests.exceptions.RequestException:
        return {"error": "El servicio de traducción falló."}

def calculate(expression: str):
    try:
        aeval = Interpreter()
        result = aeval.eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": f"Expresión matemática inválida: {e}"}

def rerank_documents(query: str, documents: list[str]):
    if not cohere_api_key: return {"error": "El servicio de Re-ranking de Cohere no está configurado."}
    try:
        co = cohere.Client(cohere_api_key)
        response = co.rerank(model='rerank-multilingual-v3.0', query=query, documents=documents, top_n=3)
        ranked_results = [{"document": result.document['text']} for result in response.results]
        return {"ranked_results": ranked_results}
    except Exception as e:
        return {"error": f"El re-ranking de documentos con Cohere falló: {e}"}

def get_pokemon_info(pokemon_name: str):
    try:
        pokemon = pb.pokemon(pokemon_name.lower())
        types = [t.type.name for t in pokemon.types]
        info = { "name": pokemon.name.capitalize(), "pokedex_id": pokemon.id, "height": f"{pokemon.height / 10} m", "weight": f"{pokemon.weight / 10} kg", "types": types }
        return info
    except Exception:
        return {"error": f"No se encontró información para el Pokémon '{pokemon_name}'."}

def search_marvel_character(character_name: str):
    if not marvel_public_key or not marvel_private_key: return {"error": "El servicio de Marvel no está configurado."}
    try:
        ts = str(time.time())
        hash_string = ts + marvel_private_key + marvel_public_key
        hash_md5 = hashlib.md5(hash_string.encode()).hexdigest()
        url = f"http://gateway.marvel.com/v1/public/characters?nameStartsWith={character_name}&ts={ts}&apikey={marvel_public_key}&hash={hash_md5}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()["data"]["results"]
        if not data: return {"result": f"No se encontró ningún personaje llamado '{character_name}'."}
        character = data[0]
        return { "name": character["name"], "description": character["description"] or "No hay una descripción disponible.", "comics_available": character["comics"]["available"] }
    except Exception as e:
        return {"error": f"La búsqueda en Marvel falló: {e}"}

# --- Configuración y Endpoints de FastAPI ---
app = FastAPI(title="Asistente Virtual con Herramientas")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
class Message(BaseModel): id: str; text: str; sender: str
class ChatRequest(BaseModel): message: str; history: list[Message] | None = None
class ImageRequest(BaseModel): prompt: str

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not api_key: raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    
    try:
        system_instruction = "Eres un asistente virtual llamado 'Fulano', con personalidad venezolana..."
        
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=system_instruction,
            tools=[get_current_time, get_weather, get_news, google_search, translate_text, calculate, rerank_documents, get_pokemon_info, search_marvel_character]
        )
        
        history = [{"role": "user" if msg.sender == 'user' else "model", "parts": [{"text": msg.text}]} for msg in request.history] if request.history else []
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(request.message)
        
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            tool_name = function_call.name
            tool_args = {key: value for key, value in function_call.args.items()}
            tool_result = None
            
            if tool_name == "get_current_time": tool_result = get_current_time(**tool_args)
            elif tool_name == "get_weather": tool_result = get_weather(**tool_args)
            elif tool_name == "get_news": tool_result = get_news(**tool_args)
            elif tool_name == "google_search": tool_result = google_search(**tool_args)
            elif tool_name == "translate_text": tool_result = translate_text(**tool_args)
            elif tool_name == "calculate": tool_result = calculate(**tool_args)
            elif tool_name == "rerank_documents": tool_result = rerank_documents(**tool_args)
            elif tool_name == "get_pokemon_info": tool_result = get_pokemon_info(**tool_args)
            elif tool_name == "search_marvel_character": tool_result = search_marvel_character(**tool_args)
            
            # CORRECCIÓN: Enviamos el FunctionResponse directamente, sin el 'Part' manual
            response = chat_session.send_message(
                protos.FunctionResponse(name=tool_name, response=tool_result)
            )

        final_text = "".join(part.text for part in response.parts)
        return JSONResponse(content=[{"generated_text": final_text}])
        
    except Exception as e:
        print(f"Error en el endpoint de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    if not api_key: raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"Una imagen fotorrealista de alta calidad de: {request.prompt}"
        response = model.generate_content(prompt)
        
        image_data = response.parts[0].inline_data
        image_base64 = base64.b64encode(image_data.data).decode('utf-8')
        
        return JSONResponse(content={"image_base64": image_base64})
    except Exception as e:
        print(f"ERROR DETALLADO DE GENERACIÓN DE IMAGEN: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de imágenes: {e}")