import pytest
from sica_bridge.schemas import ComponentAssessment, EventAssessment, RState


def test_component_assessment_valid():
    obj = ComponentAssessment(component_id="columns", r_state=RState.R2, reason="Minor cracking observed.")
    assert obj.r_state == RState.R2
    assert obj.component_id == "columns"


def test_component_assessment_rejects_empty_reason():
    with pytest.raises(Exception):
        ComponentAssessment(component_id="columns", r_state=RState.R1, reason="")


def test_event_assessment_valid():
    ev = EventAssessment(
        overall_r_state=RState.R3,
        components=[
            ComponentAssessment(component_id="approaches", r_state=RState.R1, reason="No visible issues."),
            ComponentAssessment(component_id="columns", r_state=RState.R3, reason="Significant diagonal cracking."),
        ],
    )
    assert ev.overall_r_state == RState.R3
    assert len(ev.components) == 2
