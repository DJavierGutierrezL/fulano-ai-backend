from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# Base de SQLAlchemy
Base = declarative_base()

# ==========================
# 📌 MODELOS Pydantic (Request/Response)
# ==========================

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None  # ID opcional para continuar conversación
    message: str                           # Mensaje del usuario


# ==========================
# 📌 MODELOS SQLAlchemy (BD)
# ==========================

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)  # UUID que identifica conversación
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con mensajes
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender = Column(String)  # "user" o "bot"
    content = Column(Text)
    handled_by_gemini = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relación con conversación
    conversation = relationship("Conversation", back_populates="messages")
