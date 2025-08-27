from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    model_id: str
    message: str

@app.get("/models")
def list_models(q: str = "chat"):
    url = f"https://huggingface.co/api/models?search={q}&limit=20"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    r = requests.get(url, headers=headers)
    return r.json()

@app.post("/chat")
def chat(request: ChatRequest):
    url = f"https://api-inference.huggingface.co/models/{request.model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {"inputs": request.message}
    r = requests.post(url, headers=headers, json=payload)
    try:
        data = r.json()
    except Exception:
        return {"error": "Invalid response", "raw": r.text}
    return data
