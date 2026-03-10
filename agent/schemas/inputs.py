from typing import Dict, List, Optional, Tuple
from typing_extensions import Literal
from pydantic import BaseModel, Field, ConfigDict

GridSystem = Literal["ieee14", "ieee24", "ieee30", "ieee39", "ieee57", "ieee118", "ieee300"]
InputParameter = Literal[
    "grid",
    "bus_id",
    "step_size",
    "max_scale",
    "power_factor",
    "voltage_limit",
    "capacitive",
    "continuation",
    "contingency_lines",
    "gen_voltage_setpoints",
]

class Inputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grid: GridSystem = "ieee39"
    bus_id: int = Field(default=5, ge=0, le=300)
    step_size: float = Field(default=0.01, gt=0, le=0.1)
    max_scale: float = Field(default=3.0, gt=1.0, le=10.0)
    power_factor: float = Field(default=0.95, gt=0, le=1.0)
    voltage_limit: float = Field(default=0.4, gt=0, le=1.0)
    capacitive: bool = Field(default=False)
    continuation: bool = Field(default=True)
    # N-1 / N-k: list of (from_bus, to_bus) pairs, 1-based; e.g. [(2, 3), (3, 4)]
    contingency_lines: Optional[List[Tuple[int, int]]] = Field(default=None)
    # Override generator voltage setpoints before sweep; 1-based gen index -> vm_pu; e.g. {1: 1.05}
    gen_voltage_setpoints: Optional[Dict[int, float]] = Field(default=None)

