from ..kilo_adapter import load_prompt

class AskMode:
    name = "ask"

    def system_prompt(self, ctx):
        return load_prompt(self.name)