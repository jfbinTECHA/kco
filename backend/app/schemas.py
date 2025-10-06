from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

ModeName = Literal["architect", "coder", "debugger"]

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mode: ModeName = "coder"
    project_context: Optional[Dict[str, Any]] = None  # files, paths, metadata

class ChatResponse(BaseModel):
    content: str
    meta: Dict[str, Any] = Field(default_factory=dict)