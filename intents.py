# intents.py

INTENTS = [
    {
        "name": "saludo",
        "examples": [
            "hola", "buenos dias", "buenas tardes", "buenas noches", "hey", "qué tal", "holi",
            "qué onda", "hello", "saludos", "cómo estás", "qué más", "qué hubo", "epa chamo"
        ],
        "responses": ["¡Qué pasa, pana! ¿Cómo estás? Dime, ¿qué necesitas?", "¡Chévere! ¿En qué te puedo ayudar hoy?"]
    },
    {
        "name": "despedida",
        "examples": [
            "adios", "chao", "hasta luego", "nos vemos", "bye", "hasta pronto", "me despido",
            "cuidate", "hasta la próxima", "nos vemos después", "que estés bien"
        ],
        "responses": ["¡Dale pues, mi pana! Nos vemos pronto.", "¡Chévere! Cuídate mucho."]
    },
    {
        "name": "agradecimiento",
        "examples": [
            "gracias", "muchas gracias", "te lo agradezco", "mil gracias", "genial gracias",
            "gracias por todo", "se agradece", "muy amable", "te debo una"
        ],
        "responses": ["¡De nada, estamos a la orden!", "¡Con gusto, mi pana!"]
    },
    # Estos intents no tienen respuestas directas, llamarán a una función
    {"name": "hora", "examples": ["qué hora es", "la hora", "dime la hora", "qué hora tienes"]},
    {"name": "fecha", "examples": ["qué fecha es hoy", "dime la fecha", "qué día es hoy"]},
    {"name": "chiste", "examples": ["cuéntame un chiste", "hazme reír", "quiero un chiste", "un chiste por favor"]},
]