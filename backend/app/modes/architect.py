from .base import Mode
from ..kilo_adapter import build_system_prompt

class ArchitectMode(Mode):
    name = "architect"

    def system_prompt(self, project_context):
        return build_system_prompt("architect", project_context)