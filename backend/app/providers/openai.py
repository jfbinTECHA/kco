import openai
from typing import List, Dict, Any, Iterator, Optional
from ..settings import settings

class OpenAIProvider:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Non-streaming chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=settings.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def chat_completion_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Streaming chat completion that yields tokens"""
        try:
            response = self.client.chat.completions.create(
                model=settings.model,
                messages=messages,
                stream=True,
                **kwargs
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"Error: {str(e)}"

    def map_error(self, error: Exception) -> str:
        """Map OpenAI errors to user-friendly messages"""
        error_str = str(error).lower()

        if "rate limit" in error_str:
            return "Rate limit exceeded. Please try again later."
        elif "invalid api key" in error_str:
            return "Invalid API key. Please check your configuration."
        elif "insufficient_quota" in error_str:
            return "API quota exceeded. Please check your OpenAI account."
        elif "model_not_found" in error_str:
            return f"Model '{settings.model}' not found. Please check your model configuration."
        else:
            return f"AI service error: {str(error)}"