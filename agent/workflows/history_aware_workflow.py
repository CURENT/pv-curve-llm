"""
History-Aware Workflow for LangGraph-based PV Curve Agent

This workflow integrates history-sensitive nodes that maintain conversation context
and simulation results across interactions, making the agent more intelligent and
contextually aware.
"""

from langgraph.graph import StateGraph, START, END
from agent.models.state_models import State
from agent.nodes.classifier_nodes import classify_compound_message, classify_message, question_classifier, enhanced_router
from agent.nodes.parameter_nodes import parameter_agent, planner_agent, step_controller, advance_step
from agent.nodes.execution_nodes import (
    question_general_agent, 
    question_parameter_agent, 
    generation_agent, 
    analysis_agent, 
    error_handler_agent,
    compound_summary_agent
)
from agent.nodes.history_sensitive_node import (
    history_sensitive_agent,
    history_aware_parameter_agent,
    history_aware_generation_agent,
    history_aware_analysis_agent,
    history_state_updater
)


def needs_history_context(state: State) -> bool:
    """
    Determine if the current request needs historical context.
    
    Returns True if the user is asking about:
    - Previous simulations or results
    - Comparisons with past data
    - Parameter history or trends
    - References to past conversations
    """
    if not state.get("messages"):
        return False
    
    last_message = state["messages"][-1].content.lower()
    
    # Keywords that indicate history is needed
    history_keywords = [
        "previous", "before", "last", "earlier", "compare", "comparison",
        "history", "trend", "pattern", "evolution", "change over time",
        "what did i", "what parameters", "show me my", "my previous",
        "earlier simulation", "last result", "past", "earlier result"
    ]
    
    return any(keyword in last_message for keyword in history_keywords)


def smart_question_router(state: State) -> str:
    """Route questions to history-aware or regular agents based on context needs."""
    if needs_history_context(state):
        return "history_question_general" if state.get("message_type") == "question_general" else "history_question_parameter"
    else:
        return "question_general" if state.get("message_type") == "question_general" else "question_parameter"


def smart_parameter_router(state: State) -> str:
    """Route parameter requests to history-aware or regular agents based on context needs."""
    return "history_parameter" if needs_history_context(state) else "parameter"


def smart_generation_router(state: State) -> str:
    """Route generation requests to history-aware or regular agents based on context needs."""
    return "history_generation" if needs_history_context(state) else "generation"


def smart_analysis_router(state: State) -> str:
    """Route analysis requests to history-aware or regular agents based on context needs."""
    return "history_analysis" if needs_history_context(state) else "analysis"


