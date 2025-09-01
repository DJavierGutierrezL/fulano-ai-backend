# main.py - VERSIÓN CORREGIDA CON INTENTS + GEMINI FALLBACK

import os
import random
import requests
from datetime import datetime
import pytz
import google.generativeai as genai
import google.generativeai.protos as protos
import cohere
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models, crud, database
from intents import predict_intent, INTENT_RESPONSES
from tools import (
    get_current_time, get_weather, get_news, google_search, translate_text,
    calculate, rerank_documents, get_pokemon_info, search_marvel_character,
    search_free_images, search_wikipedia, get_exchange_rate, extract_city
)

# Inicializar FastAPI
app = FastAPI()

# Inicializar Gemini y Cohere
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Base de datos
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)


# ==========================
# Endpoint principal del chat
# ==========================
@app.post("/api/chat")
def chat(request: models.ChatRequest, db: Session = Depends(database.get_db)):
    # Buscar o crear conversación
    conversation = crud.get_or_create_conversation(db, conversation_id=request.conversation_id)
    crud.create_message(db, conversation=conversation, sender="user", content=request.message)

    # Detectar intent
    intent = predict_intent(request.message)
    response_text = ""
    handled_by_gemini = False

    # -------------------------
    # Intentos directos
    # -------------------------
    if intent in ["saludo", "despedida", "agradecimiento", "chiste"]:
        response_text = random.choice(INTENT_RESPONSES[intent])

    elif intent == "hora":
        # Hora de Colombia
        colombia_tz = pytz.timezone("America/Bogota")
        now = datetime.now(colombia_tz)
        response_text = f"La hora en Colombia es {now.strftime('%H:%M:%S')}."

    elif intent == "clima":
        city = extract_city(request.message)
        weather_data = get_weather(city)
        if "error" in weather_data:
            response_text = "¡Qué vaina! No pude conseguir el clima en este momento."
        else:
            response_text = f"En {weather_data['city']} la temperatura es {weather_data['temperature']} con {weather_data['description']}."

    elif intent == "matematica":
        try:
            result = calculate(request.message)
            response_text = f"El resultado es: {result}"
        except Exception:
            response_text = "No pude calcular eso, mi pana."

    # -------------------------
    # Fallback a Gemini
    # -------------------------
    else:
        handled_by_gemini = True
        try:
            # Historial de conversación
            db_messages = crud.get_messages_by_conversation(db, conversation_id=conversation.id)
            history_for_gemini = [
                {"role": ("user" if msg.sender == "user" else "model"),
                 "parts": [{"text": msg.content}]}
                for msg in db_messages
            ]

            all_tools = [
                get_current_time, get_weather, get_news, google_search, translate_text,
                calculate, rerank_documents, get_pokemon_info, search_marvel_character,
                search_free_images, search_wikipedia, get_exchange_rate
            ]

            system_instruction = "Eres un asistente virtual llamado 'Fulano', con personalidad venezolana, divertido pero útil."

            model = genai.GenerativeModel(
                "gemini-1.5-flash-latest",
                system_instruction=system_instruction,
                tools=all_tools
            )
            chat_session = model.start_chat(history=history_for_gemini)
            response = chat_session.send_message(request.message)

            # Intentar ejecutar función si Gemini lo pide
            try:
                function_call = response.candidates[0].content.parts[0].function_call
                if function_call:
                    tool_name = function_call.name
                    tool_args = {key: value for key, value in function_call.args.items()}
                    tools_map = {tool.__name__: tool for tool in all_tools}
                    if tool_name in tools_map:
                        tool_result = tools_map[tool_name](**tool_args)
                        response = chat_session.send_message(
                            protos.FunctionResponse(name=tool_name, response=tool_result)
                        )
            except Exception:
                pass

            # Extraer texto seguro
            response_text = "".join(
                part.text for part in response.candidates[0].content.parts if hasattr(part, "text")
            )

        except Exception as e:
            print(f"Error con Gemini: {e}")
            response_text = "Lo siento, mi pana, mi cerebro se pegó otra vez."

    # Guardar respuesta en DB
    crud.create_message(db, conversation=conversation, sender="bot", content=response_text, handled_by_gemini=handled_by_gemini)

    return JSONResponse(content={"generated_text": response_text, "conversation_id": conversation.id})


# ==========================
# Endpoint raíz
# ==========================
@app.get("/")
def root():
    return {"message": "Bienvenido a Fulano AI Backend"}
