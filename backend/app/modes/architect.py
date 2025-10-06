from .base import Mode

class ArchitectMode(Mode):
    name = "architect"

    def system_prompt(self, project_context):
        return (
            "You are an expert software architect. Produce high-level designs,\n"
            "constraints, and tradeoffs. Output concise, actionable plans."
        )