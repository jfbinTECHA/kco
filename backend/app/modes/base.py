from typing import List, Dict, Any
import openai
from ..settings import settings

class Mode:
    name = "base"

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def system_prompt(self, project_context: Dict[str, Any] | None) -> str:
        return "You are a helpful software assistant."

    def postprocess(self, text: str) -> str:
        return text

    def process(self, message: str, project_context: dict = None, conversation_history: list = None) -> str:
        try:
            system_prompt = self.system_prompt(project_context)
            messages = [{"role": "system", "content": system_prompt}]

            # Add project context if available
            if project_context:
                context_str = f"Project Context: {project_context}"
                messages.append({"role": "system", "content": context_str})

            # Add conversation history if available
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages for context

            # Add current user message
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=settings.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            raw_response = response.choices[0].message.content.strip()
            return self.postprocess(raw_response)
        except Exception as e:
            return f"Error: {str(e)}"