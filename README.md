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

## Production Deployment

### Architecture Overview

```
🌐 [Vercel Frontend (Next.js)]
   ↓  HTTPS  (BACKEND_URL)
🛠️ [Fly.io Backend (FastAPI + Node)]
   ├─ FastAPI  →  /chat, /plan, /execute
   └─ Node Kilocode Agent  →  bridge.js (streaming)
```

**Stateless demo, zero ops** - No DB/Redis/volumes required. OpenAI key lives only on backend.

### Frontend Deployment (Vercel)

1. **Push to GitHub**: Ensure repo is pushed to GitHub (main or public-demo branch)
2. **Import Project**: Visit https://vercel.com/new and import your repository
3. **Configure Build**:
   - **Root Directory**: `frontend/`
   - Vercel will auto-detect Next.js settings
   - Uses the provided `vercel.json` configuration
4. **Environment Variables**:
   - `BACKEND_URL`: `https://kilocode-backend.fly.dev`
5. **Deploy**: Click "Deploy" ✅

**Your demo URL will look like**: `https://kilocode-standalone.vercel.app/dual`

### Automated Deployment (Optional)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that automatically deploys both backend and frontend when code is pushed to the main branch.

#### Required GitHub Secrets

| Secret              | Purpose                      |
| ------------------- | ---------------------------- |
| `FLY_API_TOKEN`     | Fly.io personal access token |
| `VERCEL_TOKEN`      | Vercel API token             |
| `VERCEL_PROJECT_ID` | Found in Vercel dashboard    |
| `OPENAI_API_KEY`    | (optional backup)            |

#### Setup Steps

1. **Add Repository Secrets** in GitHub Settings → Secrets and variables → Actions
2. **Push to main branch** - deployment happens automatically
3. **Monitor deployment** in the Actions tab

### Backend Deployment (Fly.io)

1. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`
2. **Deploy Backend**:
   ```bash
   cd backend
   fly auth login
   fly launch --now --region iad --copy-config
   fly secrets set OPENAI_API_KEY=sk-yourkeyhere
   ```
3. **Note Backend URL**: Once deployed, your backend will be available at:
   `https://kilocode-backend.fly.dev`

#### Testing Commands
```bash
curl https://kilocode-backend.fly.dev/docs      # FastAPI online
curl https://kilocode-backend.fly.dev/plan      # should return 405 (good)
open  https://kilocode-standalone.vercel.app/dual
```

### Key Benefits

- **Stateless**: No database/Redis/volumes required
- **Secure**: OpenAI key lives only on backend
- **Scalable**: Vercel CDN + Fly.io containers
- **Zero Ops**: Managed infrastructure
- **Fast**: Global CDN for frontend, regional backend

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

## Features Implemented

✅ **Streaming responses** (Server-Sent Events) for real-time UX
✅ **Dual-panel interface** (/dual) - AI Planner ↔ Kilocode Executor
✅ **Kilocode bridge** - Subprocess execution of original agent
✅ **Project context** - File indexing and awareness
✅ **Interactive rules** - Global/project rule editing
✅ **Multiple modes** - Architect, Coder, Debugger, Ask
✅ **Production deployment** - Vercel + Fly.io architecture

## Future Enhancements

- File upload + repo browser for project context
- Per-mode tool menus (Generate file, Run test, Diff preview)
- Cost and token-usage display
- Dynamic model switching (UI dropdown)
- User authentication and session management
- Advanced project analysis and insights