# main.py - VERSIÓN FINAL COMPLETA CON ENDPOINT /api/chat

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
# Crear tablas en BD al iniciar
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
def get_current_time(timezone: str = "America/Bogota"):
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def extract_city(text: str) -> str:
    # Busca nombres de ciudades en el texto
    match = re.search(
        r"\b(?:en|de|para)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)",
        text,
        re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    
    # Si no encuentra ciudad, ponemos Medellin como default
    return "Medellin"

def get_weather(city: str):
    if not weather_api_key: return {"error": "Servicio clima no configurado"}
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()
        return {"city": d["location"]["name"], "temperature": f"{d['current']['temp_c']}°C", "description": d["current"]["condition"]["text"]}
    except:
        return {"error": f"No se pudo obtener el clima para {city}"}

def get_news(query: str):
    if not gnews_api_key: return {"error": "Servicio noticias no configurado"}
    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=es&max=3&apikey={gnews_api_key}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()
        headlines = [{"title": art["title"], "url": art["url"]} for art in d.get("articles", [])]
        return {"headlines": headlines} if headlines else {"result": f"No hay noticias sobre {query}"}
    except:
        return {"error": f"No se pudieron obtener noticias sobre {query}"}

def google_search(query: str):
    if not serper_api_key: return {"error": "Servicio búsqueda no configurado"}
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_api_key, 'Content-Type': 'application/json'}
        r = requests.post(url, headers=headers, data=payload, timeout=10)
        r.raise_for_status()
        d = r.json()
        if "answerBox" in d: return {"result": d["answerBox"].get("answer") or d["answerBox"].get("snippet")}
        if "organic" in d and len(d["organic"]) > 0: return {"result": d["organic"][0].get("snippet")}
        return {"result": "No encontré respuesta directa."}
    except:
        return {"error": f"Búsqueda de '{query}' falló"}

def translate_text(text: str, target_language: str, source_language: str = "auto"):
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return {"translated_text": r.json()["responseData"]["translatedText"]}
    except:
        return {"error": "Error traducción"}

def calculate(expression: str):
    try:
        aeval = Interpreter()
        return {"result": aeval.eval(expression)}
    except Exception as e:
        return {"error": f"Expresión inválida: {e}"}

def rerank_documents(query: str, documents: list[str]):
    if not cohere_api_key: return {"error": "Re-ranking no configurado"}
    try:
        co = cohere.Client(cohere_api_key)
        resp = co.rerank(model='rerank-multilingual-v3.0', query=query, documents=documents, top_n=3)
        return {"ranked_results": [{"document": r.document['text']} for r in resp.results]}
    except Exception as e:
        return {"error": f"Re-ranking falló: {e}"}

def get_pokemon_info(pokemon_name: str):
    for attempt in range(3):
        try:
            pokemon = pb.pokemon(pokemon_name.lower())
            types = [t.type.name for t in pokemon.types]
            return {"name": pokemon.name.capitalize(), "pokedex_id": pokemon.id, "height": f"{pokemon.height/10} m", "weight": f"{pokemon.weight/10} kg", "types": types}
        except:
            time.sleep(1)
    return {"error": f"No se pudo obtener info de {pokemon_name}"}

def search_marvel_character(name: str):
    if not marvel_public_key or not marvel_private_key: return {"error": "Marvel no configurado"}
    try:
        ts = str(time.time())
        h = hashlib.md5((ts + marvel_private_key + marvel_public_key).encode()).hexdigest()
        url = f"http://gateway.marvel.com/v1/public/characters?nameStartsWith={name}&ts={ts}&apikey={marvel_public_key}&hash={h}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()["data"]["results"]
        if not data: return {"result": f"No encontré personaje '{name}'"}
        c = data[0]
        return {"name": c["name"], "description": c["description"] or "Sin descripción", "comics_available": c["comics"]["available"]}
    except Exception as e:
        return {"error": f"Marvel falló: {e}"}

