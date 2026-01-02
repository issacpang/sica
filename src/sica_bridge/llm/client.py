from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Optional, Literal

ImageRole = Literal["query", "reference"]

@dataclass(frozen=True)
class VisionInput:
    """
    Represents one image to analyze.
    The model will receive images in the given order.
    """
    image_bytes: bytes
    mime_type: str = "image/jpeg"
    filename: Optional[str] = None

    # NEW: help the prompt explain what each image is
    role: ImageRole = "query"          # "query" or "reference"
    caption: Optional[str] = None      # e.g., "Example: diagonal shear cracking"

class VisionLLMClient(abc.ABC):
    """
    Provider-agnostic interface.
    Implementations will call OpenAI / Anthropic / etc.
    """

    @abc.abstractmethod
    def complete_json(self, *, prompt: str, images: list[VisionInput]) -> str:
        """
        Returns the model's raw text output (expected to be JSON text).
        """
        raise NotImplementedError


class FakeVisionLLMClient(VisionLLMClient):
    """
    Deterministic fake for tests/dev without network.
    """

    def __init__(self, json_text: str):
        self._json_text = json_text

    def complete_json(self, *, prompt: str, images: VisionInput) -> str:
        # ignore prompt/image; return deterministic stub
        return self._json_text
