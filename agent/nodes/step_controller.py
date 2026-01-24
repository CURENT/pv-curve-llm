from langchain_core.messages import AIMessage, HumanMessage
from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def step_controller(state: State):
    
    display_executing_node("step_controller")
    
    plan = state.get("plan")
    current_step = state.get("current_step", 0)
    
    if not plan or current_step >= len(plan.steps):
        return {"next": "summary"}
    
    step = plan.steps[current_step]

    if step.action == "parameter" and step.parameters:
        current_inputs = state["inputs"]
        updates = {}
        reply_parts = []
        
        param_dict = step.parameters.model_dump(exclude_none=True)
        for param, value in param_dict.items():
            converted_value = value
            if param == "grid":
                value_str = str(value).lower().replace(" ", "").replace("_", "")
                if "14" in value_str:
                    converted_value = "ieee14"
                elif "24" in value_str:
                    converted_value = "ieee24"
                elif "30" in value_str:
                    converted_value = "ieee30"
                elif "39" in value_str:
                    converted_value = "ieee39"
                elif "57" in value_str:
                    converted_value = "ieee57"
                elif "118" in value_str:
                    converted_value = "ieee118"
                elif "300" in value_str:
                    converted_value = "ieee300"
                else:
                    converted_value = value
            elif param in ["bus_id"]:
                converted_value = int(value)
            elif param in ["step_size", "max_scale", "power_factor", "voltage_limit"]:
                converted_value = float(value)
            elif param in ["capacitive", "continuation"]:
                if isinstance(value, str):
                    converted_value = value.lower() in ["true", "yes", "1", "on"]
                else:
                    converted_value = bool(value)
            
            updates[param] = converted_value
            reply_parts.append(f"{param} to {converted_value}")
        
        new_inputs = current_inputs.model_copy(update=updates)
        
        if len(reply_parts) == 1:
            reply_content = f"Updated {reply_parts[0]}"
        else:
            reply_content = f"Updated {len(reply_parts)} parameters:\n" + "\n".join(f"• {part}" for part in reply_parts)

        reply = AIMessage(content=reply_content)
        node_response = NodeResponse(
            node_type="step_controller",
            success=True,
            data={
                "step_executed": "parameter",
                "updated_parameters": list(updates.keys()),
                "current_inputs": new_inputs.model_dump()
            },
            message=reply_content,
            timestamp=datetime.now()
        )
        return {"messages": [reply], "inputs": new_inputs, "next": "advance_step", "node_response": node_response}

    step_message = HumanMessage(content=step.content)
    
    if step.action == "question":
        return {"messages": [step_message], "message_type": "question", "next": "question_general"}
    else:
        return {"messages": [step_message], "message_type": step.action, "next": step.action}

