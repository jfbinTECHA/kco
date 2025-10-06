# Kilocode Standalone Chat

## Attribution

Portions of this project are adapted from [Kilo-Org/kilocode](https://github.com/Kilo-Org/kilocode)
under the Apache-2.0 license. See [NOTICE](NOTICE) for details.

## Prereqs
- Docker + Docker Compose
- OpenAI API key

## Run
cp .env.example .env
# edit .env and set OPENAI_API_KEY
docker compose up --build
Open http://localhost:3000

## How to "Plug Back" Real Kilocode Logic Later
Create a kilocode wrapper in backend/app/kilo_adapter.py that calls the real project's
functions or a local CLI you expose.
Replace the simplistic system_prompt with kilocode's real prompt templates and utilities.
Add project context providers (e.g., index files, AST, logs) through a safe file picker or a mounted
repo path exposed to the backend.
(Optional) Execution sandbox — add a runner module using Docker to run tests or commands
when ALLOW_EXECUTE=true .

## Custom Rules

The system supports customizable rules that are automatically merged into AI prompts:

- **Global Rules** (`backend/app/rules/global.md`): Apply to all interactions
- **Project Rules** (`backend/app/rules/project.md`): Apply to this specific project

System prompts are built as: `base + global + project + mode-specific`

### Interactive Rules Editor

The web interface includes a **Rules Pane** with two textareas for editing rules in real-time:

- **Global Rules**: Universal guidelines for all conversations
- **Project Rules**: Specific rules for the current project context

Click "Show Rules" to access the editor and customize AI behavior without restarting the application.

### Project Context Integration

The **Project Panel** allows you to specify a project path for automatic context generation:

- Uses `fs.index` tool to scan project directories
- Provides file listings and metadata to the AI
- Helps the AI understand project structure and available files
- Integrates seamlessly with all modes for context-aware responses

## Next Steps / Nice to Have
Streaming responses (Server-Sent Events) for faster UX.
File upload + lightweight repo browser to supply project_context .
Per-mode tool menus (Generate file, Run test, Diff preview).
Cost and token-usage display.
Swap models dynamically (UI dropdown).