from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from agent.utils.context import get_conversation_context
from datetime import datetime
from agent.utils.display import display_executing_node

def question_general_agent(state: State, llm, prompts, retriever):
    
    display_executing_node("question_general")
    
    last_message = state["messages"][-1]
    context = retriever.invoke(last_message.content)
    
    recent_exchanges = get_conversation_context(state, max_exchanges=5)
    conversation_context = ""
    
    if recent_exchanges:
        conversation_context = "\n\n**Previous Conversation Context:**\n"
        
        for i, exchange in enumerate(recent_exchanges, 1):
            conversation_context += f"\n**Exchange {i}:**\n"
            conversation_context += f"User: {exchange.get('user_input', 'N/A')}\n"
            conversation_context += f"Assistant: {exchange.get('assistant_response', 'N/A')[:200]}...\n"
            
            if exchange.get('inputs_state'):
                inputs = exchange['inputs_state']
                conversation_context += f"Parameters: Grid: {inputs.get('grid', 'N/A')}, Bus: {inputs.get('bus_id', 'N/A')}, PF: {inputs.get('power_factor', 'N/A')}\n"
            
            if exchange.get('results'):
                results = exchange['results']
                conversation_context += f"Results: {results.get('grid_system', 'N/A')} system analysis completed\n"
                conversation_context += f"  - Load Margin: {results.get('load_margin_mw', 'N/A')} MW\n"
                conversation_context += f"  - Nose Point Voltage: {results.get('nose_point_voltage_pu', 'N/A')} pu\n"
                conversation_context += f"  - Converged Steps: {results.get('convergence_steps', 'N/A')}\n"
                if results.get('nose_point'):
                    nose = results.get('nose_point', {})
                    conversation_context += f"  - Nose Point Load: {nose.get('load_mw', 'N/A')} MW\n"
                    conversation_context += f"  - Nose Point Voltage: {nose.get('voltage_pu', 'N/A')} pu\n"

    system_prompt = prompts["question_general_agent"]["system"].format(context=context) + conversation_context
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompts["question_general_agent"]["user"].format(user_input=last_message.content)}
    ]
    reply = llm.invoke(messages)
    node_response = NodeResponse(
        node_type="question_general",
        success=True,
        data={
            "response": reply.content,
            "context_retrieved": len(context),
            "conversation_context_used": bool(conversation_context),
            "exchanges_included": len(recent_exchanges)
        },
        message=reply.content,
        timestamp=datetime.now()
    )
    return {"messages": [reply], "node_response": node_response}

