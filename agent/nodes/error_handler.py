from langchain_core.messages import AIMessage
from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def error_handler_agent(state: State, llm, prompts):
    
    display_executing_node("error_handler")

    error_info = state.get("error_info", {})
    retry_count = state.get("retry_count", 0)
    failed_node = state.get("failed_node")

    if retry_count < 2 and error_info.get("error_type") in ["simulation_error", "validation_error"]:
        
        if error_info.get("error_type") == "simulation_error":
            current_inputs = state["inputs"]
            corrected_inputs = current_inputs.model_copy()
            
            error_msg = error_info.get("error_message", "").lower()
            if "unsupported grid" in error_msg or "grid" in error_msg:
                if "39" in error_msg:
                    corrected_inputs = corrected_inputs.model_copy(update={"grid": "ieee39"})
                elif "14" in error_msg:
                    corrected_inputs = corrected_inputs.model_copy(update={"grid": "ieee14"})
                elif "118" in error_msg:
                    corrected_inputs = corrected_inputs.model_copy(update={"grid": "ieee118"})
            
            if "bus" in error_msg and "out of range" in error_msg:
                corrected_inputs = corrected_inputs.model_copy(update={"bus_id": 0})

            return {
                "inputs": corrected_inputs,
                "retry_count": retry_count + 1,
                "error_info": None,
                "retry_node": failed_node
            }
    
    error_context = f"""
Error Type: {error_info.get('error_type', 'unknown')}
Error Message: {error_info.get('error_message', 'No message available')}
Context: {error_info.get('context', 'No context available')}

Current Inputs: {error_info.get('current_inputs', 'Not available')}
User Input: {error_info.get('user_input', 'Not available')}
Additional Info: {error_info.get('validation_errors', 'None')}
"""
    
    messages = [
        {"role": "system", "content": prompts["error_handler"]["system"]},
        {"role": "user", "content": prompts["error_handler_user"]["user"].format(error_context=error_context)}
    ]

    reply = llm.invoke(messages)

    node_response = NodeResponse(
        node_type="error_handler",
        success=True,
        data={"error_resolved": True, "error_type": error_info.get('error_type', 'unknown')},
        message=reply.content,
        timestamp=datetime.now()
    )
    return {"messages": [reply], "retry_count": 0, "failed_node": None, "node_response": node_response}