def create_history_aware_workflow(llm, prompts, retriever, generate_pv_curve):
    """
    Create a history-aware workflow that maintains context across interactions.
    
    This workflow uses history-sensitive nodes that:
    1. Consider previous conversations and simulation results
    2. Provide more intelligent and contextually aware responses
    3. Learn from user preferences and parameter usage patterns
    4. Maintain continuity across multiple interactions
    """
    graph_builder = StateGraph(State)
    
    # Add all nodes with dependencies injected
    graph_builder.add_node("compound_classifier", lambda state: classify_compound_message(state, llm, prompts))
    graph_builder.add_node("classifier", lambda state: classify_message(state, llm, prompts))
    graph_builder.add_node("enhanced_router", enhanced_router)
    graph_builder.add_node("planner", lambda state: planner_agent(state, llm, prompts))
    graph_builder.add_node("step_controller", step_controller)
    graph_builder.add_node("advance_step", advance_step)
    graph_builder.add_node("compound_summary", compound_summary_agent)
    
    # Question handling - use regular versions by default
    graph_builder.add_node("question", lambda state: question_classifier(state, llm, prompts))
    graph_builder.add_node("question_general", lambda state: question_general_agent(state, llm, prompts, retriever))
    graph_builder.add_node("question_parameter", lambda state: question_parameter_agent(state, llm, prompts))
    
    # Parameter and generation - use regular versions by default
    graph_builder.add_node("parameter", lambda state: parameter_agent(state, llm, prompts))
    graph_builder.add_node("generation", lambda state: generation_agent(state, generate_pv_curve))
    graph_builder.add_node("analysis", lambda state: analysis_agent(state, llm, prompts, retriever))
    
    # History-aware versions - only used when explicitly needed
    graph_builder.add_node("history_question_general", lambda state: history_sensitive_agent(state, llm, prompts, retriever))
    graph_builder.add_node("history_question_parameter", lambda state: history_aware_parameter_agent(state, llm, prompts))
    graph_builder.add_node("history_parameter", lambda state: history_aware_parameter_agent(state, llm, prompts))
    graph_builder.add_node("history_generation", lambda state: history_aware_generation_agent(state, generate_pv_curve))
    graph_builder.add_node("history_analysis", lambda state: history_aware_analysis_agent(state, llm, prompts, retriever))
    
    # Error handling
    graph_builder.add_node("error_handler", lambda state: error_handler_agent(state, llm, prompts))
    
    # History state updater - runs after each interaction
    graph_builder.add_node("history_updater", lambda state: history_state_updater(
        state, 
        state.get("last_user_input", ""), 
        state.get("last_assistant_response", ""), 
        state.get("last_inputs_used", {}), 
        state.get("results")
    ))
    
    # Start with compound classification
    graph_builder.add_edge(START, "compound_classifier")
    
    # Route based on compound vs simple
    graph_builder.add_conditional_edges(
        "compound_classifier",
        lambda state: "planner" if state.get("is_compound") else "classifier",
        {
            "planner": "planner",
            "classifier": "classifier"
        }
    )
    
    # Simple workflow path
    graph_builder.add_edge("classifier", "enhanced_router")
    
    graph_builder.add_conditional_edges(
        "enhanced_router",
        lambda state: state.get("next") if state.get("next") != "parameter" and state.get("next") != "generation" else smart_parameter_router(state) if state.get("next") == "parameter" else smart_generation_router(state),
        {
            "question": "question",
            "parameter": "parameter",
            "generation": "generation",
            "history_parameter": "history_parameter",
            "history_generation": "history_generation",
            "planner": "planner"
        }
    )
    
    # Compound workflow path
    graph_builder.add_edge("planner", "step_controller")
    
    graph_builder.add_conditional_edges(
        "step_controller",
        lambda state: state.get("next") if state.get("next") not in ["parameter", "generation"] else smart_parameter_router(state) if state.get("next") == "parameter" else smart_generation_router(state),
        {
            "question": "question",
            "parameter": "parameter",
            "generation": "generation",
            "history_parameter": "history_parameter",
            "history_generation": "history_generation",
            "advance_step": "advance_step",
            "error_handler": "error_handler",
            "compound_summary": "compound_summary"
        }
    )
    
    # Question handling - use smart routing
    graph_builder.add_conditional_edges(
        "question",
        smart_question_router,
        {
            "question_general": "question_general",
            "question_parameter": "question_parameter",
            "history_question_general": "history_question_general",
            "history_question_parameter": "history_question_parameter"
        }
    )
    
    # Question endings - handle both simple and compound
    graph_builder.add_conditional_edges(
        "question_general",
        lambda state: "history_updater" if state.get("is_compound") else "history_updater",
        {
            "history_updater": "history_updater"
        }
    )
    
    graph_builder.add_conditional_edges(
        "question_parameter",
        lambda state: "history_updater" if state.get("is_compound") else "history_updater",
        {
            "history_updater": "history_updater"
        }
    )
    
    graph_builder.add_conditional_edges(
        "history_question_general",
        lambda state: "history_updater" if state.get("is_compound") else "history_updater",
        {
            "history_updater": "history_updater"
        }
    )
    
    graph_builder.add_conditional_edges(
        "history_question_parameter",
        lambda state: "history_updater" if state.get("is_compound") else "history_updater",
        {
            "history_updater": "history_updater"
        }
    )
    
    # Generation workflow - use smart routing
    graph_builder.add_conditional_edges(
        "generation",
        lambda state: "error_handler" if state.get("error_info") else smart_analysis_router(state),
        {
            "error_handler": "error_handler",
            "analysis": "analysis",
            "history_analysis": "history_analysis"
        }
    )
    
    graph_builder.add_conditional_edges(
        "analysis",
        lambda state: "history_updater" if state.get("is_compound") else "history_updater",
        {
            "history_updater": "history_updater"
        }
    )
    
    graph_builder.add_conditional_edges(
        "history_analysis",
        lambda state: "history_updater" if state.get("is_compound") else "history_updater",
        {
            "history_updater": "history_updater"
        }
    )
    
    # Parameter handling - use smart routing
    graph_builder.add_conditional_edges(
        "parameter",
        lambda state: "error_handler" if state.get("error_info") else ("history_updater" if state.get("is_compound") else "history_updater"),
        {
            "error_handler": "error_handler",
            "history_updater": "history_updater"
        }
    )
    
    graph_builder.add_conditional_edges(
        "history_parameter",
        lambda state: "error_handler" if state.get("error_info") else ("history_updater" if state.get("is_compound") else "history_updater"),
        {
            "error_handler": "error_handler",
            "history_updater": "history_updater"
        }
    )
    
    # Error handling with retry
    def route_after_error(state):
        if state.get("retry_node"):
            return state["retry_node"]
        return "history_updater" if state.get("is_compound") else "history_updater"
    
    graph_builder.add_conditional_edges(
        "error_handler",
        route_after_error,
        {
            "parameter": "parameter",
            "generation": "generation", 
            "advance_step": "advance_step",
            "history_updater": "history_updater"
        }
    )
    
    # Step advancement
    graph_builder.add_conditional_edges(
        "advance_step",
        lambda state: state.get("next"),
        {
            "step_controller": "step_controller",
            "compound_summary": "compound_summary"
        }
    )
    
    # Compound workflow ending
    graph_builder.add_edge("compound_summary", "history_updater")
    
    # History updater always goes to END
    graph_builder.add_edge("history_updater", END)
    
    return graph_builder.compile()


def create_hybrid_workflow(llm, prompts, retriever, generate_pv_curve, use_history=True):
    """
    Create a hybrid workflow that can switch between history-aware and regular modes.
    
    Args:
        use_history: If True, use history-aware nodes; if False, use regular nodes
    """
    if use_history:
        return create_history_aware_workflow(llm, prompts, retriever, generate_pv_curve)
    else:
        # Import and use the regular compound workflow
        from agent.workflows.compound_workflow import create_compound_workflow
        return create_compound_workflow(llm, prompts, retriever, generate_pv_curve)
