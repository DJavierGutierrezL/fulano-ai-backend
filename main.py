# main.py - VERSIÓN FINAL, COMPLETA Y VERIFICADA

import os
import re
import requests
from datetime import datetime
import pytz 
import google.generativeai as genai
import google.generativeai.protos as protos
import cohere
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json
from asteval import Interpreter
import time
import hashlib
import pokebase as pb
import wikipediaapi
import random
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sqlalchemy.orm import Session

# Importaciones locales
from intents import INTENTS
import models, crud, database
from database import get_db, engine

# Crea las tablas en la base de datos si no existen al iniciar la app
models.Base.metadata.create_all(bind=database.engine)

# --- Configuración de APIs ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
gnews_api_key = os.getenv("GNEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
marvel_public_key = os.getenv("MARVEL_PUBLIC_KEY")
marvel_private_key = os.getenv("MARVEL_PRIVATE_KEY")
pexels_api_key = os.getenv("PEXELS_API_KEY")
rapidapi_key = os.getenv("RAPIDAPI_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- Herramientas ---
def get_current_time(timezone: str = "America/Caracas"):
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def extract_city(text: str) -> str:
    match = re.search(r"\b(en|de|para)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)", text)
    if match:
        return match.group(2).strip()
    return "Caracas" 

def get_weather(city: str):
    if not weather_api_key: return {"error": "El servicio del clima no está configurado"}
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["location"]["name"],
            "temperature": f"{data['current']['temp_c']}°C",
            "description": data["current"]["condition"]["text"]
        }
    except requests.exceptions.RequestException:
        return {"error": f"No se pudo obtener el clima para {city}"}

def get_news(query: str):
    if not gnews_api_key: return {"error": "El servicio de noticias no está configurado"}
    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=es&max=3&apikey={gnews_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        headlines = [{"title": a["title"], "url": a["url"]} for a in data.get("articles", [])]
        if not headlines: return {"result": f"No se encontraron noticias sobre '{query}'."}
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
        if "answerBox" in data:
            return {"result": data["answerBox"].get("answer") or data["answerBox"].get("snippet")}
        if "organic" in data and len(data["organic"]) > 0:
            return {"result": data["organic"][0].get("snippet")}
        return {"result": "No se encontró una respuesta directa."}
    except requests.exceptions.RequestException:
        return {"error": f"La búsqueda de '{query}' falló."}

def translate_text(text: str, target_language: str, source_language: str = "auto"):
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {"translated_text": response.json()["responseData"]["translatedText"]}
    except requests.exceptions.RequestException:
        return {"error": "El servicio de traducción falló."}

def calculate(expression: str):
    try:
        aeval = Interpreter()
        return {"result": aeval.eval(expression)}
    except Exception as e:
        return {"error": f"Expresión matemática inválida: {e}"}

def rerank_documents(query: str, documents: list[str]):
    if not cohere_api_key: return {"error": "El servicio de Re-ranking de Cohere no está configurado."}
    try:
        co = cohere.Client(cohere_api_key)
        response = co.rerank(model='rerank-multilingual-v3.0', query=query, documents=documents, top_n=3)
        return {"ranked_results": [{"document": r.document['text']} for r in response.results]}
    except Exception as e:
        return {"error": f"El re-ranking de documentos con Cohere falló: {e}"}

def get_pokemon_info(pokemon_name: str):
    for attempt in range(3):
        try:
            pokemon = pb.pokemon(pokemon_name.lower())
            types = [t.type.name for t in pokemon.types]
            return {
                "name": pokemon.name.capitalize(),
                "pokedex_id": pokemon.id,
                "height": f"{pokemon.height / 10} m",
                "weight": f"{pokemon.weight / 10} kg",
                "types": types
            }
        except Exception as e:
            print(f"Intento {attempt+1} falló: {e}")
            time.sleep(1)
    return {"error": f"No se pudo contactar la PokéAPI para '{pokemon_name}'."}

def search_marvel_character(character_name: str):
    if not marvel_public_key or not marvel_private_key:
        return {"error": "El servicio de Marvel no está configurado."}
    try:
        ts = str(time.time())
        hash_md5 = hashlib.md5((ts + marvel_private_key + marvel_public_key).encode()).hexdigest()
        url = f"http://gateway.marvel.com/v1/public/characters?nameStartsWith={character_name}&ts={ts}&apikey={marvel_public_key}&hash={hash_md5}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()["data"]["results"]
        if not data: return {"result": f"No se encontró ningún personaje '{character_name}'."}
        c = data[0]
        return {"name": c["name"], "description": c["description"] or "No hay descripción.", "comics_available": c["comics"]["available"]}
    except Exception as e:
        return {"error": f"La búsqueda en Marvel falló: {e}"}

def search_free_images(search_query: str):
    if not pexels_api_key: return {"error": "El servicio de Pexels no está configurado."}
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": pexels_api_key}
        params = {"query": search_query, "per_page": 3, "locale": "es-ES"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get("photos", [])
        if not data: return {"result": f"No se encontraron imágenes para '{search_query}'."}
        return {"image_urls": [p.get("src", {}).get("medium") for p in data]}
    except Exception as e:
        return {"error": f"La búsqueda de imágenes falló: {e}"}

def search_wikipedia(topic: str):
    try:
        wiki = wikipediaapi.Wikipedia('es', user_agent='FulanoAI/1.0')
        page = wiki.page(topic)
        if not page.exists(): return {"error": f"No encontré Wikipedia para '{topic}'."}
        return {"topic": topic, "summary": f"{page.summary[0:500]}..."}
    except Exception as e:
        return {"error": f"Wikipedia falló: {e}"}

def tell_joke():
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?lang=es&type=single", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("error"): return {"error": "No se pudo obtener un chiste."}
        return {"joke": data.get("joke")}
    except Exception as e:
        return {"error": f"API de chistes falló: {e}"}

def get_exchange_rate(base_currency: str = "USD", target_currency: str = "COP"):
    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = data.get("rates", {}).get(target_currency.upper())
        if not rate: return {"error": f"No se encontró la tasa de {target_currency.upper()}."}
        return {"base": base_currency.upper(), "target": target_currency.upper(), "rate": rate}
    except Exception as e:
        return {"error": f"La consulta de divisas falló: {e}"}

# --- Clasificador de Intenciones ---
def _collect_training_data():
    X, y = [], []
    for intent in INTENTS:
        if "examples" in intent:
            for ex in intent["examples"]:
                X.append(ex.lower())
                y.append(intent["name"])
    return X, y

def make_intent_model():
    X, y = _collect_training_data()
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(C=10, solver='liblinear')),
    ])
    pipeline.fit(X, y)
    return pipeline

