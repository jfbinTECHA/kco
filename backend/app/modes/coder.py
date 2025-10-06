from .base import Mode

class CoderMode(Mode):
    name = "coder"

    def system_prompt(self, project_context):
        files = (project_context or {}).get("files_index", [])
        return (
            "You are a senior engineer writing clean, production-quality code.\n"
            f"You can reference these files: {files}. Respond with code blocks\n"
            "and brief notes."
        )