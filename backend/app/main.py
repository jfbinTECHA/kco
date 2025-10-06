import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ChatRequest, ChatResponse
from .kilo_adapter import get_mode
from .settings import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

app = FastAPI(title="Kilocode Standalone Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "KiloCode Standalone Backend"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    mode = get_mode(req.mode)
    system = mode.system_prompt(req.project_context)
    messages = [{"role": "system", "content": system}] + [m.dict() for m in req.messages]
    try:
        resp = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=0.2,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    text = resp.choices[0].message.content or ""
    return ChatResponse(content=mode.postprocess(text), meta={"mode": mode.name})