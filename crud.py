from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import uuid


# ==========================
# 📌 Conversaciones
# ==========================

def get_or_create_conversation(db: Session, conversation_id: str = None) -> models.Conversation:
    """
    Busca una conversación por ID, o crea una nueva si no existe.
    """
    if conversation_id:
        conversation = db.query(models.Conversation).filter_by(conversation_id=conversation_id).first()
        if conversation:
            return conversation

    # Crear nueva conversación
    new_conversation = models.Conversation(conversation_id=str(uuid.uuid4()))
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation


def get_conversation_by_id(db: Session, conversation_id: str):
    """
    Retorna una conversación por su conversation_id.
    """
    return db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation_id).first()


# ==========================
# 📌 Mensajes
# ==========================

def create_message(db: Session, conversation: models.Conversation, sender: str, content: str, handled_by_gemini: bool = False):
    """
    Crea un nuevo mensaje en la conversación.
    """
    new_message = models.Message(
        conversation_id=conversation.id,
        sender=sender,
        content=content,
        handled_by_gemini=handled_by_gemini
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def get_messages_by_conversation(db: Session, conversation_id: int):
    """
    Obtiene todos los mensajes de una conversación específica.
    """
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.timestamp.asc()).all()


def delete_conversation(db: Session, conversation_id: str):
    """
    Elimina una conversación y sus mensajes.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False
