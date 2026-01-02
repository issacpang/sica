from sica_bridge.assess import assess_component_many, aggregate_component
from sica_bridge.llm.client import FakeVisionLLMClient
from sica_bridge.schemas import RState


def test_assess_component_many_and_aggregate():
    fake = FakeVisionLLMClient('{"component_id":"columns","r_state":"R2","reason":"x"}')

    photos = [
        (b"1", "a.jpg", "image/jpeg"),
        (b"2", "b.jpg", "image/jpeg"),
    ]
    results = assess_component_many(component_id="columns", photos=photos, client=fake)
    assert len(results) == 2
    assert all(r.r_state == RState.R2 for r in results)

    overall = aggregate_component(results)
    assert overall == RState.R2
