from .base import Mode

class AskMode(Mode):
    name = "ask"

    def system_prompt(self, project_context=None):
        return (
            "You are a knowledgeable AI assistant ready to help with any questions.\n"
            "Provide clear, accurate, and helpful answers. Be concise but comprehensive.\n"
            "Draw from your knowledge to give practical advice and explanations."
        )