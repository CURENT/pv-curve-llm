from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def router(state: State):
    
    display_executing_node("router")
    
    message_type = state.get("message_type", "question_general")
    last_message = state["messages"][-1] if state.get("messages") else None
    user_input = last_message.content.lower() if last_message and hasattr(last_message, 'content') else ""
    
    multi_step_keywords = ["then", "after that", "next", "also", "and then", "followed by", "after"]
    comparison_patterns = ["compare", "versus", "vs", "both", "different", "multiple"]
    
    is_multi_step = any(keyword in user_input for keyword in multi_step_keywords)
    is_comparison = any(pattern in user_input for pattern in comparison_patterns)
    has_multiple_actions = user_input.count("set ") > 1 or user_input.count("change ") > 1 or user_input.count("generate") > 0 and ("set" in user_input or "change" in user_input)
    
    needs_planning = is_multi_step or (is_comparison and has_multiple_actions)
    
    if needs_planning:
        next_node = "planner"
        is_compound = True
    elif message_type in ["question_general", "question_parameter"]:
        next_node = message_type
        is_compound = False
    elif message_type == "parameter":
        next_node = "parameter"
        is_compound = False
    elif message_type == "generation":
        next_node = "generation"
        is_compound = False
    elif message_type == "analysis":
        next_node = "analysis"
        is_compound = False
    else:
        next_node = "question_general"
        is_compound = False
    
    node_response = NodeResponse(
        node_type="router",
        success=True,
        data={"next": next_node, "message_type": message_type, "is_compound": is_compound},
        message=f"Routing to: {next_node}",
        timestamp=datetime.now()
    )
    return {"next": next_node, "is_compound": is_compound, "node_response": node_response}

