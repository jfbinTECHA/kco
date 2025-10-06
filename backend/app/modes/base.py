from typing import List, Dict, Any
import os
from ..settings import settings
from ..providers.openai import OpenAIProvider

class Mode:
    name = "base"

    def __init__(self):
        self.provider = OpenAIProvider()

    def load_rules(self) -> Dict[str, str]:
        """Load global and project rules from files."""
        rules = {}
        rules_dir = os.path.join(os.path.dirname(__file__), '..', 'rules')

        # Load global rules
        global_rules_path = os.path.join(rules_dir, 'global.md')
        if os.path.exists(global_rules_path):
            with open(global_rules_path, 'r') as f:
                rules['global'] = f.read().strip()

        # Load project rules
        project_rules_path = os.path.join(rules_dir, 'project.md')
        if os.path.exists(project_rules_path):
            with open(project_rules_path, 'r') as f:
                rules['project'] = f.read().strip()

        return rules

    def system_prompt(self, project_context: Dict[str, Any] | None) -> str:
        return "You are a helpful software assistant."

    def postprocess(self, text: str) -> str:
        return text

    def build_system_prompt(self, project_context=None) -> str:
        """Build complete system prompt: base + global + project + mode-specific"""
        rules = self.load_rules()

        prompt_parts = []

        # Base system prompt
        prompt_parts.append("You are a helpful software assistant.")

        # Global rules
        if 'global' in rules:
            prompt_parts.append(f"\n## Global Rules\n{rules['global']}")

        # Project rules
        if 'project' in rules:
            prompt_parts.append(f"\n## Project Rules\n{rules['project']}")

        # Mode-specific prompt
        mode_prompt = self.system_prompt(project_context)
        if mode_prompt != "You are a helpful software assistant.":  # Don't duplicate base prompt
            prompt_parts.append(f"\n## Mode-Specific Instructions\n{mode_prompt}")

        return "\n".join(prompt_parts)

    def process(self, message: str, project_context: dict = None, conversation_history: list = None) -> str:
        try:
            system_prompt = self.build_system_prompt(project_context)
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

            raw_response = self.provider.chat_completion(
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            return self.postprocess(raw_response)
        except Exception as e:
            return f"Error: {str(e)}"