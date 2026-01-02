from sica_bridge.assess import assess_component
from sica_bridge.llm.client import FakeVisionLLMClient


def test_assess_component_parses_and_validates():
    fake = FakeVisionLLMClient('{"component_id":"columns","r_state":"R2","reason":"Some cracking"}')
    out = assess_component(component_id="columns", image_bytes=b"fakebytes", client=fake)
    assert out.component_id == "columns"
    assert out.r_state.value == "R2"
    assert "cracking" in out.reason.lower()


def test_assess_component_handles_wrapped_json():
    fake = FakeVisionLLMClient('NOTE:\n{"r_state":"R1","reason":"ok"}\nThanks!')
    out = assess_component(component_id="approaches", image_bytes=b"x", client=fake)
    assert out.component_id == "approaches"
    assert out.r_state.value == "R1"
