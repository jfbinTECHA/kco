from .base import Mode
from ..kilo_adapter import build_system_prompt

class DebuggerMode(Mode):
    name = "debugger"

    def system_prompt(self, project_context):
        return build_system_prompt("debugger", project_context)