import random

# Lista de intenciones con ejemplos y respuestas
INTENTS = [
    {
        "name": "saludo",
        "examples": ["epale", "buenas", "que mas pues", "hola", "saludos"],
        "responses": [
            "¡Épale, mi pana! ¿Qué cuentas?",
            "¡Chévere verte por aquí! Dime qué se te ofrece.",
            "¡Qlq! ¿Qué más, yunta?"
        ]
    },
    {
        "name": "despedida",
        "examples": ["chao", "nos vemos", "hasta luego", "me voy"],
        "responses": [
            "Dale pues, estamos hablando. ¡Cualquier vaina me avisas!",
            "Chévere, mi pana. ¡Nos vemos en la bajadita!",
            "¡Listo, compa! Que la pases bien."
        ]
    },
    {
        "name": "agradecimiento",
        "examples": ["gracias", "muchas gracias", "chévere, gracias"],
        "responses": [
            "¡De nada, mi pana! A la orden siempre.",
            "¡Tranquilo, para eso estamos!",
            "¡Fino! Me alegra haberte ayudado."
        ]
    },
    {
        "name": "hora",
        "examples": ["qué hora es", "la hora", "dime la hora"],
        "responses": ["Déjame revisar el reloj y te digo la hora exacta."]
    },
    {
        "name": "clima",
        "examples": ["qué clima hace", "cómo está el clima", "clima en Medellín"],
        "responses": ["Dame un momento y te busco el clima actualizado."]
    },
    {
        "name": "matematica",
        "examples": ["calcula", "cuánto es", "resuelve", "suma", "multiplica"],
        "responses": ["Déjame hacer las cuentas, mi pana."]
    },
    {
        "name": "chiste",
        "examples": ["cuéntame un chiste", "dime algo gracioso"],
        "responses": [
            "A ver... ¿Qué le dice un pez a otro? ¡Nada!",
            "¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!"
        ]
    }
]

# Diccionario rápido de respuestas
INTENT_RESPONSES = {intent["name"]: intent["responses"] for intent in INTENTS}

# Función simple para predecir intención
def predict_intent(text: str) -> str:
    text = text.lower()
    for intent in INTENTS:
        for example in intent["examples"]:
            if example in text:
                return intent["name"]
    return "desconocido"
