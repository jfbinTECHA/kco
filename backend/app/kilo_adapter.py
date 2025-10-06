"""
Thin adapter to emulate kilocode-like modes without VS Code bindings.
Replace internals later by importing real kilocode modules or calling its CLI/
HTTP.
"""
from .modes import MODE_MAP

def get_mode(name: str):
    return MODE_MAP.get(name, MODE_MAP["coder"])