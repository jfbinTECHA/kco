from typing import List, Dict, Any

def normalize_plan(raw_json: str) -> list[str]:
    """Takes planner JSON string and returns a list of step strings."""
    import json
    try:
        obj = json.loads(raw_json)
        if isinstance(obj, dict) and isinstance(obj.get("plan"), list):
            return [str(x) for x in obj["plan"]]
    except Exception:
        pass
    return []