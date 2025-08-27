import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuración de la API de Gemini ---
# Lee la clave de API desde las variables de entorno de Render
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Esto nos avisará en los logs de Render si la clave no está configurada
    print("ERROR: La variable de entorno GEMINI_API_KEY no está configurada.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Configuración de la Aplicación FastAPI ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que tu frontend se comunique con este backend
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos (lo que recibe la API) ---
class ChatRequest(BaseModel):
    message: str
    # El model_id ya no es necesario para Gemini, pero lo dejamos para no cambiar el frontend
    model_id: str | None = None

# --- Endpoint del Chat ---
@app.post("/chat")
def chat(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado en el servidor.")

    try:
        # Seleccionamos el modelo de Gemini que queremos usar
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Enviamos el mensaje del usuario al modelo
        response = model.generate_content(request.message)

        # Devolvemos la respuesta en el formato que el frontend espera
        # para que no tengas que modificar el frontend de nuevo.
        return [{"generated_text": response.text}]

    except Exception as e:
        # Si algo sale mal con la API de Gemini, devolvemos un error
        print(f"Error al llamar a la API de Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de IA: {e}")