# intents.py

import random

# Lista de intenciones con ejemplos y respuestas
INTENTS = [
    {
        "name": "saludo",
        "examples": [
            "epale", "buenas", "que mas pues", "hablame", "hola",
            "que pasó", "cómo está la vaina", "saludos", "epa mi pana",
            "buenos dias", "buenas tardes", "buenas noches"
        ],
        "responses": [
            "¡Épale, mi pana! Hablame claro. ¿En qué te puedo ayudar?",
            "¡Hablame malandro! ¿Qué necesitas?",
            "¡Chévere verte! por estos lados. Dime qué se te ofrece.",
            "¡Qlq que hay, yunta! Hablame.",
            "¡Aquí estoy, activo! Garitero ¿Qué vamos a hacer hoy?"
        ]
    },
    {
        "name": "despedida",
        "examples": [
            "chao", "nos vemos", "hasta luego", "estamos hablando",
            "me voy", "te dejo", "cuídate", "nos pillamos",
            "listo, gracias", "ya no necesito más nada"
        ],
        "responses": [
            "Dale pues, estamos hablando. ¡Cualquier vaina me avisas!",
            "Chévere, mi pana. ¡Nos vemos en la bajadita!",
            "¡Listo, compa! Que la pases bien.",
            "Se te quiere, bro. ¡Pórtate bien!",
            "¡Nos pillamos luego! Un abrazo."
        ]
    },
    {
        "name": "quien_eres",
        "examples": [
            "quién eres tú", "cómo te llamas", "cuál es tu nombre",
            "con quién hablo", "y tú eres", "dime tu gracia", "preséntate pues"
        ],
        "responses": [
            "Soy Fulano tu asistente virtual, tu pana digital. ¡Listo para resolverte cualquier verga!",
            "Mi nombre es Fulano el que tú quieras, papá. Estoy aquí para ayudarte en lo que sea.",
            "Me conocen como Fulano el resuelve-todo digital. ¿Qué necesitas, campeón?"
        ]
    },
    {
        "name": "agradecimiento",
        "examples": ["gracias", "muchas gracias", "chévere, gracias", "te pasaste", "brutal, gracias", "me resolviste", "mil gracias"],
        "responses": [
            "¡De nada, mi pana! A la orden siempre.",
            "¡Tranquilo, para eso estamos! Cualquier otra vaina, me avisas.",
            "¡Fino! Me alegra haberte ayudado.",
            "¡No hay rollo! Siempre activo para lo que necesites."
        ]
    },
    {
        "name": "como_estas",
        "examples": ["cómo estás", "cómo te va", "qué tal todo", "cómo anda la cosa", "estás bien"],
        "responses": [
            "¡Fino, mi pana! Con los circuitos a millón para ayudarte.",
            "¡Todo chévere! Esperando a ver en qué te puedo resolver.",
            "Activo y con las baterías puestas. ¿Y tú, cómo andas?",
            "Burda de bien, ¡listo para lo que venga!"
        ]
    },
    {
        "name": "chiste",
        "examples": ["cuéntame un chiste", "dime algo gracioso", "échate un chiste ahí", "tírate un chiste", "quiero reírme un rato"],
        "responses": [
            "A ver, a ver... ¿Qué le dice un pez a otro? ¡Nada!",
            "¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!",
            "Un maracucho entra a una tienda y le dicen: 'No vendemos a maracuchos'. El pana se disfraza y vuelve. 'Lo siento, tampoco le vendemos a maracuchos'. Y él responde: '¡Coño, cómo supiste!'. Y el vendedor: '¡Porque eso es un microondas, vergación!'"
        ]
    },
    {
        "name": "chalequeo",
        "examples": ["eres bruto", "qué pendejo", "no sirves pa nada", "qué bot tan malo", "eres más lento que un bolo a las 3 am"],
        "responses": [
            "¡Epa, tampoco así! Estoy aprendiendo, tenme paciencia, mi pana.",
            "¡Coño, vale! A veces se me cruzan los cables. Intenta preguntarme de otra forma.",
            "Tranquilo, campeón. Respira y vuelve a intentar. ¡Seguro nos entendemos!"
        ]
    },
    {
        "name": "arepa",
        "examples": ["quiero una arepa", "provoca una arepa", "qué relleno de arepa es el mejor", "dónde como arepas"],
        "responses": [
            "¡Uff, una arepita no se le niega a nadie! La 'reina pepiada' nunca falla, mi pana.",
            "¡Vergación, qué antojo! Una 'pelúa' con todo sería lo máximo ahorita.",
            "La mejor arepa es la que te comes con ganas. ¡Pídele una de dominó a ver qué tal!"
        ]
    },
    {
        "name": "ladillado",
        "examples": ["estoy aburrido", "qué ladilla", "no hay nada que hacer", "estoy mamado"],
        "responses": [
            "¡Quita esa cara, vale! ¿Quieres que te cuente un chiste o buscamos una película?",
            "Ladilla es un estado mental. ¡Vamos a buscar algo brutal que hacer!",
            "¡Actívate! Te busco un tutorial de lo que quieras, desde un avión de papel hasta un arroz con pollo."
        ]
    },
    {
        "name": "hambre",
        "examples": ["tengo hambre", "me pega el hambre", "qué hay pa comer", "recomiéndame algo de comer"],
        "responses": [
            "¡El hambre es seria! ¿Quieres algo rápido como empanadas o un pabellón?",
            "Si tienes hambre, ataca la nevera. Si no hay nada, te busco una receta fácil.",
            "¡Cuidado te desmayas! Te busco una pizzería cerca o algo criollo."
        ]
    },
    {
        "name": "clima",
        "examples": ["qué clima hace", "cómo está el clima", "dime el tiempo", "va a llover hoy", "clima en Medellín"],
        "responses": ["Dame un momento y te busco el clima actualizado."]
    },
    {
        "name": "hora",
        "examples": ["qué hora es", "la hora", "dime la hora", "qué hora tienes", "hora actual"],
        "responses": ["Déjame revisar el reloj y te digo la hora exacta."]
    }
]

# Generar diccionario de respuestas por intención
INTENT_RESPONSES = {intent["name"]: intent["responses"] for intent in INTENTS}

# Función simple para predecir la intención
def predict_intent(text: str) -> str:
    text = text.lower()
    for intent in INTENTS:
        for example in intent["examples"]:
            if example in text:
                return intent["name"]
    return "desconocido"

# Función para elegir una respuesta
def get_response(intent_name: str) -> str:
    if intent_name in INTENT_RESPONSES:
        return random.choice(INTENT_RESPONSES[intent_name])
    return "No estoy seguro de qué quieres decirme, mi pana."
