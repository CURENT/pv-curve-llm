from langchain_core.messages import AIMessage
from agent.state.app_state import State
from agent.schemas.parameter import InputModifier
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def parameter_agent(state: State, llm, prompts):
    
    display_executing_node("parameter")
    
    last_message = state["messages"][-1]
    modifier_llm = llm.with_structured_output(InputModifier)
    current_inputs = state["inputs"]
    
    result = modifier_llm.invoke([
        {"role": "system", "content": prompts["parameter_agent"]["system"].format(current_inputs=current_inputs)},
        {"role": "user", "content": last_message.content}
    ])
    
    updates = {}
    reply_parts = []

    if not result.modifications:
        reply_content = "No parameter changes detected"
        reply = AIMessage(content=reply_content)
        node_response = NodeResponse(
            node_type="parameter",
            success=True,
            data={"updated_parameters": [], "current_inputs": current_inputs.model_dump()},
            message=reply_content,
            timestamp=datetime.now()
        )
        return {"messages": [reply], "node_response": node_response}

    for modification in result.modifications:
        converted_value = modification.value
        if modification.parameter in ["bus_id"]:
            converted_value = int(modification.value)
        elif modification.parameter in ["step_size", "max_scale", "power_factor", "voltage_limit"]:
            converted_value = float(modification.value)
        elif modification.parameter in ["capacitive", "continuation"]:
            if isinstance(modification.value, str):
                converted_value = modification.value.lower() in ["true", "yes", "1", "on"]
            else:
                converted_value = bool(modification.value)
        
        updates[modification.parameter] = converted_value
        reply_parts.append(f"{modification.parameter} to {converted_value}")
    
    new_inputs = current_inputs.model_copy(update=updates)
    
    if len(reply_parts) == 1:
        reply_content = f"Updated {reply_parts[0]}"
    else:
        reply_content = f"Updated {len(reply_parts)} parameters:\n" + "\n".join(f"• {part}" for part in reply_parts)

    reply = AIMessage(content=reply_content)
    node_response = NodeResponse(
        node_type="parameter",
        success=True,
        data={
            "updated_parameters": list(updates.keys()),
            "current_inputs": new_inputs.model_dump(),
            "changes": updates
        },
        message=reply_content,
        timestamp=datetime.now()
    )
    return {"messages": [reply], "inputs": new_inputs, "node_response": node_response}

