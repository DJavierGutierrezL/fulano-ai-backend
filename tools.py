# tools.py - Funciones utilitarias para Fulano AI

import os
import requests
from datetime import datetime
import pytz
import re
from datetime import datetime
import pytz
# ==========================
# Herramientas básicas
# ==========================


def get_weather(city: str = "Bogotá"):
    """Consulta el clima actual usando la API de OpenWeatherMap"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "Falta la API key de OpenWeather"}
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=es&units=metric"

    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return {"error": response.get("message", "No se pudo obtener el clima")}
        
        return {
            "city": response["name"],
            "temperature": f"{response['main']['temp']} °C",
            "description": response["weather"][0]["description"]
        }
    except Exception as e:
        return {"error": str(e)}

def get_news(country: str = "co", lang: str = "es"):
    """Consulta titulares de noticias usando GNews API"""
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        return {"error": "Falta la API key de GNews"}

    url = f"https://gnews.io/api/v4/top-headlines?country={country}&lang={lang}&token={api_key}"
    try:
        response = requests.get(url).json()
        if "articles" not in response:
            return {"error": response.get("message", "No se pudo obtener noticias")}
        
        articles = response["articles"]
        top_news = [f"{a['title']} - {a['source']['name']}" for a in articles[:5]]
        return {"news": top_news}
    except Exception as e:
        return {"error": str(e)}


def google_search(query: str):
    """Simula búsqueda en Google (sin API real)"""
    return {"result": f"Busqué en Google: {query}, pero no tengo API oficial configurada."}

def translate_text(text: str, target_lang: str = "en"):
    """Traducción usando Google Translate API (Traduce con 'translate.googleapis.com')"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={text}"
        response = requests.get(url)
        if response.status_code == 200:
            translated_text = response.json()[0][0][0]
            return {"translated_text": translated_text}
        return {"error": "No pude traducir el texto."}
    except Exception as e:
        return {"error": str(e)}

def calculate(expression: str):
    """Evalúa expresiones matemáticas simples"""
    try:
        result = eval(expression, {"__builtins__": {}})
        return result
    except Exception:
        return "No pude calcular eso, mi pana."

def rerank_documents(query: str, documents: list):
    """Simulación de rerankeo de documentos"""
    return {"reranked": sorted(documents, key=lambda x: len(x))}

def get_pokemon_info(name: str):
    """Ejemplo de integración con la API de Pokémon"""
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    try:
        response = requests.get(url).json()
        return {
            "name": response["name"],
            "height": response["height"],
            "weight": response["weight"],
            "base_experience": response["base_experience"]
        }
    except Exception:
        return {"error": "No pude conseguir ese Pokémon."}

def search_marvel_character(name: str):
    """Simulación búsqueda personaje Marvel"""
    return {"character": f"Busqué a {name} en Marvel, pero no tengo API configurada aún."}

def search_free_images(query: str):
    """Simulación de búsqueda de imágenes gratis"""
    return {"images": [f"https://dummyimage.com/600x400/000/fff&text={query}"]}

def search_wikipedia(query: str):
    """Simulación de búsqueda en Wikipedia"""
    return {"summary": f"Resumen ficticio de Wikipedia sobre: {query}"}

def get_exchange_rate(base: str = "USD", target: str = "COP"):
    """Obtiene tasa de cambio usando exchangerate.host"""
    url = f"https://api.exchangerate.host/latest?base={base}&symbols={target}"
    try:
        response = requests.get(url).json()
        rate = response["rates"][target]
        return {"rate": rate}
    except Exception:
        return {"error": "No pude obtener la tasa de cambio."}

def extract_city(text: str):
    """Extrae una ciudad básica del texto (rudimentario)"""
    ciudades = ["bogotá", "medellín", "cali", "barranquilla", "caracas", "maracaibo"]
    for ciudad in ciudades:
        if ciudad in text.lower():
            return ciudad
    return "Bogotá"
# ==========================
# Herramienta: Calcular operaciones matemáticas
# ==========================
def calculate(expression: str):
    """
    Evalúa operaciones matemáticas básicas desde el texto del usuario.
    Ejemplo:
        "8 * 8" -> 64
        "100 / 5" -> 20
    """
    try:
        # Extraer solo números y operadores permitidos
        match = re.findall(r"[0-9\.\+\-\*\/\(\)]+", expression)
        safe_expression = "".join(match)
        if not safe_expression:
            return "Expresión inválida."

        result = eval(safe_expression)
        return result
    except Exception:
        return "No pude calcular eso."


# ==========================
# Herramienta: Hora actual en Colombia
# ==========================
def get_current_time():
    """
    Retorna la hora actual en Colombia.
    """
    colombia_tz = pytz.timezone("America/Bogota")
    now = datetime.now(colombia_tz)
    return now.strftime("%H:%M:%S")