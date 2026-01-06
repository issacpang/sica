from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

# Issac
class RState(str, Enum):
    R1 = "R1"  # Open
    R2 = "R2"  # Open but inspection needed
    R3 = "R3"  # Close but inspection needed
    R4 = "R4"  # Close immediately


class ComponentAssessment(BaseModel):
    component_id: str = Field(..., description="Registry id, e.g. 'columns'")
    r_state: RState
    reason: str = Field(..., min_length=1, description="Why the photo maps to the chosen R_state")

    # Optional: keep room for the future without changing the contract
    notes: str | None = None


class EventAssessment(BaseModel):
    """
    Result for a full inspection event.
    Overall r_state should be the worst-case (max severity) among components.
    """
    overall_r_state: RState
    components: list[ComponentAssessment]
