from agent.models.state_models import Inputs

def format_inputs_display(inputs: Inputs) -> str:
    param_labels = {
        "grid": "Grid system",
        "bus_id": "Bus to monitor voltage",
        "step_size": "Load increment step size",
        "max_scale": "Maximum load multiplier",
        "power_factor": "Power factor",
        "voltage_limit": "Voltage threshold to stop",
        "capacitive": "Load type",
        "continuation": "Curve type"
    }
    
    formatted_lines = []
    for param, value in inputs.model_dump().items():
        label = param_labels.get(param, param)
        
        # Display the parameter in a more readable format
        if param == "capacitive":
            display_value = "Capacitive" if value else "Inductive"
        elif param == "continuation":
            display_value = "Continuous" if value else "Stops at nose point"
        elif param == "grid":
            display_value = value.upper()
        else:
            display_value = str(value)
            
        formatted_lines.append(f"{label}: {display_value}")
    
    return "\n".join(formatted_lines)

def create_initial_state():
    from agent.models.state_models import Inputs
    return {
        "messages": [], 
        "message_type": None, 
        "inputs": Inputs(), 
        "results": None, 
        "error_info": None,
        "plan": None,
        "current_step": 0,
        "step_results": [],
        "is_compound": False,
        "retry_count": 0,
        "failed_node": None,
        "conversation_history": [],
        "cached_results": [],
        # Enhanced history context fields
        "parameter_evolution": [],
        "simulation_trends": [],
        "user_preferences": {},
        "context_summary": ""
    }

def validate_state(state) -> dict[str, bool]:
    """Basic state validation"""
    validations = {
        "has_inputs": state.get("inputs") is not None,
        "valid_step_index": state.get("current_step", 0) >= 0,
        "valid_compound_flag": isinstance(state.get("is_compound"), bool)
    }
    
    if state.get("plan"):
        validations["valid_plan"] = len(state["plan"].steps) > 0
        validations["step_in_bounds"] = state.get("current_step", 0) <= len(state["plan"].steps)
    
    return validations 