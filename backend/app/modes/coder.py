from ..kilo_adapter import load_prompt

class CoderMode:
    name = "coder"

    def system_prompt(self, project_context):
        return load_prompt(self.name)