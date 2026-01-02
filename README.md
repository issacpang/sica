# sica-bridge

<p align="center">
  <img src="image/sica_logo.svg" alt="SICA logo" width="300"/>
</p>

**SICA** = **S**tructure **I**nvestigation and **C**ondition **A**ssessment.

`sica-bridge` is a Python package that uses a vision-capable LLM to perform **post-earthquake visual inspection** from photos and to **support rapid decision-making** for bridge safety assessment.
It outputs an **R-state** (R1–R4) and a **short reason** per photo, then aggregates results to component-level and event-level summaries that can be used to **prioritize inspections, closures, and follow-up actions**.

> Current scope: 4 component categories (approaches, columns, joints/hinges, abutments/wingwalls/shear keys).
