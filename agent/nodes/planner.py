from agent.state.app_state import State
from agent.schemas.planner import MultiStepPlan
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node

def planner_agent(state: State, llm, prompts):
    display_executing_node("planner")
    
    last_message = state["messages"][-1]
    current_inputs = state.get("inputs")
    
    inputs_context = ""
    if current_inputs:
        inputs_dict = current_inputs.model_dump() if hasattr(current_inputs, 'model_dump') else current_inputs
        inputs_context = f"\n\n**CRITICAL: Current Parameters Already Exist:**\n"
        inputs_context += f"- Grid: {inputs_dict.get('grid')}\n"
        inputs_context += f"- Bus ID: {inputs_dict.get('bus_id')}\n"
        inputs_context += f"- Power Factor: {inputs_dict.get('power_factor')}\n"
        inputs_context += f"- Step Size: {inputs_dict.get('step_size')}\n"
        inputs_context += f"- Max Scale: {inputs_dict.get('max_scale')}\n"
        inputs_context += f"- Voltage Limit: {inputs_dict.get('voltage_limit')}\n"
        inputs_context += f"- Load Type: {'Capacitive' if inputs_dict.get('capacitive') else 'Inductive'}\n"
        inputs_context += f"- Curve Type: {'Continuous' if inputs_dict.get('continuation') else 'Stops at nose point'}\n"
    
    planner_llm = llm.with_structured_output(MultiStepPlan)
    
    result = planner_llm.invoke([
        {"role": "system", "content": prompts["planner"]["system"] + inputs_context},
        {"role": "user", "content": prompts["planner"]["user"].format(user_input=last_message.content)}
    ])

    node_response = NodeResponse(
        node_type="planner",
        success=True,
        data={
            "plan_description": result.description,
            "steps_count": len(result.steps),
            "plan": result.model_dump()
        },
        message=f"Plan created with {len(result.steps)} steps: {result.description}",
        timestamp=datetime.now()
    )
    return {"plan": result, "current_step": 0, "step_results": [], "node_response": node_response}

