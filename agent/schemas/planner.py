from typing_extensions import Literal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class StepParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    grid: Optional[str] = Field(None, description="Grid system (e.g., ieee14, ieee118)")
    bus_id: Optional[int] = Field(None, description="Bus ID to monitor")
    step_size: Optional[float] = Field(None, description="Load increment step size")
    max_scale: Optional[float] = Field(None, description="Maximum load multiplier")
    power_factor: Optional[float] = Field(None, description="Power factor")
    voltage_limit: Optional[float] = Field(None, description="Voltage threshold")
    capacitive: Optional[bool] = Field(None, description="Load type - true for capacitive")
    continuation: Optional[bool] = Field(None, description="Curve type - true for continuous")

class StepType(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    action: Literal["question", "parameter", "generation", "analysis"] = Field(..., description="The type of action to perform")
    content: str = Field(..., description="The specific content for this step")
    parameters: Optional[StepParameters] = Field(None, description="Parameters for this step if it's a parameter modification")

class MultiStepPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    steps: List[StepType] = Field(..., description="Sequence of steps to execute")
    description: str = Field(..., description="Brief description of the overall plan")

