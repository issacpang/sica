from __future__ import annotations

from pathlib import Path
from typing import List
from dotenv import load_dotenv
from sica_bridge.assess import assess_component_many, aggregate_component, aggregate_event
from sica_bridge.llm.openai_client import OpenAIVisionClient

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

import json
import uuid
from datetime import datetime, timezone
from fastapi import Body


load_dotenv()

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"

def _find_project_root(start: Path) -> Path:
    # Try to locate repo root by common markers; fallback to parent of gui folder
    for p in [start, *start.parents]:
        if (p / "pyproject.toml").exists() or (p / ".git").exists():
            return p
    return start.parent 

PROJECT_ROOT = _find_project_root(HERE)
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SICA GUI Server", version="0.1")

# Serve /static/* from the same folder
app.mount("/static", StaticFiles(directory=str(HERE)), name="static")


@app.get("/")
def root():
    return FileResponse(str(INDEX))


def _pack_uploads(files: List[UploadFile]) -> list[tuple[bytes, str | None, str]]:
    """
    Convert UploadFile list -> [(bytes, filename, mimetype), ...]
    format expected by your assess_component_many()
    """
    packed: list[tuple[bytes, str | None, str]] = []
    for f in files or []:
        content = f.file.read()
        mt = f.content_type or "application/octet-stream"
        packed.append((content, f.filename, mt))
    return packed


def _assessment_to_dict(a, *, filename: str | None, photo_index: int) -> dict:
    return {
        "photo_index": photo_index,
        "filename": filename,
        # keep "photo" for backward compat with your frontend renderer
        "photo": filename or f"Photo {photo_index}",
        "r_state": getattr(a.r_state, "value", "UNKNOWN"),
        "reason": getattr(a, "reason", ""),
        "notes": getattr(a, "notes", None),
    }



@app.post("/api/assess")
def api_assess(
    # IMPORTANT: field names must match what frontend sends
    approaches: List[UploadFile] = File(default=[]),
    columns: List[UploadFile] = File(default=[]),
    joints_hinges: List[UploadFile] = File(default=[]),
    abutments_wingwalls_shearkeys: List[UploadFile] = File(default=[]),
):
    client = OpenAIVisionClient()

    component_inputs = {
        "approaches": _pack_uploads(approaches),
        "columns": _pack_uploads(columns),
        "joints_hinges": _pack_uploads(joints_hinges),
        "abutments_wingwalls_shearkeys": _pack_uploads(abutments_wingwalls_shearkeys),
    }

    all_assessments = []
    components_out = {}

    for cid, photos in component_inputs.items():
        if not photos:
            continue

        results = assess_component_many(component_id=cid, photos=photos, client=client)
        all_assessments.extend(results)

        comp_overall = aggregate_component(results)

        items = []
        for idx, (r, (_, fname, _)) in enumerate(zip(results, photos), start=1):
            items.append(_assessment_to_dict(r, filename=fname, photo_index=idx))

        components_out[cid] = {
            "overall_r_state": getattr(comp_overall, "value", "UNKNOWN"),
            "items": items,
        }

    if not all_assessments:
        return JSONResponse(
            status_code=400,
            content={"error": "No photos uploaded."},
        )

    event = aggregate_event(all_assessments)
    overall = getattr(event.overall_r_state, "value", "UNKNOWN")

    total_photos = sum(len(v) for v in component_inputs.values())
    used_components = sum(1 for v in component_inputs.values() if v)

    return {
        "overall_r_state": overall,
        "kpis": {"components_assessed": used_components, "photos_analyzed": total_photos},
        "components": components_out,
    }

@app.post("/api/save_result")
def api_save_result(payload: dict = Body(...)):
    # Save JSON under <project_root>/results/
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fname = f"assessment_{ts}_{uuid.uuid4().hex[:8]}.json"
    out_path = RESULTS_DIR / fname

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"saved": True, "filename": fname, "path": str(out_path)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
