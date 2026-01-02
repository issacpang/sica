from __future__ import annotations

from sica_bridge.llm import render_prompt
from sica_bridge.llm.client import VisionInput, VisionLLMClient
from sica_bridge.schemas import ComponentAssessment
from sica_bridge.utils import extract_json_object
from sica_bridge.resources import load_reference_images
from typing import Iterable
from sica_bridge.schemas import RState

# severity order (higher = worse)
_SEVERITY = {RState.R1: 1, RState.R2: 2, RState.R3: 3, RState.R4: 4}

def assess_component(
    *,
    component_id: str,
    image_bytes: bytes,
    client: VisionLLMClient,
    mime_type: str = "image/jpeg",
    filename: str | None = None,
    reference_limit: int = 4,  # optional tuning knob
) -> ComponentAssessment:
    """
    Assess ONE inspection photo.
    Preset reference images are auto-loaded from the codebase.
    """
    query_image = VisionInput(
        image_bytes=image_bytes,
        mime_type=mime_type,
        filename=filename,
        role="query",
        caption="Inspection photo",
    )

    refs = load_reference_images(component_id, limit=reference_limit)  # preset only
    images = [query_image, *refs]

    prompt = render_prompt(component_id, images=images)
    raw = client.complete_json(prompt=prompt, images=images)

    data = extract_json_object(raw)
    data["component_id"] = component_id  # enforce consistency
    return ComponentAssessment.model_validate(data)


def assess_component_many(
    *,
    component_id: str,
    photos: Iterable[tuple[bytes, str | None, str]],  # (image_bytes, filename, mime_type)
    client,
) -> list[ComponentAssessment]:
    """
    Issac: assess inspection photos one-by-one.
    Each photo returns its own R_state + reason.
    """
    results: list[ComponentAssessment] = []
    for idx, (b, fname, mt) in enumerate(photos, start=1):
        a = assess_component(
            component_id=component_id,
            image_bytes=b,
            filename=fname,
            mime_type=mt,
            client=client,
        )
        # optional traceability (doesn't change required fields)
        a = a.model_copy(update={"notes": f"photo_index={idx}, filename={fname}"})
        results.append(a)
    return results


def aggregate_component(assessments: list[ComponentAssessment]) -> RState:
    """
    Worst-case rollup for ONE component (across multiple photos).
    """
    if not assessments:
        raise ValueError("No photo assessments for this component.")
    return max(assessments, key=lambda a: _SEVERITY[a.r_state]).r_state
