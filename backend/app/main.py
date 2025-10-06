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
    # Extract the latest user message
    user_messages = [msg for msg in req.messages if msg.role == "user"]
    if not user_messages:
        return ChatResponse(content="No user message found", meta={"error": "no_user_message"})

    latest_message = user_messages[-1].content

    # Process with mode, context, and custom rules
    response_text = mode.process(
        message=latest_message,
        project_context=req.project_context,
        custom_rules=req.custom_rules
    )
    return ChatResponse(content=response_text, meta={"mode": mode.name})

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    mode = get_mode(req.mode)
    # Extract the latest user message
    user_messages = [msg for msg in req.messages if msg.role == "user"]
    if not user_messages:
        async def error_generate():
            yield "data: Error: No user message found\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            error_generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    latest_message = user_messages[-1].content
    # Convert messages to format expected by process method
    conversation_history = [m.dict() for m in req.messages[:-1]]  # All except last message

    async def generate():
        try:
            # Use the mode's process method with streaming
            response_text = mode.process(
                message=latest_message,
                project_context=req.project_context,
                conversation_history=conversation_history,
                custom_rules=req.custom_rules
            )

            # For now, yield the full response as one chunk (streaming token-by-token would require provider changes)
            yield f"data: {response_text}\n\n"
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