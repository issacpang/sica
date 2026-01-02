from sica_bridge.llm.client import FakeVisionLLMClient, VisionInput


def test_fake_client_returns_stub():
    c = FakeVisionLLMClient('{"component_id":"columns","r_state":"R1","reason":"ok"}')
    out = c.complete_json(prompt="x", images=VisionInput(image_bytes=b"123"))
    assert '"r_state":"R1"' in out
