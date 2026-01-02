from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(frozen=True)
class ComponentSpec:
    """
    Defines an inspection component category.

    `id` is the stable key used everywhere (schema output, prompts, rubrics, GUI).
    """
    id: str
    display_name: str
    rubric_filename: str
    prompt_filename: str


# Issac: Default set (today's 4 items). Extend by adding entries here (or later via plugins).
DEFAULT_COMPONENTS: Dict[str, ComponentSpec] = {
    "approaches": ComponentSpec(
        id="approaches",
        display_name="Approaches",
        rubric_filename="approaches.yaml",
        prompt_filename="components/approaches.md",
    ),
    "columns": ComponentSpec(
        id="columns",
        display_name="Columns",
        rubric_filename="columns.yaml",
        prompt_filename="components/columns.md",
    ),
    "joints_hinges": ComponentSpec(
        id="joints_hinges",
        display_name="Intermediate Deck Joints & Hinges",
        rubric_filename="joints_hinges.yaml",
        prompt_filename="components/joints_hinges.md",
    ),
    "abutments_wingwalls_shearkeys": ComponentSpec(
        id="abutments_wingwalls_shearkeys",
        display_name="Abutments, Wingwalls, & Shear Keys",
        rubric_filename="abutments_wingwalls_shearkeys.yaml",
        prompt_filename="components/abutments_wingwalls_shearkeys.md",
    ),
}


def list_components() -> list[ComponentSpec]:
    """Stable ordering for GUI display."""
    return [DEFAULT_COMPONENTS[k] for k in DEFAULT_COMPONENTS.keys()]


def get_component(component_id: str) -> ComponentSpec:
    try:
        return DEFAULT_COMPONENTS[component_id]
    except KeyError as e:
        raise KeyError(f"Unknown component_id={component_id!r}. Valid: {sorted(DEFAULT_COMPONENTS)}") from e


def register_component(spec: ComponentSpec) -> None:
    """
    Extension point.
    Later we can evolve this into a plugin mechanism; for now this enables adding items in code.
    """
    if spec.id in DEFAULT_COMPONENTS:
        raise ValueError(f"Component {spec.id!r} already exists.")
    # type: ignore[misc]
    DEFAULT_COMPONENTS[spec.id] = spec 


def iter_component_ids() -> Iterable[str]:
    return DEFAULT_COMPONENTS.keys()
