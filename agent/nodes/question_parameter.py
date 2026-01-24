from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from agent.utils.context import get_conversation_context
from datetime import datetime
from agent.utils.display import display_executing_node

def question_parameter_agent(state: State, llm, prompts):
    
    display_executing_node("question_parameter")
    
    last_message = state["messages"][-1]
    
    recent_exchanges = get_conversation_context(state, max_exchanges=3)
    parameter_context = ""
    
    if recent_exchanges:
        parameter_context = "\n\n**Previous Parameter Discussions:**\n"
        
        for i, exchange in enumerate(recent_exchanges, 1):
            if exchange.get('inputs_state'):
                inputs = exchange['inputs_state']
                parameter_context += f"\n**Previous Parameters (Exchange {i}):**\n"
                parameter_context += f"- Grid: {inputs.get('grid', 'N/A')}\n"
                parameter_context += f"- Bus ID: {inputs.get('bus_id', 'N/A')}\n"
                parameter_context += f"- Power Factor: {inputs.get('power_factor', 'N/A')}\n"
                parameter_context += f"- Step Size: {inputs.get('step_size', 'N/A')}\n"
                parameter_context += f"- Max Scale: {inputs.get('max_scale', 'N/A')}\n"
                parameter_context += f"- Voltage Limit: {inputs.get('voltage_limit', 'N/A')}\n"
                parameter_context += f"- Load Type: {'Capacitive' if inputs.get('capacitive', False) else 'Inductive'}\n"
                parameter_context += f"- Curve Type: {'Continuous' if inputs.get('continuation', True) else 'Stops at nose point'}\n"
    
    system_prompt = prompts["question_parameter_agent"]["system"] + parameter_context
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(messages)
    node_response = NodeResponse(
        node_type="question_parameter",
        success=True,
        data={
            "response": reply.content,
            "parameter_context_used": bool(parameter_context),
            "exchanges_included": len(recent_exchanges)
        },
        message=reply.content,
        timestamp=datetime.now()
    )
    return {"messages": [reply], "node_response": node_response}

