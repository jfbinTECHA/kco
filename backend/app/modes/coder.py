from .base import Mode
from ..kilo_adapter import build_system_prompt

class CoderMode(Mode):
    name = "coder"

    def system_prompt(self, project_context):
        return build_system_prompt("coder", project_context)