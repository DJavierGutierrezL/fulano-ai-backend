from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
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
    conversation_id: Optional[str] = None
    message: str


# ==========================
# 📌 MODELOS SQLAlchemy (BD)
# ==========================

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(String) # Considera si este campo es realmente necesario si 'id' ya es un UUID
    created_at = Column(DateTime, default=datetime.utcnow) # Es útil tener la fecha de creación

    # Relación inversa (back_populates) para acceder a los mensajes desde la conversación
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Asegúrate de que el tipo de ForeignKey coincida con el tipo de la clave primaria de 'conversations'
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    
    sender = Column(String)  # "user" o "bot"
    content = Column(Text)
    handled_by_gemini = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relación con conversación
    conversation = relationship("Conversation", back_populates="messages")