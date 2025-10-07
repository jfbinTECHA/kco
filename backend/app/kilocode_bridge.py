"""
Kilocode Bridge — run the Node-based Kilocode agent as a subprocess.
Allows the Python backend to call Kilocode's original JS/TS reasoning logic.
"""

import subprocess, json, tempfile, os, sys
from pathlib import Path

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