"""
Kilocode Bridge — run the Node-based Kilocode agent as a subprocess.
Allows the Python backend to call Kilocode's original JS/TS reasoning logic.
"""

import subprocess, json, tempfile, os, sys, asyncio
from pathlib import Path
from typing import AsyncGenerator

BASE_DIR = Path(__file__).resolve().parents[1]
AGENT_DIR = BASE_DIR / "kilocode_core" / "agent"

def run_kilocode_agent(mode: str, input_data: dict) -> dict:
    """
    Executes the Kilocode agent with JSON input.
    Requires Node.js and built packages (tsc compiled JS).
    """

    # Write input to a temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump({"mode": mode, "input": input_data}, f)
        f.flush()
        input_path = f.name

    script_path = AGENT_DIR / "bridge.js"  # Node.js bridge script

    try:
        # Run Node subprocess
        cmd = ["node", str(script_path), input_path]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(AGENT_DIR),
            timeout=60,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Kilocode agent failed: {proc.stderr}")

        # Parse output JSON
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"error": "Non-JSON response", "raw": proc.stdout}

    except Exception as e:
        return {"error": str(e)}

    finally:
        try:
            os.remove(input_path)
        except:
            pass

async def stream_kilocode_agent(mode: str, input_data: dict) -> AsyncGenerator[str, None]:
    """
    Asynchronously stream output from the Kilocode agent subprocess.
    Yields each line as it becomes available (JSON or text tokens).
    """
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump({"mode": mode, "input": input_data}, f)
        f.flush()
        input_path = f.name

    script_path = AGENT_DIR / "bridge.js"  # streaming-capable bridge

    try:
        process = await asyncio.create_subprocess_exec(
            "node",
            str(script_path),
            input_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(AGENT_DIR),
        )

        async for line in process.stdout:
            line_str = line.decode("utf-8", errors="ignore").strip()
            if line_str:
                yield line_str  # each line may be JSON or raw token

        await process.wait()

        # Check for errors
        if process.returncode != 0:
            stderr = await process.stderr.read()
            yield f"Error: {stderr.decode('utf-8', errors='ignore')}"

    finally:
        try:
            os.remove(input_path)
        except:
            pass