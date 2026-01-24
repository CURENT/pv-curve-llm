from agent.state.app_state import State
from agent.utils.display import display_executing_node

def advance_step(state: State):
    
    display_executing_node("advance_step")

    current_step = state.get("current_step", 0)
    plan = state.get("plan")
    step_results = state.get("step_results", [])
    
    if state.get("messages"):
        last_message = state["messages"][-1]
        result_preview = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        current_step_action = plan.steps[current_step].action if plan and current_step < len(plan.steps) else "unknown"
        
        step_results.append({
            "step": current_step,
            "action": current_step_action,
            "result": last_message.content if hasattr(last_message, 'content') else str(last_message)
        })
    
    next_step = current_step + 1
    
    return {
        "current_step": next_step,
        "step_results": step_results,
        "next": "step_controller" if plan and next_step < len(plan.steps) else "summary"
    }

