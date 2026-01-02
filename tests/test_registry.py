from sica_bridge.registry import get_component, list_components


def test_list_components_has_4_defaults():
    comps = list_components()
    assert len(comps) == 4
    assert [c.id for c in comps] == [
        "approaches",
        "columns",
        "joints_hinges",
        "abutments_wingwalls_shearkeys",
    ]


def test_get_component():
    c = get_component("columns")
    assert c.display_name.lower().startswith("columns")
