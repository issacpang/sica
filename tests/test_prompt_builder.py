from sica_bridge.llm import render_prompt


def test_render_prompt_contains_schema_and_rubric():
    txt = render_prompt("columns")
    assert "OUTPUT REQUIREMENTS" in txt
    assert "json_schema" not in txt.lower()  # we don't need that word
    assert "R1" in txt and "R4" in txt
    assert "RUBRIC" in txt
