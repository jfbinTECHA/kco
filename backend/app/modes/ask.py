from .base import Mode

class AskMode(Mode):
    name = "ask"

    def system_prompt(self, ctx):
        return ("You answer questions about codebases and technology. "
                "Prefer precise, cited, minimal answers; when code helps, include small snippets.")