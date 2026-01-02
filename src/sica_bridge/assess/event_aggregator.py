from __future__ import annotations

from sica_bridge.schemas import ComponentAssessment, EventAssessment, RState


# severity order (higher = worse)
_SEVERITY = {
    RState.R1: 1,
    RState.R2: 2,
    RState.R3: 3,
    RState.R4: 4,
}


def aggregate_event(components: list[ComponentAssessment]) -> EventAssessment:
    if not components:
        raise ValueError("No component assessments provided.")

    overall = max(components, key=lambda c: _SEVERITY[c.r_state]).r_state
    return EventAssessment(overall_r_state=overall, components=components)
