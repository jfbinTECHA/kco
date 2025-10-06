"""
Thin adapter to emulate kilocode-like modes without VS Code bindings.
Replace internals later by importing real kilocode modules or calling its CLI/
HTTP.
"""
from pathlib import Path
from .modes import MODE_MAP
from .settings import settings

KILOCODE_PROMPTS = Path(__file__).resolve().parents[1] / "kilocode_core" / "prompts"

def load_prompt(mode: str) -> str:
    p = KILOCODE_PROMPTS / f"{mode}.md"
    return p.read_text() if p.exists() else "You are a helpful AI assistant."

def build_system_prompt(mode: str, project_context: dict | None = None) -> str:
    base = load_prompt(mode)
    ctx = ""
    if project_context:
        ctx = f"\n\n# Context\n{project_context}"
    return base + ctx

def get_mode(name: str):
    return MODE_MAP.get(name, MODE_MAP["coder"])