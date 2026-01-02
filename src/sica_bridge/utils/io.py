from __future__ import annotations

import json
from typing import Any, Dict


def extract_json_object(text: str) -> Dict[str, Any]:
    """
    Robustly parse a JSON object from model output.

    Issac: We instruct the model to output pure JSON, but in practice it may include
    extra whitespace or accidental leading/trailing text. This function:
    - tries direct json.loads
    - otherwise extracts the first {...} block and parses it
    """
    text = text.strip()

    # Fast path: pure JSON
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Fallback: extract first JSON object by braces
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in text output.")

    candidate = text[start : end + 1]
    obj = json.loads(candidate)
    if not isinstance(obj, dict):
        raise TypeError("Extracted JSON is not an object/dict.")
    return obj
