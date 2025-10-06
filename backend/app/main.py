import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    mode = get_mode(req.mode)
    system = mode.system_prompt(req.project_context)
    messages = [{"role": "system", "content": system}] + [m.dict() for m in req.messages]

    async def generate():
        try:
            response = client.chat.completions.create(
                model=settings.model,
                messages=messages,
                temperature=0.2,
                stream=True,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    # Send each token as a Server-Sent Event
                    yield f"data: {chunk.choices[0].delta.content}\n\n"

            # Send end marker
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )