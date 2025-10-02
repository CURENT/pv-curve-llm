"""
History Sensitive Node for LangGraph-based PV Curve Agent

This module provides history-aware functionality that maintains conversation context
and simulation results across interactions, making the agent more intelligent and
contextually aware.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from agent.models.state_models import State
from agent.terminal_ui import info, spinner
from langchain_core.messages import AIMessage


class HistoryContext:
    """Manages historical context for the agent."""
    
    def __init__(self, max_conversation_history: int = 10, max_simulation_results: int = 5):
        self.max_conversation_history = max_conversation_history
        self.max_simulation_results = max_simulation_results
    
    def extract_conversation_context(self, state: State) -> str:
        """Extract relevant conversation context from state."""
        conversation_history = state.get("conversation_history", [])
        if not conversation_history:
            return ""
        
        # Get recent conversations (last 3-5 interactions)
        recent_conversations = conversation_history[-3:]
        
        context_parts = ["Recent conversation context:"]
        for i, conv in enumerate(recent_conversations, 1):
            user_input = conv.get("user_input", "")
            assistant_response = conv.get("assistant_response", "")
            
            # Truncate very long responses for context
            if len(assistant_response) > 300:
                assistant_response = assistant_response[:300] + "..."
            
            context_parts.append(f"Interaction {i}:")
            context_parts.append(f"  User: {user_input}")
            context_parts.append(f"  Assistant: {assistant_response}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def extract_simulation_context(self, state: State) -> str:
        """Extract relevant simulation results context from state."""
        cached_results = state.get("cached_results", [])
        if not cached_results:
            return ""
        
        # Get recent simulation results
        recent_results = cached_results[-2:]
        
        context_parts = ["Previous simulation results for reference:"]
        for i, result in enumerate(recent_results, 1):
            inputs = result.get("inputs", {})
            results_data = result.get("results", {})
            
            context_parts.append(f"Simulation {i}:")
            context_parts.append(f"  Grid: {inputs.get('grid', 'Unknown')}")
            context_parts.append(f"  Bus: {inputs.get('bus_id', 'Unknown')}")
            context_parts.append(f"  Power Factor: {inputs.get('power_factor', 'Unknown')}")
            context_parts.append(f"  Load Type: {'Capacitive' if inputs.get('capacitive', False) else 'Inductive'}")
            context_parts.append(f"  Curve Type: {'Continuous' if inputs.get('continuation', True) else 'Upper branch only'}")
            
            # Include key results if available
            if results_data:
                if 'save_path' in results_data:
                    context_parts.append(f"  Plot saved to: {results_data['save_path']}")
                if 'max_power' in results_data:
                    context_parts.append(f"  Max power: {results_data['max_power']}")
                if 'voltage_at_max_power' in results_data:
                    context_parts.append(f"  Voltage at max power: {results_data['voltage_at_max_power']}")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def extract_parameter_evolution_context(self, state: State) -> str:
        """Extract context about how parameters have evolved over time."""
        conversation_history = state.get("conversation_history", [])
        if not conversation_history:
            return ""
        
        # Track parameter changes over time
        parameter_changes = []
        for conv in conversation_history:
            inputs_used = conv.get("inputs_used", {})
            if inputs_used:
                timestamp = conv.get("timestamp", "Unknown time")
                changes = []
                for param, value in inputs_used.items():
                    changes.append(f"{param}={value}")
                if changes:
                    parameter_changes.append(f"  {timestamp}: {', '.join(changes)}")
        
        if parameter_changes:
            context = "Parameter evolution over time:\n" + "\n".join(parameter_changes[-5:])  # Last 5 changes
            return context
        
        return ""


def history_sensitive_agent(state: State, llm, prompts, retriever):
    """
    Main history-sensitive agent that processes requests with full historical context.
    
    This agent:
    1. Analyzes the current request in context of previous interactions
    2. Considers previous simulation results and parameter changes
    3. Provides more intelligent and contextually aware responses
    4. Updates the state with new historical information
    """
    info("Processing request with historical context...")
    
    last_message = state["messages"][-1]
    history_context = HistoryContext()
    
    with spinner("Analyzing historical context...") as update:
        update("Retrieving relevant context...")
        
        # Get RAG context
        context = retriever.invoke(last_message.content)
        
        # Get conversation context
        conversation_context = history_context.extract_conversation_context(state)
        
        # Get simulation results context
        simulation_context = history_context.extract_simulation_context(state)
        
        # Get parameter evolution context
        parameter_context = history_context.extract_parameter_evolution_context(state)
        
        # Combine all contexts
        full_context = f"{context}\n\n{conversation_context}\n\n{simulation_context}\n\n{parameter_context}"
        
        update("Generating contextually aware response...")
        
        # Create enhanced system prompt with historical context
        system_prompt = f"""
{prompts["question_general_agent"]["system"]}

