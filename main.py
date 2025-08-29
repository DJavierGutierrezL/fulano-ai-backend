# main.py - VERSIÓN FINAL CON ENFOQUE HÍBRIDO

import os
import requests
from datetime import datetime
import pytz 
import google.generativeai as genai
import google.generativeai.protos as protos
import cohere
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json
from asteval import Interpreter
import time
import hashlib
import pokebase as pb
import wikipediaapi
import random
# <-- NUEVAS IMPORTACIONES PARA EL CLASIFICADOR -->
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# <-- IMPORTAMOS NUESTROS INTENTS LOCALES -->
from intents import INTENTS

# --- Configuración de APIs (sin cambios) ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
marvel_public_key = os.getenv("MARVEL_PUBLIC_KEY")
marvel_private_key = os.getenv("MARVEL_PRIVATE_KEY")
pexels_api_key = os.getenv("PEXELS_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- Definición de Herramientas (sin cambios) ---
def get_current_time(timezone: str = "America/Caracas"):
    """Devuelve la hora actual en una zona horaria específica."""
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

# ... (Todas las demás funciones de herramientas: get_weather, get_news, google_search, etc., van aquí sin cambios)
def get_weather(city: str):
    """Obtiene el clima actual para una ciudad específica usando WeatherAPI.com."""
    if not weather_api_key: return {"error": "El servicio del clima no está configurado"}
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = { "city": data["location"]["name"], "temperature": f"{data['current']['temp_c']}°C", "description": data["current"]["condition"]["text"] }
        return weather
    except requests.exceptions.RequestException:
        return {"error": f"No se pudo obtener el clima para {city}"}
def get_news(query: str):
    """Busca las 5 noticias más recientes sobre un tema específico."""
    if not news_api_key: return {"error": "El servicio de noticias no está configurado"}
    try:
        url = f"https://newsapi.org/v2/top-headlines?q={query}&language=es&pageSize=5&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        headlines = [{"title": article["title"], "url": article["url"]} for article in data["articles"]]
        return {"headlines": headlines}
    except requests.exceptions.RequestException:
        return {"error": f"No se pudieron obtener noticias sobre {query}"}
def google_search(query: str):
    """Realiza una búsqueda en Google para obtener una respuesta rápida a una pregunta."""
    if not serper_api_key: return {"error": "El servicio de búsqueda no está configurado"}
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_api_key, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "answerBox" in data: return {"result": data["answerBox"].get("answer") or data["answerBox"].get("snippet")}
        if "organic" in data and len(data["organic"]) > 0: return {"result": data["organic"][0].get("snippet")}
        return {"result": "No se encontró una respuesta directa."}
    except requests.exceptions.RequestException:
        return {"error": f"La búsqueda de '{query}' falló."}
def translate_text(text: str, target_language: str, source_language: str = "auto"):
    """Traduce un texto de un idioma a otro."""
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"translated_text": data["responseData"]["translatedText"]}
    except requests.exceptions.RequestException:
        return {"error": "El servicio de traducción falló."}
def calculate(expression: str):
    """Evalúa una expresión matemática de forma segura."""
    try:
        aeval = Interpreter()
        result = aeval.eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": f"Expresión matemática inválida: {e}"}
def rerank_documents(query: str, documents: list[str]):
    """Re-ordena una lista de documentos según su relevancia a una consulta, usando la API oficial de Cohere."""
    if not cohere_api_key: return {"error": "El servicio de Re-ranking de Cohere no está configurado."}
    try:
        co = cohere.Client(cohere_api_key)
        response = co.rerank(model='rerank-multilingual-v3.0', query=query, documents=documents, top_n=3)
        ranked_results = [{"document": result.document['text']} for result in response.results]
        return {"ranked_results": ranked_results}
    except Exception as e:
        return {"error": f"El re-ranking de documentos con Cohere falló: {e}"}
def get_pokemon_info(pokemon_name: str):
    """Busca un Pokémon por su nombre en una Pokédex y devuelve sus datos clave como ID, altura, peso y tipos."""
    for attempt in range(3):
        try:
            pokemon = pb.pokemon(pokemon_name.lower())
            types = [t.type.name for t in pokemon.types]
            info = { "name": pokemon.name.capitalize(), "pokedex_id": pokemon.id, "height": f"{pokemon.height / 10} m", "weight": f"{pokemon.weight / 10} kg", "types": types }
            return info
        except Exception as e:
            print(f"Intento {attempt + 1} para get_pokemon_info falló: {e}")
            time.sleep(1)
    return {"error": f"No se pudo contactar la PokéAPI para buscar a '{pokemon_name}' después de varios intentos."}
