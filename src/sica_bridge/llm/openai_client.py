from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI

from sica_bridge.llm.client import VisionInput, VisionLLMClient


def _to_data_url(image_bytes: bytes, mime_type: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


@dataclass
class OpenAIVisionClient(VisionLLMClient):
    """
    OpenAI Responses API implementation.

    API key is read from environment variable OPENAI_API_KEY.
    """
    model: str = "gpt-4.1-mini"
    detail: str = "auto"

    def __post_init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set it before running the application."
            )

        self._client = OpenAI(api_key=api_key)

        # Optional override via env (nice for experiments)
        self.model = os.getenv("SICA_OPENAI_MODEL", self.model)

    def _build_input(self, prompt: str, images: list[VisionInput]) -> list[Dict[str, Any]]:
        content: List[Dict[str, Any]] = [{"type": "input_text", "text": prompt}]

        for im in images:
            content.append(
                {
                    "type": "input_image",
                    "image_url": _to_data_url(im.image_bytes, im.mime_type),
                    "detail": self.detail,
                }
            )

        return [{"role": "user", "content": content}]

    def complete_json(self, *, prompt: str, images: list[VisionInput]) -> str:
        resp = self._client.responses.create(
            model=self.model,
            input=self._build_input(prompt, images),
        )
        return (resp.output_text or "").strip()
