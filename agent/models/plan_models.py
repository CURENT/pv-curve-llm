from typing_extensions import Literal
from typing import Union, List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MessageClassifier(BaseModel):
    message_type: Literal["question", "parameter", "generation"] = Field(
        ...,
        description="Classify if the message requires a parameter modification, a PV-curve generation/run, or a question/request that requires a knowledge response."
    )

class QuestionClassifier(BaseModel):
    question_type: Literal["question_general", "question_parameter"] = Field(
        ...,
        description="Classify if the question is a general voltage stability/PV curve question or specifically about parameter meanings/functionality."
    )

class ParameterModification(BaseModel):
    parameter: str = Field(..., description="The parameter to modify")
    value: Union[str, float, int, bool] = Field(..., description="The new value for the parameter")

class InputModifier(BaseModel):
    modifications: List[ParameterModification] = Field(..., description="List of parameter modifications to apply")

class StepType(BaseModel):
    action: Literal["question", "parameter", "generation"] = Field(..., description="The type of action to perform")
    content: str = Field(..., description="The specific content for this step")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for this step if it's a parameter modification")

class MultiStepPlan(BaseModel):
    steps: List[StepType] = Field(..., description="Sequence of steps to execute")
    description: str = Field(..., description="Brief description of the overall plan")

class CompoundMessageClassifier(BaseModel):
    message_type: Literal["simple", "compound"] = Field(
        ...,
        description="Classify if the message is a simple single action or a compound multi-step request"
    ) 