def search_marvel_character(character_name: str):
    """Busca un personaje en el universo de Marvel y devuelve su descripción."""
    if not marvel_public_key or not marvel_private_key: return {"error": "El servicio de Marvel no está configurado."}
    try:
        ts = str(time.time())
        hash_string = ts + marvel_private_key + marvel_public_key
        hash_md5 = hashlib.md5(hash_string.encode()).hexdigest()
        url = f"http://gateway.marvel.com/v1/public/characters?nameStartsWith={character_name}&ts={ts}&apikey={marvel_public_key}&hash={hash_md5}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()["data"]["results"]
        if not data: return {"result": f"No se encontró ningún personaje llamado '{character_name}'."}
        character = data[0]
        return { "name": character["name"], "description": character["description"] or "No hay una descripción disponible.", "comics_available": character["comics"]["available"] }
    except Exception as e:
        print(f"ERROR en la herramienta search_marvel_character: {e}")
        return {"error": f"La búsqueda en Marvel falló: {e}"}
def search_free_images(search_query: str):
    """Busca imágenes gratuitas y de alta calidad sobre un tema específico usando la API de Pexels."""
    if not pexels_api_key: return {"error": "El servicio de Pexels no está configurado."}
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": pexels_api_key}
        params = {"query": search_query, "per_page": 3, "locale": "es-ES"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get("photos", [])
        if not data: return {"result": f"No se encontraron imágenes en Pexels para '{search_query}'."}
        image_urls = [photo.get("src", {}).get("medium") for photo in data]
        return {"image_urls": image_urls}
    except Exception as e:
        print(f"ERROR en la herramienta search_free_images (Pexels): {e}")
        return {"error": f"La búsqueda de imágenes en Pexels falló: {e}"}
def search_wikipedia(topic: str):
    """Busca un tema en Wikipedia y devuelve un resumen del artículo."""
    try:
        wiki_wiki = wikipediaapi.Wikipedia(language='es', user_agent='FulanoAI/1.0')
        page = wiki_wiki.page(topic)
        if not page.exists():
            return {"error": f"No encontré un artículo de Wikipedia para '{topic}'."}
        summary = page.summary[0:500]
        return {"topic": topic, "summary": f"{summary}..."}
    except Exception as e:
        return {"error": f"La búsqueda en Wikipedia falló: {e}"}
def tell_joke():
    """Cuenta un chiste al azar en español."""
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?lang=es&type=single", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("error"):
            return {"error": "No se pudo obtener un chiste en este momento."}
        return {"joke": data.get("joke")}
    except Exception as e:
        return {"error": f"La API de chistes falló: {e}"}
def get_exchange_rate(base_currency: str = "USD", target_currency: str = "COP"):
    """Obtiene la tasa de cambio actual entre dos monedas."""
    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "error":
            return {"error": data.get("error-type", "Error desconocido en la API de divisas")}
        rate = data.get("rates", {}).get(target_currency.upper())
        if not rate:
            return {"error": f"No se encontró la tasa de cambio para '{target_currency.upper()}'."}
        return {"base": base_currency.upper(), "target": target_currency.upper(), "rate": rate}
    except Exception as e:
        return {"error": f"La consulta de divisas falló: {e}"}


# --- LÓGICA DEL CLASIFICADOR DE INTENCIONES (NUESTRO MINI-CEREBRO) ---
def _collect_training_data():
    X, y = [], []
    for intent in INTENTS:
        if "examples" in intent:
            for example in intent["examples"]:
                X.append(example.lower())
                y.append(intent["name"])
    return X, y

def make_intent_model():
    X, y = _collect_training_data()
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(C=10, solver='liblinear')),
    ])
    pipeline.fit(X, y)
    return pipeline

# Entrenamos el modelo cuando la aplicación inicia
INTENT_CLASSIFIER = make_intent_model()

def predict_intent(text: str):
    """Clasifica la intención de un texto. Si no está seguro, devuelve 'fallback_to_gemini'."""
    predictions = INTENT_CLASSIFIER.predict_proba([text.lower()])[0]
    max_proba_index = predictions.argmax()
    if predictions[max_proba_index] > 0.7: # Umbral de confianza
        return INTENT_CLASSIFIER.classes_[max_proba_index]
    return "fallback_to_gemini"


