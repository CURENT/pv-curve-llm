from langchain_core.messages import AIMessage
from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def summary_agent(state: State):
    
    display_executing_node("summary")
    
    plan = state.get("plan")
    step_results = state.get("step_results", [])

    summary_parts = [f"Completed multi-step request: {plan.description if plan else 'Unknown'}\n"]

    for i, result in enumerate(step_results):
        step_info = plan.steps[i] if plan and i < len(plan.steps) else None
        action_name = step_info.action if step_info else result.get("action", "unknown")
        result_text = result['result'][:100] + "..." if len(result['result']) > 100 else result['result']
        summary_parts.append(f"Step {i+1} ({action_name}): {result_text}")

    summary = "\n".join(summary_parts)
    reply = AIMessage(content=summary)

    node_response = NodeResponse(
        node_type="summary",
        success=True,
        data={
            "summary": summary,
            "steps_completed": len(step_results),
            "plan_description": plan.description if plan else "Unknown"
        },
        message=summary,
        timestamp=datetime.now()
    )
    return {"messages": [reply], "node_response": node_response}

