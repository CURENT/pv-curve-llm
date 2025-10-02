from typing_extensions import TypedDict, Annotated, Literal
from typing import Union, List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

GridSystem = Literal["ieee14", "ieee24", "ieee30", "ieee39", "ieee57", "ieee118", "ieee300"]
InputParameter = Literal["grid", "bus_id", "step_size", "max_scale", "power_factor", "voltage_limit", "capacitive", "continuation"]

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

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None
    inputs: Inputs
    results: dict | None
    error_info: dict | None
    plan: Optional[Any]  # MultiStepPlan type
    current_step: int
    step_results: List[dict]
    is_compound: bool
    retry_count: int
    failed_node: str | None
    conversation_history: List[dict]
    cached_results: List[dict]
    # Enhanced history context fields
    parameter_evolution: List[dict]  # Track parameter changes over time
    simulation_trends: List[dict]  # Track simulation patterns and trends
    user_preferences: Dict[str, Any]  # Learn user preferences from history
    context_summary: str  # Current context summary for quick reference 