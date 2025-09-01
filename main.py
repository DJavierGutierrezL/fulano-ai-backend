# main.py - VERSIÓN FINAL HÍBRIDA + BASE DE DATOS

import os
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
from intents import INTENTS
import models, crud, database

# Crear tablas en la DB
models.Base.metadata.create_all(bind=database.engine)

# --- Configuración de APIs (sin cambios previos) ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
gnews_api_key = os.getenv("GNEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
marvel_public_key = os.getenv("MARVEL_PUBLIC_KEY")
marvel_private_key = os.getenv("MARVEL_PRIVATE_KEY")
pexels_api_key = os.getenv("PEXELS_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- TODAS LAS FUNCIONES DE HERRAMIENTAS AQUÍ (get_weather, get_news, etc.) ---
# (se mantienen tal cual las que ya tienes arriba)

# --- LÓGICA DEL CLASIFICADOR DE INTENCIONES ---
def _collect_training_data():
    X, y = [], []
    for intent in INTENTS:
        if "examples" in intent:
            for example in intent["examples"]:
                X.append(example.lower())
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
INTENT_RESPONSES = {intent['name']: intent.get('responses', []) for intent in INTENTS}

def predict_intent(text: str):
    predictions = INTENT_CLASSIFIER.predict_proba([text.lower()])[0]
    max_proba_index = predictions.argmax()
    if predictions[max_proba_index] > 0.7:
        return INTENT_CLASSIFIER.classes_[max_proba_index]
    return "fallback_to_gemini"

# --- Configuración de FastAPI ---
app = FastAPI(title="Asistente Virtual con DB")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Modelos de Datos ---
class Message(BaseModel): 
    id: str
    text: str
    sender: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] | None = None
    conversation_id: str | None = None

class ImageRequest(BaseModel):
    prompt: str

# --- ENDPOINT DEL CHAT (CON DB) ---
@app.post("/api/chat")
def chat(request: ChatRequest, db: Session = Depends(database.get_db)):
    # 1. Obtenemos o creamos la conversación
    conversation = crud.get_or_create_conversation(db, conversation_id=request.conversation_id)

    # 2. Guardamos el mensaje del usuario
    crud.create_message(db, conversation=conversation, sender='user', content=request.message)

    # 3. Clasificamos la intención
    intent = predict_intent(request.message)
    response_text = ""
    handled_by_gemini = False

    # 4. Si es intención simple, la respondemos localmente
    if intent in ["saludo", "despedida", "agradecimiento"]:
        response_text = random.choice(INTENT_RESPONSES[intent])
    elif intent == "hora":
        time_data = get_current_time()
        response_text = f"¡Claro! La hora es {time_data.get('time', 'desconocida')}."
    elif intent == "chiste":
        joke_data = tell_joke()
        response_text = joke_data.get('joke', 'Hoy no estoy de humor para chistes.')
    else:
        # 5. Si no, usamos Gemini
        handled_by_gemini = True
        try:
            all_tools = [
                get_current_time, get_weather, get_news, google_search, translate_text, 
                calculate, rerank_documents, get_pokemon_info, search_marvel_character, 
                search_free_images, search_wikipedia, tell_joke, get_exchange_rate
            ]

            model = genai.GenerativeModel(
                'gemini-1.5-flash-latest',
                system_instruction="Eres Fulano, un asistente pana venezolano...",
                tools=all_tools
            )

            # Recuperamos historial de DB
            db_messages = crud.get_messages_by_conversation(db, conversation_id=conversation.id)
            history_for_gemini = [
                {"role": "user" if msg.sender == 'user' else "model", "parts": [{"text": msg.content}]}
                for msg in db_messages
            ]

            chat_session = model.start_chat(history=history_for_gemini)
            response = chat_session.send_message(request.message)

            final_text = "".join(part.text for part in response.parts)
            response_text = final_text

        except Exception as e:
            response_text = f"Error al contactar a Gemini: {e}"

    # 6. Guardamos la respuesta del bot
    crud.create_message(db, conversation=conversation, sender='bot', content=response_text, handled_by_gemini=handled_by_gemini)

    return JSONResponse(content={
        "generated_text": response_text,
        "conversation_id": conversation.id
    })

# --- ENDPOINT PARA RECUPERAR HISTORIAL ---
@app.get("/api/history/{conversation_id}")
def get_history(conversation_id: str, db: Session = Depends(database.get_db)):
    db_messages = crud.get_messages_by_conversation(db, conversation_id=conversation_id)
    return [{"id": msg.id, "text": msg.content, "sender": msg.sender} for msg in db_messages]

# --- ENDPOINT DE IMAGENES (sin cambios) ---
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
        raise HTTPException(status_code=500, detail=f"Error en el servicio de imágenes: {e}")
