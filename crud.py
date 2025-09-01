# crud.py
from sqlalchemy.orm import Session
import models
from datetime import datetime

def get_or_create_conversation(db: Session, conversation_id: str = None) -> models.Conversation:
    if conversation_id:
        conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        if conversation:
            return conversation
    
    new_conversation = models.Conversation()
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

def create_message(db: Session, conversation_id: str, sender: str, content: str, handled_by_gemini: bool = False):
    new_message = models.Message(
        conversation_id=conversation_id,
        sender=sender,
        content=content,
        handled_by_gemini=handled_by_gemini
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_messages_by_conversation(db: Session, conversation_id: str):
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at).all()