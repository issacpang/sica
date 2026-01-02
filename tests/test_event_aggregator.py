from sica_bridge.assess import aggregate_event
from sica_bridge.schemas import ComponentAssessment, RState


def test_aggregate_event_worst_case():
    comps = [
        ComponentAssessment(component_id="approaches", r_state=RState.R1, reason="ok"),
        ComponentAssessment(component_id="columns", r_state=RState.R3, reason="bad"),
        ComponentAssessment(component_id="joints_hinges", r_state=RState.R2, reason="minor"),
    ]
    ev = aggregate_event(comps)
    assert ev.overall_r_state == RState.R3
    assert len(ev.components) == 3


def test_aggregate_event_empty_raises():
    import pytest

    with pytest.raises(ValueError):
        aggregate_event([])
