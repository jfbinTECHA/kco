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
    from .kilo_adapter import build_system_prompt

    # Extract the latest user message
    user_messages = [msg for msg in req.messages if msg.role == "user"]
    if not user_messages:
        return ChatResponse(content="No user message found", meta={"error": "no_user_message"})

    latest_message = user_messages[-1].content

    # Build system prompt using Kilocode templates
    system_prompt = build_system_prompt(req.mode, req.project_context)

    # Get conversation history (all messages except the last user message)
    conversation_history = [m.dict() for m in req.messages[:-1]]

    # Process with OpenAI directly using the prompt template
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": latest_message})

    try:
        resp = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=0.2,
        )
        response_text = resp.choices[0].message.content or ""
        return ChatResponse(content=response_text, meta={"mode": req.mode})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    from .kilo_adapter import build_system_prompt

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

    # Build system prompt using Kilocode templates
    system_prompt = build_system_prompt(req.mode, req.project_context)

    # Get conversation history (all messages except the last user message)
    conversation_history = [m.dict() for m in req.messages[:-1]]

    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": latest_message})

    async def generate():
        try:
            # Use streaming response from OpenAI
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