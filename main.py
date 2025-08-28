# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router_gemini, router_huggingface

app = FastAPI(title="Asistente Virtual Multi-IA")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye los enrutadores en la aplicación principal
app.include_router(router_gemini.router, prefix="/api", tags=["Gemini"])
app.include_router(router_huggingface.router, prefix="/api", tags=["Hugging Face"])

@app.get("/")
def read_root():
    return {"status": "API Multi-IA está funcionando"}