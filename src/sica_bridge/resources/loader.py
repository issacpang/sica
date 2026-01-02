from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from sica_bridge.registry import get_component
from sica_bridge.llm.client import VisionInput


def repo_root() -> Path:
    """
    Assumes this file lives at: src/sica_bridge/resources/loader.py
    Repo root is three parents up from src/sica_bridge/resources.
    """
    return Path(__file__).resolve().parents[3]


def rubrics_dir() -> Path:
    return repo_root() / "rubrics"


def prompts_dir() -> Path:
    return repo_root() / "prompts"


def load_rubric(component_id: str) -> Dict[str, Any]:
    spec = get_component(component_id)
    path = rubrics_dir() / spec.rubric_filename
    if not path.exists():
        raise FileNotFoundError(f"Rubric not found for {component_id}: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise TypeError(f"Rubric file must be a YAML mapping/dict: {path}")
    return data


def load_prompt_template(component_id: str) -> str:
    spec = get_component(component_id)
    path = prompts_dir() / spec.prompt_filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found for {component_id}: {path}")
    return path.read_text(encoding="utf-8")


def load_system_prompt() -> str:
    path = prompts_dir() / "system.md"
    if not path.exists():
        raise FileNotFoundError(f"System prompt not found: {path}")
    return path.read_text(encoding="utf-8")

def damage_examples_dir() -> Path:
    return repo_root() / "assets" / "damage_examples"


def _infer_mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    return "application/octet-stream"


def load_reference_images(component_id: str, limit: int | None = None) -> list[VisionInput]:
    """
    Load preset reference images from:
      assets/reference_examples/<component_id>/

    Returns VisionInput(role="reference") entries with captions from meta.yaml if present.
    """
    folder = damage_examples_dir() / component_id
    if not folder.exists():
        return []

    meta_path = folder / "meta.yaml"
    captions: dict[str, str] = {}

    if meta_path.exists():
        with meta_path.open("r", encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}
        for item in (meta.get("examples") or []):
            if isinstance(item, dict) and "file" in item:
                captions[str(item["file"])] = str(item.get("caption") or "")

    # Prefer ordering from meta.yaml; otherwise load all images
    if captions:
        files = [folder / fname for fname in captions.keys() if (folder / fname).exists()]
    else:
        files = sorted([p for p in folder.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])

    if limit is not None:
        files = files[:limit]

    refs: list[VisionInput] = []
    for p in files:
        refs.append(
            VisionInput(
                image_bytes=p.read_bytes(),
                mime_type=_infer_mime_type(p),
                filename=p.name,
                role="reference",
                caption=captions.get(p.name) or p.name,
            )
        )
    return refs