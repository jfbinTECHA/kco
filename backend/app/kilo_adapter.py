"""
Thin adapter to emulate kilocode-like modes without VS Code bindings.
Replace internals later by importing real kilocode modules or calling its CLI/
HTTP.
"""
from .modes.architect import ArchitectMode
from .modes.coder import CoderMode
from .modes.debugger import DebuggerMode

MODE_MAP = {
    "architect": ArchitectMode(),
    "coder": CoderMode(),
    "debugger": DebuggerMode(),
}

def get_mode(name: str):
    return MODE_MAP.get(name, MODE_MAP["coder"])