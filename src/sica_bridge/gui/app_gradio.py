from __future__ import annotations

import gradio as gr

from sica_bridge.assess import assess_component_many, aggregate_component, aggregate_event
from sica_bridge.llm.openai_client import OpenAIVisionClient
from sica_bridge.registry import list_components
from sica_bridge.schemas import ComponentAssessment

from dotenv import load_dotenv
load_dotenv()

def _read_gradio_files(files) -> list[tuple[bytes, str | None, str]]:
    """
    Gradio File returns objects with .name (path). We'll read bytes from disk.
    """
    photos: list[tuple[bytes, str | None, str]] = []
    if not files:
        return photos

    for f in files:
        path = f.name  # filepath
        with open(path, "rb") as fp:
            b = fp.read()
        # crude mime guess
        mt = "image/jpeg"
        if path.lower().endswith(".png"):
            mt = "image/png"
        photos.append((b, path.split("/")[-1], mt))
    return photos


def _format_component_results(component_id: str, assessments: list[ComponentAssessment]) -> str:
    overall = aggregate_component(assessments)
    lines = [f"## {component_id}", f"**Overall:** {overall.value}", ""]
    for a in assessments:
        lines.append(f"- {a.notes or a.component_id}: **{a.r_state.value}** — {a.reason}")
    return "\n".join(lines)


def run_assessment(approaches_files, columns_files, joints_files, abutments_files) -> str:
    client = client = OpenAIVisionClient()

    component_inputs = {
        "approaches": _read_gradio_files(approaches_files),
        "columns": _read_gradio_files(columns_files),
        "joints_hinges": _read_gradio_files(joints_files),
        "abutments_wingwalls_shearkeys": _read_gradio_files(abutments_files),
    }

    all_assessments: list[ComponentAssessment] = []
    report_sections: list[str] = []

    for cid, photos in component_inputs.items():
        if not photos:
            continue
        results = assess_component_many(component_id=cid, photos=photos, client=client)
        all_assessments.extend(results)
        report_sections.append(_format_component_results(cid, results))

    if not all_assessments:
        return "No photos uploaded."

    ev = aggregate_event(all_assessments)
    header = f"# Event Overall: {ev.overall_r_state.value}\n"
    return header + "\n\n".join(report_sections)


def main():
    comps = list_components()

    with gr.Blocks(title="sica-bridge") as demo:
        gr.Markdown("# sica-bridge — post-earthquake visual inspection (Option A)")

        with gr.Row():
            approaches = gr.File(label="Approaches (upload 1+ photos)", file_count="multiple")
            columns = gr.File(label="Columns (upload 1+ photos)", file_count="multiple")

        with gr.Row():
            joints = gr.File(label="Intermediate Deck Joints & Hinges (upload 1+ photos)", file_count="multiple")
            abutments = gr.File(label="Abutments, Wingwalls, & Shear Keys (upload 1+ photos)", file_count="multiple")

        run_btn = gr.Button("Run assessment")
        out = gr.Markdown()

        run_btn.click(
            fn=run_assessment,
            inputs=[approaches, columns, joints, abutments],
            outputs=[out],
        )

    demo.launch()


if __name__ == "__main__":
    main()
