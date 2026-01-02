from sica_bridge.resources import load_prompt_template, load_rubric, load_system_prompt


def test_load_system_prompt():
    txt = load_system_prompt()
    assert isinstance(txt, str)
    assert len(txt) > 0


def test_load_rubric_and_prompt():
    r = load_rubric("columns")
    p = load_prompt_template("columns")
    assert isinstance(r, dict)
    assert isinstance(p, str)
    assert len(p) > 0
