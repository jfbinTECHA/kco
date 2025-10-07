# Kilocode → Standalone Smart Chat (OpenAI) — Integration Guide

This guide extends the starter scaffold into a **full Kilocode‑powered AI chat platform** that runs independently of VS Code.

## Architecture Overview

```
[Chat UI / Frontend]
    ↕ Websocket / HTTP
[Chat Orchestrator / API Layer]
    ↕ Memory & State Store
    ↕ Project Context Layer
    ↕ Agent / Planner (copied from Kilo)
        ↕ Subtasks, Tools, Chains
    ↕ Tool Invocation Layer (fs, exec, web, plugin)
    ↕ Model Interface (OpenAI, etc.)
```

---

## 1. New Repository Layout

```
kilocode-standalone/
├─ backend/
│  ├─ app/
│  │  ├─ modes/
│  │  ├─ kilo_adapter.py
│  │  ├─ tools/
│  │  │  ├─ fs.py
│  │  │  └─ sandbox.py
│  │  └─ prompts/
│  ├─ kilocode_core/         ← imported from Kilo‑Org/kilocode/packages
│  │  ├─ agent/
│  │  ├─ parser/
│  │  └─ prompts/
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ components/
│  │  ├─ Chat.tsx
│  │  ├─ ModeSelector.tsx
│  │  └─ FileIndexView.tsx
│  ├─ app/
│  │  ├─ api/chat/route.ts
│  │  └─ page.tsx
│  └─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

---

## 2. Copy Kilocode Core

Clone [Kilo‑Org/kilocode](https://github.com/Kilo-Org/kilocode) and copy these:

| Source                      | Destination                      | Notes                |
| --------------------------- | -------------------------------- | -------------------- |
| `packages/agent/src/*`      | `backend/kilocode_core/agent/`   | reasoning/plan logic |
| `packages/parser/src/*`     | `backend/kilocode_core/parser/`  | code parser utils    |
| `packages/prompts/src/*`    | `backend/kilocode_core/prompts/` | mode templates       |
| (optional) `packages/types` | for schema hints                 |                      |

Preserve Apache‑2.0 headers.

---

## 3. Python Bridge (`kilo_adapter.py`)

```python
from pathlib import Path
KILOCODE_PROMPTS = Path(__file__).resolve().parents[1]/"kilocode_core"/"prompts"

def load_prompt(mode:str)->str:
    p = KILOCODE_PROMPTS/f"{mode}.md"
    return p.read_text() if p.exists() else "You are a helpful AI assistant."

def build_system_prompt(mode:str, ctx:dict|None=None)->str:
    base=load_prompt(mode)
    if ctx:
        base+=f"\n\n# Context\n{ctx}"
    return base
```

Use in `main.py`:

```python
system = build_system_prompt(req.mode, req.project_context)
```

---

## 4. Mode Classes

Each mode just loads its template:

```python
from ..kilo_adapter import load_prompt
class ArchitectMode:
    name="architect"
    def system_prompt(self, ctx):
        return load_prompt(self.name)
```

Repeat for coder, debugger, ask.

---

## 5. Rules Merge

Merge project/global rules before sending to OpenAI:

```python
def load_rules():
    def r(p):
        try:return open(p).read()
        except: return ""
    return r("rules/global.md"),r("rules/project.md")

g,p=load_rules()
system=f"{mode.system_prompt(req.project_context)}\n# Global Rules\n{g}\n# Project Rules\n{p}"
```

---

## 6. Safe File Index Tool

```python
from pathlib import Path
def index(root:str,max_bytes=2000):
    rootp=Path(root).resolve();out=[]
    for p in rootp.rglob('*'):
        if p.is_file() and p.stat().st_size<=max_bytes:
            out.append({"path":str(p.relative_to(rootp)),"sample":p.read_text(errors='ignore')[:400]})
    return {"root":str(rootp),"files":out}
```

---

## 7. Streaming Endpoint (SSE)

```python
from fastapi import Request
from fastapi.responses import StreamingResponse
@app.post('/chat/stream')
async def chat_stream(req:ChatRequest,request:Request):
    mode=get_mode(req.mode)
    system=build_system_prompt(req.mode,req.project_context)
    def gen():
        with client.chat.completions.stream(model=settings.model,messages=[{"role":"system","content":system}]+[m.dict() for m in req.messages],temperature=0.2,) as s:
            for e in s:
                if e.type=='content.delta': yield f"data: {e.delta}\n\n"
                if request.is_disconnected(): break
            yield "data: [DONE]\n\n"
    return StreamingResponse(gen(),media_type='text/event-stream')
```

---

## 8. Frontend Updates

### ModeSelector.tsx

```tsx
<select value={mode} onChange={e=>setMode(e.target.value)}>
  <option value="architect">Architect</option>
  <option value="coder">Coder</option>
  <option value="debugger">Debugger</option>
  <option value="ask">Ask</option>
</select>
```

### FileIndexView.tsx

Add basic file browser that hits `/tools/fs/index`.

---

## 9. Testing Checklist

| Test               | Expected           |
| ------------------ | ------------------ |
| `/chat` mode=coder | loads real prompt  |
| `/tools/fs/index`  | returns file list  |
| `/chat/stream`     | token stream works |
| Mode switch        | prompt changes     |

---

## 10. Licensing

Add to root README:

> Portions of this project are adapted from [Kilo‑Org/kilocode](https://github.com/Kilo-Org/kilocode) under Apache‑2.0.

Create `NOTICE`:

```
This project includes source from Kilo‑Org/kilocode
Copyright (c) 2024 Kilo‑Org. Licensed under Apache‑2.0.
```

---

## 11. Deployment

```bash
cp .env.example .env
# set OPENAI_API_KEY
docker compose up --build
```

Visit [http://localhost:3000](http://localhost:3000).

---

## 12. Integration Challenges & Solutions

When adapting Kilocode components from VS Code extension to standalone chat platform:

| Challenge                           | What to Change / Simplify                                                                                      | Reason / Risk                                                                     |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Editor & extension APIs**         | Remove or abstract all VS Code / JetBrains-specific APIs (file watchers, editor buffers, command palette)      | In a chat backend you won't have a host editor environment                        |
| **Heavy tools or commands**         | Restrict or sandbox "write file," "exec," "git," etc.                                                          | To avoid compromising the host or environment                                     |
| **Complex memory / state coupling** | Decouple memory from editor context and make state APIs explicit (e.g. conversation history, project snapshot) | Chat modes need explicit state management                                         |
| **UI/webview code**                 | You'll reuse some React/TS logic, but you'll need to adapt it to Next.js or your chat frontend                 | Embedding vs standalone UI are different models                                   |
| **Prompt size & token limits**      | Kilo likely uses aggressive summarization/truncation strategies to stay within model limits                    | You'll need similar prompt trimming logic for chat                                |
| **Error recovery and chaining**     | Some recovery logic might assume the user can directly run code, fix files in editor                           | In chat interface, you may need more clarifying questions instead of direct edits |

### ✅ Result

You now have a **Kilocode‑compatible chat platform**:

* Real Kilocode prompts drive OpenAI completions.
* Modes: Architect / Coder / Debugger / Ask.
* Streaming, rule merging, and safe context tools ready.
* Integration challenges identified and solutions provided.

Next: connect your GitHub repo, commit this integration guide, and push branch `feature/kilocode-adapter`. 🚀