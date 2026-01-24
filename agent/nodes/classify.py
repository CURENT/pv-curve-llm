from agent.state.app_state import State
from agent.schemas.classifier import MessageClassifier
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def classify_message(state: State, llm, prompts):
    
    display_executing_node("classifier")

    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)
    
    result = classifier_llm.invoke([
        {"role": "system", "content": prompts["classifier"]["system"]},
        {"role": "user", "content": last_message.content}
    ])
    
    node_response = NodeResponse(
        node_type="classifier",
        success=True,
        data={"message_type": result.message_type},
        message=f"Classified as: {result.message_type}",
        timestamp=datetime.now()
    )
    return {"message_type": result.message_type, "node_response": node_response}

