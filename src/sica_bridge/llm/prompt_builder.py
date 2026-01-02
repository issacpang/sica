from __future__ import annotations

import json
from typing import Any, Dict

from sica_bridge.resources import load_prompt_template, load_rubric, load_system_prompt
from sica_bridge.schemas import ComponentAssessment, RState
from sica_bridge.llm.client import VisionInput


def component_assessment_json_schema() -> Dict[str, Any]:
    """
    Use Pydantic's JSON schema as the contract we force the LLM to follow.
    """
    return ComponentAssessment.model_json_schema()


def render_prompt(component_id: str, images: list[VisionInput] | None = None) -> str:
    system = load_system_prompt().strip()
    component_prompt = load_prompt_template(component_id).strip()
    rubric = load_rubric(component_id)

    schema = component_assessment_json_schema()

    # Minimal, explicit instruction: output JSON only.
    # (No confidence, no recommendations.)
    parts = [
        system,
        "",
        "=== COMPONENT INSTRUCTIONS ===",
        component_prompt,
        "",
        "=== RUBRIC (YAML parsed to JSON) ===",
        json.dumps(rubric, indent=2, ensure_ascii=False),
        "",
        "=== OUTPUT REQUIREMENTS ===",
        "Return ONLY a valid JSON object that matches this JSON Schema.",
        "Do not wrap in markdown. Do not include extra keys.",
        json.dumps(schema, indent=2, ensure_ascii=False),
        "",
        "Reminder: r_state must be one of: " + ", ".join([s.value for s in RState]),
    ]
    return "\n".join(parts).strip()
