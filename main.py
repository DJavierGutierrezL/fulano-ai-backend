# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importamos el nuevo enrutador de imágenes
from api import router_gemini, router_image_generation

app = FastAPI(title="Asistente Virtual Multi-Modal")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye los enrutadores en la aplicación principal
app.include_router(router_gemini.router, prefix="/api", tags=["Gemini Chat"])
# Reemplazamos el enrutador de huggingface por el de generación de imágenes
app.include_router(router_image_generation.router, prefix="/api", tags=["Image Generation"])

@app.get("/")
def read_root():
    return {"status": "API Multi-Modal está funcionando"}