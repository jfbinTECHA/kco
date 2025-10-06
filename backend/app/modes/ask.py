from .base import Mode
from ..kilo_adapter import build_system_prompt

class AskMode(Mode):
    name = "ask"

    def system_prompt(self, ctx):
        return build_system_prompt("ask", ctx)