# --- Configuración y Endpoints de FastAPI ---
app = FastAPI(title="Asistente Virtual con Herramientas")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Message(BaseModel): id: str; text: str; sender: str
class ChatRequest(BaseModel): message: str; history: list[Message] | None = None
class ImageRequest(BaseModel): prompt: str


# --- Endpoint del Chat (REFACTORIZADO CON LÓGICA HÍBRIDA) ---
@app.post("/api/chat")
def chat(request: ChatRequest):
    user_message = request.message
    
    # 1. El mini-cerebro local intenta clasificar la pregunta
    intent = predict_intent(user_message)
    
    # 2. Si es una intención simple, respondemos directamente
    if intent == "saludo":
        response_text = random.choice([resp for i in INTENTS if i["name"] == "saludo" for resp in i["responses"]])
        return JSONResponse(content=[{"generated_text": response_text}])
    
    if intent == "despedida":
        response_text = random.choice([resp for i in INTENTS if i["name"] == "despedida" for resp in i["responses"]])
        return JSONResponse(content=[{"generated_text": response_text}])

    if intent == "agradecimiento":
        response_text = random.choice([resp for i in INTENTS if i["name"] == "agradecimiento" for resp in i["responses"]])
        return JSONResponse(content=[{"generated_text": response_text}])

    if intent == "hora":
        time_data = get_current_time()
        return JSONResponse(content=[{"generated_text": f"¡Claro! La hora es {time_data.get('time', 'desconocida')}."}])

    if intent == "fecha":
        # Nota: Usando la hora del servidor. Para otras zonas horarias, se necesitaría una lógica más compleja.
        now_caracas = datetime.now(pytz.timezone("America/Caracas"))
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        fecha_str = f"Hoy es {dias[now_caracas.weekday()]}, {now_caracas.day} de {meses[now_caracas.month - 1]} de {now_caracas.year}"
        return JSONResponse(content=[{"generated_text": fecha_str}])

    if intent == "chiste":
        joke_data = tell_joke()
        return JSONResponse(content=[{"generated_text": joke_data.get('joke', 'Hoy no estoy de humor para chistes, mi pana.')}])
        
    # 3. Si no es una intención simple (fallback), llamamos al cerebro principal: Gemini
    if not api_key: raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    try:
        system_instruction = """
        Eres un asistente virtual llamado 'Fulano', con personalidad venezolana. Tu estilo debe ser amigable y pana, como si hablaras con un chamo. Usa jergas como 'chévere', 'mi pana', 'qué fino', 'dale pues'. Evita ser robótico. Sé útil, pero con un toque personal y cercano. Cuando una herramienta te devuelva información, como una lista de URLs de imágenes o noticias, tu trabajo es presentar esa información al usuario de forma clara y directa. No intentes 'mostrar' la imagen tú mismo, simplemente proporciona los enlaces o los datos que recibiste.
        """
        
        all_tools = [
            get_current_time, get_weather, get_news, google_search, translate_text, 
            calculate, rerank_documents, get_pokemon_info, search_marvel_character, 
            search_free_images, search_wikipedia, tell_joke, get_exchange_rate
        ]
        
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=system_instruction,
            tools=all_tools
        )
        
        history = [{"role": "user" if msg.sender == 'user' else "model", "parts": [{"text": msg.text}]} for msg in request.history] if request.history else []
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_message)
        
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

        final_text = "".join(part.text for part in response.parts)
        return JSONResponse(content=[{"generated_text": final_text}])
        
    except Exception as e:
        print(f"Error en el endpoint de chat (Fallback a Gemini): {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-image")
def generate_image(request: ImageRequest):
    # ... (Este endpoint no cambia)
    if not api_key: raise HTTPException(status_code=500, detail="El servicio de IA no está configurado.")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"Una imagen fotorrealista de alta calidad de: {request.prompt}"
        response = model.generate_content(prompt)
        image_data = response.parts[0].inline_data
        image_base64 = base64.b64encode(image_data.data).decode('utf-8')
        return JSONResponse(content={"image_base64": image_base64})
    except Exception as e:
        print(f"ERROR DETALLADO DE GENERACIÓN DE IMAGEN: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de imágenes: {e}")