INTENT_CLASSIFIER = make_intent_model()
INTENT_RESPONSES = {i['name']: i.get('responses', []) for i in INTENTS}

def predict_intent(text: str):
    predictions = INTENT_CLASSIFIER.predict_proba([text.lower()])[0]
    max_idx = predictions.argmax()
    if predictions[max_idx] > 0.7:
        return INTENT_CLASSIFIER.classes_[max_idx]
    return "fallback_to_gemini"

# --- FastAPI ---
app = FastAPI(title="Asistente Virtual con Base de Datos")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PydanticMessage(BaseModel):
    id: str
    text: str
    sender: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ImageRequest(BaseModel):
    prompt: str

class FaceSwapRequest(BaseModel):
    source_image_url: str
    target_image_url: str

# --- Endpoints ---
@app.get("/api/history/{conversation_id}", response_model=list[PydanticMessage])
def get_history(conversation_id: str, db: Session = Depends(database.get_db)):
    db_messages = crud.get_messages_by_conversation(db, conversation_id=conversation_id)
    return [{"id": m.id, "text": m.content, "sender": m.sender} for m in db_messages]

@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    if not api_key: raise HTTPException(status_code=500, detail="Gemini no está configurado.")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"Una imagen fotorrealista de: {request.prompt}"
        response = model.generate_content(prompt)
        image_data = response.parts[0].inline_data
        image_base64 = base64.b64encode(image_data.data).decode('utf-8')
        return JSONResponse(content={"image_base64": image_base64})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en imágenes: {e}")

@app.post("/api/face-swap")
def face_swap(request: FaceSwapRequest):
    if not rapidapi_key: raise HTTPException(status_code=500, detail="RapidAPI no está configurado.")
    try:
        source_b64 = base64.b64encode(requests.get(request.source_image_url, timeout=20).content).decode('utf-8')
        target_b64 = base64.b64encode(requests.get(request.target_image_url, timeout=20).content).decode('utf-8')
        payload = {"source": f"data:image/jpeg;base64,{source_b64}", "target": f"data:image/jpeg;base64,{target_b64}"}
        headers = {"content-type": "application/json", "X-RapidAPI-Key": rapidapi_key, "X-RapidAPI-Host": "deepfake-face-swap.p.rapidapi.com"}
        api_response = requests.post("https://deepfake-face-swap.p.rapidapi.com/swap", json=payload, headers=headers, timeout=120)
        api_response.raise_for_status()
        data = api_response.json()
        result_base64 = data.get("image")
        if not result_base64: raise HTTPException(status_code=500, detail="Face swap no devolvió imagen.")
        return JSONResponse(content={"image_base64": result_base64.split(',')[1]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en face swap: {e}")
