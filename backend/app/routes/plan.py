from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Dict, Any
from ..settings import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)
router = APIRouter(prefix="/plan", tags=["planner"])

class Msg(BaseModel):
    role: Literal["user","assistant","system"]
    content: str

class PlanRequest(BaseModel):
    messages: List[Msg]

@router.post("")
async def make_plan(req: PlanRequest):
    """Use a planning prompt to return a structured plan.
    The response is JSON with a `plan` array of steps and a `summary` string.
    """
    system = (
        "You are a senior software planner.\n"
        "Return a concise plan as JSON with keys: plan (array of steps), summary (string).\n"
        "Each plan step should be an imperative action.\n"
    )
    try:
        resp = client.chat.completions.create(
            model=settings.model,
            messages=[{"role":"system","content":system}] + [m.dict() for m in req.messages],
            temperature=0.2,
            response_format={"type":"json_object"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    txt = resp.choices[0].message.content or "{}"
    return txt