# main.py - VERSIÓN CON SINTAXIS VERIFICADA

import os
import requests
from datetime import datetime
import pytz 
import google.generativeai as genai
from google.generativeai.types import Part
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json

# --- Configuración de APIs ---
api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- Definición de Herramientas ---
def get_current_time(timezone: str = "America/Caracas"):
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {"time": current_time.strftime("%I:%M %p")}
    except pytz.UnknownTimeZoneError:
        return {"error": "Zona horaria desconocida"}

def get_weather(city: str):
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
    if not news_api_key: return {"error": "El servicio de noticias no está configurado"}
    try:
        url = f"https://newsapi.org/v2/top-headlines?q={query}&language=es&pageSize=3&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        headlines = [{"title": article["title"], "url": article["url"]} for article in data["articles"]]
        return {"headlines": headlines}
    except requests.exceptions.RequestException:
        return {"error": f"No se pudieron obtener noticias sobre {query}"}

def google_search(query: str):
    if not serper_api_key: return {"error": "El servicio de búsqueda no está configurado"}
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_api_key, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "answerBox" in data:
            return {"result": data["answerBox"].get("answer") or data["answerBox"].get("snippet")}
        if "organic" in data and len(data["organic"]) > 0:
            return {"result": data["organic"][0].get("snippet")}
        return {"result": "No se encontró una respuesta directa."}
    except requests.exceptions.RequestException:
        return {"error": f"La búsqueda de '{query}' fall