IMPORTANT: You have access to the complete conversation history and previous simulation results. Use this context to:
1. Reference previous interactions when relevant
2. Compare current request with previous simulations
3. Provide more intelligent responses based on the user's history
4. Suggest improvements or variations based on previous results
5. Maintain continuity in the conversation

Historical Context:
{full_context}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompts["question_general_agent"]["user"].format(user_input=last_message.content)}
        ]
        
        reply = llm.invoke(messages)
    
    return {"messages": [reply]}


def update_conversation_history(state: State, user_input: str, assistant_response: str, inputs_used: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the conversation history with the latest interaction.
    
    Args:
        state: Current agent state
        user_input: User's input message
        assistant_response: Assistant's response
        inputs_used: Parameters used in this interaction
    
    Returns:
        Updated state with new conversation history
    """
    conversation_history = state.get("conversation_history", [])
    
    # Add new conversation entry
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "assistant_response": assistant_response,
        "inputs_used": inputs_used
    }
    
    conversation_history.append(new_entry)
    
    # Keep only the most recent conversations
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]
    
    return {"conversation_history": conversation_history}


def update_simulation_results(state: State, results: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the cached simulation results with new results.
    
    Args:
        state: Current agent state
        results: New simulation results
        inputs: Parameters used for the simulation
    
    Returns:
        Updated state with new simulation results
    """
    cached_results = state.get("cached_results", [])
    
    # Add new result entry
    new_result = {
        "timestamp": datetime.now().isoformat(),
        "inputs": inputs,
        "results": results
    }
    
    cached_results.append(new_result)
    
    # Keep only the most recent results
    if len(cached_results) > 5:
        cached_results = cached_results[-5:]
    
    return {"cached_results": cached_results}


def history_aware_parameter_agent(state: State, llm, prompts):
    """
    Parameter agent that considers historical parameter usage and actually updates parameters.
    """
    info("Processing parameter request with historical context...")
    
    # Import the original parameter agent logic
    from agent.nodes.parameter_nodes import parameter_agent
    
    # First, run the original parameter agent to get the actual parameter updates
    parameter_result = parameter_agent(state, llm, prompts)
    
    # If parameters were successfully updated, add historical context to the response
    if "inputs" in parameter_result and not parameter_result.get("error_info"):
        last_message = state["messages"][-1]
        history_context = HistoryContext()
        
        # Get parameter evolution context
        parameter_context = history_context.extract_parameter_evolution_context(state)
        
        # Get recent simulation results for parameter suggestions
        simulation_context = history_context.extract_simulation_context(state)
        
        # Create enhanced response with historical context
        original_content = parameter_result["messages"][0].content
        
        # Add historical context to the response
        enhanced_content = f"""{original_content}

Historical Context:
{parameter_context}

Recent Simulation Results:
{simulation_context}

Based on your parameter history, consider these insights for your next simulation."""
        
        # Update the message content
        from langchain_core.messages import AIMessage
        enhanced_message = AIMessage(content=enhanced_content)
        parameter_result["messages"] = [enhanced_message]
    
    return parameter_result


def history_aware_generation_agent(state: State, generate_pv_curve):
    """
    Generation agent that considers previous simulation results and provides comparative analysis.
    """
    info("Generating PV curve with historical context...")
    
    from langchain_core.messages import AIMessage
    inputs = state["inputs"]
    
    try:
        # Generate the PV curve
        results = generate_pv_curve(
            grid=inputs.grid,
            target_bus_idx=inputs.bus_id,
            step_size=inputs.step_size,
            max_scale=inputs.max_scale,
            power_factor=inputs.power_factor,
            voltage_limit=inputs.voltage_limit,
            capacitive=inputs.capacitive,
            continuation=inputs.continuation,
        )
        
        # Get historical context for comparison
        history_context = HistoryContext()
        simulation_context = history_context.extract_simulation_context(state)
        
        load_type = "capacitive" if inputs.capacitive else "inductive"
        curve_type = "with continuation curve" if inputs.continuation else "upper branch only"
        
        # Enhanced response with historical comparison
        reply_content = f"""PV curve generated for {inputs.grid.upper()} system (Bus {inputs.bus_id})
Load type: {load_type}, Power factor: {inputs.power_factor}
Plot saved to {results['save_path']} ({curve_type})

Historical Context:
{simulation_context}

This simulation can be compared with previous results above for analysis of parameter effects."""
        
        # Show positive generation success message
        load_type_display = "Capacitive" if inputs.capacitive else "Inductive"
        curve_type_display = "Continuous" if inputs.continuation else "Stops at nose point"
        info(f"PV Curve Generated: {inputs.grid.upper()} Bus {inputs.bus_id} | Step: {inputs.step_size} | Max Scale: {inputs.max_scale} | PF: {inputs.power_factor} | V Limit: {inputs.voltage_limit} | Load: {load_type_display} | Type: {curve_type_display}")
        
        reply = AIMessage(content=reply_content)
        return {"messages": [reply], "results": results}
    
    except Exception as e:
        info(f"Generation failed: {str(e)}")
        return {"error_info": {
            "error_type": "simulation_error",
            "error_message": str(e),
            "current_inputs": inputs.model_dump(),
            "context": "PV curve simulation failed"
        }, "failed_node": "generation"}


def history_aware_analysis_agent(state: State, llm, prompts, retriever):
    """
    Analysis agent that provides comparative analysis with previous results.
    """
    info("Analyzing PV curve with historical context...")
    
    last_message = state["messages"][-1]
    history_context = HistoryContext()
    
    with spinner("Performing comparative analysis...") as update:
        # Get RAG context
        context = retriever.invoke(last_message.content)
        
        # Get simulation context for comparison
        simulation_context = history_context.extract_simulation_context(state)
        
        # Get conversation context
        conversation_context = history_context.extract_conversation_context(state)
        
        # Enhanced system prompt with historical analysis
        enhanced_system_prompt = f"""
{prompts["analysis_agent"]["system"]}

Historical Analysis Context:
{simulation_context}

Conversation Context:
{conversation_context}

Use this historical context to:
1. Compare current results with previous simulations
2. Identify trends and patterns in parameter effects
3. Provide insights based on the user's simulation history
4. Suggest next steps based on previous interactions
"""
        
        messages = [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "user", "content": last_message.content}
        ]
        
        reply = llm.invoke(messages)
    
    return {"messages": [reply]}


def history_state_updater(state: State, user_input: str, assistant_response: str, inputs_used: Dict[str, Any], results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Central function to update the agent state with new historical information.
    
    This should be called after each interaction to maintain the historical context.
    """
    updates = {}
    
    # Update conversation history
    conversation_updates = update_conversation_history(state, user_input, assistant_response, inputs_used)
    updates.update(conversation_updates)
    
    # Update simulation results if available
    if results:
        simulation_updates = update_simulation_results(state, results, inputs_used)
        updates.update(simulation_updates)
    
    return updates
