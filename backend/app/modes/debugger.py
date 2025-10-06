from ..kilo_adapter import load_prompt

class DebuggerMode:
    name = "debugger"

    def system_prompt(self, project_context):
        return load_prompt(self.name)