def search_free_images(q: str):
    if not pexels_api_key: return {"error": "Pexels no configurado"}
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": pexels_api_key}
        params = {"query": q, "per_page": 3, "locale": "es-ES"}
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        return {"image_urls": [p.get("src", {}).get("medium") for p in photos]} if photos else {"result": f"No encontré imágenes para {q}"}
    except Exception as e:
        return {"error": f"Pexels falló: {e}"}

def search_wikipedia(topic: str):
    try:
        wiki = wikipediaapi.Wikipedia('es', user_agent='FulanoAI/1.0')
        page = wiki.page(topic)
        if not page.exists(): return {"error": f"No hay artículo '{topic}'"}
        return {"topic": topic, "summary": page.summary[:500] + "..."}
    except:
        return {"error": "Wikipedia falló"}

def tell_joke():
    try:
        r = requests.get("https://v2.jokeapi.dev/joke/Any?lang=es&type=single", timeout=10)
        r.raise_for_status()
        d = r.json()
        return {"joke": d.get("joke")}
    except:
        return {"error": "API chistes falló"}

def get_exchange_rate(base_currency: str = "USD", target_currency: str = "COP"):
    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()
        rate = d.get("rates", {}).get(target_currency)
        return {"base": base_currency, "target": target_currency, "rate": rate}
    except:
        return {"error": "Divisas falló"}

# --- Clasificador de Intenciones ---
def _collect_training_data():
    X, y = [], []
    for intent in INTENTS:
        for ex in intent.get("examples", []):
            X.append(ex.lower())
            y.append(intent["name"])
    return X, y

def make_intent_model():
    X, y = _collect_training_data()
    pipeline = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1,2))), ("clf", LogisticRegression(C=10, solver='liblinear'))])
    pipeline.fit(X, y)
    return pipeline

INTENT_CLASSIFIER = make_intent_model()
INTENT_RESPONSES = {i['name']: i.get('responses', []) for i in INTENTS}

def predict_intent(text: str):
    probs = INTENT_CLASSIFIER.predict_proba([text.lower()])[0]
    idx = probs.argmax()
    return INTENT_CLASSIFIER.classes_[idx] if probs[idx] > 0.7 else "fallback_to_gemini"

# --- FastAPI ---
app = FastAPI(title="Asistente Virtual Fulano")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ImageRequest(BaseModel):
    prompt: str

class FaceSwapRequest(BaseModel):
    source_image_url: str
    target_image_url: str

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    intent = predict_intent(request.message)
    response_text = ""

    if intent in ["saludo", "despedida", "agradecimiento", "chiste"]:
        response_text = random.choice(INTENT_RESPONSES[intent])

    elif intent == "hora":
        t = get_current_time()
        response_text = f"La hora es {t.get('time', 'desconocida')}."

    elif intent == "clima":
        city = extract_city(request.message)
        w = get_weather(city)
        response_text = f"En {w['city']} la temperatura es {w['temperature']} con {w['description']}." if "error" not in w else w["error"]

    else:
        try:
            conv = crud.get_or_create_conversation(db, request.conversation_id)
            crud.save_message(db, conv.id, "user", request.message)
            hist = [{"role": ("user" if m.sender == 'user' else "model"), "parts": [{"text": m.content}]} for m in crud.get_messages_by_conversation(db, conv.id)]
            model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction="Eres Fulano, un pana venezolano simpático.", tools=[get_current_time, get_weather])
            chat_session = model.start_chat(history=hist)
            r = chat_session.send_message(request.message)
            response_text = "".join(p.text for p in r.parts)
            crud.save_message(db, conv.id, "assistant", response_text)
            return {"generated_text": response_text, "conversation_id": conv.id, "intent": intent}
        except Exception as e:
            response_text = f"Error con Gemini: {e}"

    return {"generated_text": response_text, "conversation_id": request.conversation_id or "N/A", "intent": intent}
