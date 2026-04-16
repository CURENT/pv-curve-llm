from pydantic import BaseModel
from typing import Optional, Dict, List, Tuple
from agent.schemas.inputs import Inputs, GridSystem


class ParametersResponse(BaseModel):
    """Current parameter state for a session."""
    session_id: str
    parameters: Inputs


class ParametersUpdateRequest(BaseModel):
    """Partial update — only the fields the user wants to change."""
    session_id: str
    grid: Optional[GridSystem] = None
    bus_id: Optional[int] = None
    step_size: Optional[float] = None
    max_scale: Optional[float] = None
    power_factor: Optional[float] = None
    voltage_limit: Optional[float] = None
    capacitive: Optional[bool] = None
    continuation: Optional[bool] = None
    contingency_lines: Optional[List[Tuple[int, int]]] = None
    gen_voltage_setpoints: Optional[Dict[int, float]] = None
