## Adding a new LLM provider (Gemini, Llama, etc.)

SICA Bridge is designed so you can swap LLM providers **without changing the assessment pipeline**.
To add a new provider, implement the `VisionLLMClient` interface and return **JSON-only text**
matching the `ComponentAssessment` schema.

---

### 1) Create a new client file

Add a new module under:

```
src/sica_bridge/llm/
```

Example filenames:

- `gemini_client.py`
- `llama_client.py` (for open-source models via a local server)

---

### 2) Implement the provider-agnostic interface

Your client must implement:

```
complete_json(prompt: str, images: list[VisionInput]) -> str
```

Rules:

- Return **one JSON object** as **plain text**
- Do **not** include markdown fences
- Preserve image order (inspection images first, references after)

Minimal template:

```python
from __future__ import annotations
from dataclasses import dataclass
import os

from sica_bridge.llm.client import VisionLLMClient, VisionInput

@dataclass
class MyVisionClient(VisionLLMClient):
    model: str = "my-default-model"

    def __post_init__(self) -> None:
        self.model = os.getenv("SICA_MYPROVIDER_MODEL", self.model)

    def complete_json(self, prompt: str, images: list[VisionInput]) -> str:
        """Return a JSON object as plain text (no markdown)."""
        # 1) Convert VisionInput -> provider-specific image format
        # 2) Send prompt + images to provider
        # 3) Return raw JSON string
        raise NotImplementedError
```

---

### 3) Configuration conventions (recommended)

All providers should follow the same conventions:

- Secrets via environment variables
- Optional model override via `SICA_<PROVIDER>_MODEL`

Examples:

| Provider | Environment variables |
|--------|-----------------------|
| OpenAI | `OPENAI_API_KEY`, `SICA_OPENAI_MODEL` |
| Gemini | `GEMINI_API_KEY`, `SICA_GEMINI_MODEL` |
| Llama (local server) | `SICA_LLAMA_ENDPOINT`, `SICA_LLAMA_MODEL` |

---

### 4) Using your new provider

All assessment functions accept a `client=` argument:

```python
from sica_bridge.assess import assess_component
from sica_bridge.llm.gemini_client import GeminiVisionClient

client = GeminiVisionClient(model="gemini-1.5-pro")

out = assess_component(
    component_id="columns",
    image_bytes=open("column.jpg", "rb").read(),
    mime_type="image/jpeg",
    filename="column.jpg",
    client=client,
)
```

---

### 5) Example: Gemini client (skeleton)

Create `src/sica_bridge/llm/gemini_client.py`:

```python
from __future__ import annotations
from dataclasses import dataclass
import os

from sica_bridge.llm.client import VisionLLMClient, VisionInput

@dataclass
class GeminiVisionClient(VisionLLMClient):
    model: str = "gemini-1.5-pro"

    def __post_init__(self) -> None:
        self.api_key = os.environ["GEMINI_API_KEY"]
        self.model = os.getenv("SICA_GEMINI_MODEL", self.model)
        # Initialize Gemini SDK here

    def complete_json(self, prompt: str, images: list[VisionInput]) -> str:
        # Convert images to Gemini parts
        # Call Gemini with prompt + images
        # Return JSON-only string
        raise NotImplementedError
```

---

### 6) Example: Open-source Llama via local inference server

For open-source models, a common pattern is to run a **local inference server**
(e.g., vLLM, llama.cpp) and write a thin HTTP client.

```python
from __future__ import annotations
from dataclasses import dataclass
import os
import requests

from sica_bridge.llm.client import VisionLLMClient, VisionInput

@dataclass
class LlamaVisionClient(VisionLLMClient):
    endpoint: str
    model: str = "llama-vision"

    def __post_init__(self) -> None:
        self.endpoint = os.getenv("SICA_LLAMA_ENDPOINT", self.endpoint)
        self.model = os.getenv("SICA_LLAMA_MODEL", self.model)

    def complete_json(self, prompt: str, images: list[VisionInput]) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
        }
        r = requests.post(self.endpoint, json=payload, timeout=60)
        r.raise_for_status()
        return r.text
```

---


