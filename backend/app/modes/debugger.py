from .base import Mode

class DebuggerMode(Mode):
    name = "debugger"

    def system_prompt(self, project_context):
        logs = (project_context or {}).get("logs", [])[:5]
        return (
            "You are an expert at debugging. Analyze errors and propose minimal\n"
            "fixes.\n"
            f"Recent logs: {logs}"
        )