import os
import random
from datetime import datetime
import pytz
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Importar módulos locales
import models, crud, database
from intents import predict_intent, INTENT_RESPONSES
from tools import calculate
from fastapi.middleware.cors import CORSMiddleware

# ==========================
# Inicializar FastAPI
# ==========================
app = FastAPI(
    title="Fulano AI Backend",
    description="Asistente virtual con memoria y manejo de intents",
    version="1.0.0"
)

@app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 En desarrollo lo dejamos abierto
    allow_credentials=True,
    allow_methods=["*"],  # 👈 Esto incluye OPTIONS, POST, GET, etc.
    allow_headers=["*"],
)
# ==========================
# Evento al iniciar (crear tablas si no existen)
# ==========================
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)


# ==========================
# Endpoint principal del chat
# ==========================
@app.post("/api/chat")
def chat(request: models.ChatRequest, db: Session = Depends(database.get_db)):
    """
    Endpoint de conversación.
    - Guarda los mensajes en la base de datos
    - Detecta la intención del usuario
    - Genera la respuesta correspondiente
    """
    # Crear o buscar conversación
    conversation = crud.get_or_create_conversation(db, conversation_id=request.conversation_id)

    # Guardar mensaje del usuario en la DB
    crud.create_message(db, conversation=conversation, sender="user", content=request.message)

    # Detectar intent
    intent = predict_intent(request.message)
    response_text = ""

    # -------------------------
    # Respuestas por intención
    # -------------------------
    if intent in ["saludo", "despedida", "agradecimiento"]:
        response_text = random.choice(INTENT_RESPONSES[intent])

    elif intent == "hora":
        colombia_tz = pytz.timezone("America/Bogota")
        now = datetime.now(colombia_tz)
        response_text = f"La hora en Colombia es {now.strftime('%H:%M:%S')}."

    elif intent == "matematica":
        try:
            result = calculate(request.message)
            response_text = f"El resultado es: {result}"
        except Exception:
            response_text = "No pude calcular eso, mi pana."

    else:
        response_text = "No entendí bien, pero dime otra vez y lo resolvemos."

    # Guardar respuesta del bot en DB
    crud.create_message(db, conversation=conversation, sender="bot", content=response_text)

    # Retornar respuesta
    return JSONResponse(content={
        "generated_text": response_text,
        "conversation_id": conversation.id
    })


# ==========================
# Endpoint historial de conversación
# ==========================
@app.get("/api/history/{conversation_id}")
def get_history(conversation_id: int, db: Session = Depends(database.get_db)):
    """
    Recupera el historial de una conversación
    """
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        return JSONResponse(content={"error": "Conversación no encontrada"}, status_code=404)

    history = [{"sender": msg.sender, "content": msg.content} for msg in conversation.messages]
    return {"conversation_id": conversation.id, "history": history}


# ==========================
# Endpoint raíz
# ==========================
@app.get("/")
def root():
    return {"message": "Bienvenido a Fulano AI Backend (versión final con intents y memoria)"}
