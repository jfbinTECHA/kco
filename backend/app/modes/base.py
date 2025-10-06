from typing import List, Dict, Any
import os
from ..settings import settings
from ..providers.openai import OpenAIProvider
from ..tools.fs import FileSystemTool

class Mode:
    name = "base"

    def __init__(self):
        self.provider = OpenAIProvider()
        self.fs_tool = FileSystemTool()

    def load_rules(self, custom_rules: Dict[str, str] = None) -> Dict[str, str]:
        """Load rules from custom input or fallback to files."""
        if custom_rules:
            return custom_rules

        # Fallback to static files
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

    def build_system_prompt(self, project_context=None, custom_rules=None) -> str:
        """Build complete system prompt: base + global + project + mode-specific"""
        rules = self.load_rules(custom_rules)

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

    def get_project_context(self, project_path: str = ".") -> Dict[str, Any]:
        """Generate project context using filesystem tools"""
        try:
            # Index the project directory
            index_result = self.fs_tool.index_directory(project_path, max_depth=2)

            if "error" in index_result:
                return {"error": index_result["error"]}

            # Create a compact file list for context
            files_list = []
            for file_info in index_result.get("files", [])[:20]:  # Limit to 20 files
                files_list.append(f"{file_info['path']} ({file_info['size']} bytes)")

            return {
                "path": project_path,
                "files_index": files_list,
                "total_files": index_result.get("total_files", 0),
                "total_dirs": index_result.get("total_dirs", 0)
            }
        except Exception as e:
            return {"error": f"Failed to generate project context: {str(e)}"}

    def process(self, message: str, project_context: dict = None, conversation_history: list = None, custom_rules: dict = None) -> str:
        try:
            system_prompt = self.build_system_prompt(project_context, custom_rules)
            messages = [{"role": "system", "content": system_prompt}]

            # Generate project context if path provided
            if project_context and "path" in project_context:
                fs_context = self.get_project_context(project_context["path"])
                if "error" not in fs_context:
                    context_str = f"Project Files: {', '.join(fs_context.get('files_index', [])[:10])}"  # Limit to 10 files
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