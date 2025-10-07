import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Literal, Dict, Any

from ..kilocode_bridge import stream_kilocode_agent  # from earlier bridge step

router = APIRouter(prefix="/execute", tags=["executor"])

class ExecRequest(BaseModel):
    mode: Literal["coder","architect","debugger","ask"] = "coder"
    plan: List[str]
    context: Dict[str, Any] | None = None

@router.post("")
async def execute_plan(req: ExecRequest):
    """Streams live logs/tokens from the Kilocode agent applying the plan."""
    async def gen():
        payload = {"plan": req.plan, "context": req.context or {}}
        async for chunk in stream_kilocode_agent(req.mode, payload):
            # Expect JSON lines {"delta": "..."} or raw text
            try:
                data = json.loads(chunk)
                token = data.get("delta") or data.get("content") or chunk
            except Exception:
                token = chunk
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")