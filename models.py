from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

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
    __tablename__ = 'conversations'

    # Opción 1: Auto-incremento (para un id entero)
    id = Column(Integer, primary_key=True) 

    # Opción 2: UUID generado automáticamente (para un id de tipo UUID)
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    conversation_id = Column(String)
    # ... otras columnas


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
