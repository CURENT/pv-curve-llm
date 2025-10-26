from typing_extensions import Literal
from pydantic import BaseModel, Field, ConfigDict

class MessageClassifier(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    message_type: Literal["question_general", "question_parameter", "parameter", "generation"] = Field(
        ...,
        description="Classify the message into one category: question_general (educational questions), question_parameter (questions about parameters), parameter (modify settings), or generation (run PV curve)."
    )

