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


def create_compound_workflow(llm, prompts, retriever, generate_pv_curve, use_history=True):
    graph_builder = StateGraph(State)
    
    # Add all nodes with dependencies injected
    graph_builder.add_node("compound_classifier", lambda state: classify_compound_message(state, llm, prompts))
    graph_builder.add_node("classifier", lambda state: classify_message(state, llm, prompts))
    graph_builder.add_node("enhanced_router", enhanced_router)
    graph_builder.add_node("planner", lambda state: planner_agent(state, llm, prompts))
    graph_builder.add_node("step_controller", step_controller)
    graph_builder.add_node("advance_step", advance_step)
    graph_builder.add_node("compound_summary", compound_summary_agent)
    graph_builder.add_node("question", lambda state: question_classifier(state, llm, prompts))
    graph_builder.add_node("question_general", lambda state: question_general_agent(state, llm, prompts, retriever))
    graph_builder.add_node("question_parameter", lambda state: question_parameter_agent(state, llm, prompts))
    graph_builder.add_node("parameter", lambda state: parameter_agent(state, llm, prompts))
    graph_builder.add_node("generation", lambda state: generation_agent(state, generate_pv_curve))
    graph_builder.add_node("analysis", lambda state: analysis_agent(state, llm, prompts, retriever))
    graph_builder.add_node("error_handler", lambda state: error_handler_agent(state, llm, prompts))
    
    # History-sensitive nodes (only added if use_history=True)
    if use_history:
        graph_builder.add_node("history_question_general", lambda state: history_sensitive_agent(state, llm, prompts, retriever))
        graph_builder.add_node("history_question_parameter", lambda state: history_aware_parameter_agent(state, llm, prompts))
        graph_builder.add_node("history_parameter", lambda state: history_aware_parameter_agent(state, llm, prompts))
        graph_builder.add_node("history_generation", lambda state: history_aware_generation_agent(state, generate_pv_curve))
        graph_builder.add_node("history_analysis", lambda state: history_aware_analysis_agent(state, llm, prompts, retriever))
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
    
    # Smart routing for enhanced_router based on history setting
    def enhanced_router_decision(state):
        if use_history:
            next_node = state.get("next")
            if next_node == "parameter":
                return smart_parameter_router(state)
            elif next_node == "generation":
                return smart_generation_router(state)
            else:
                return next_node
        else:
            return state.get("next")
    
    # Define routing options based on history setting
    enhanced_router_routes = {
        "question": "question",
        "parameter": "parameter",
        "generation": "generation",
        "planner": "planner"
    }
    
    if use_history:
        enhanced_router_routes.update({
            "history_parameter": "history_parameter",
            "history_generation": "history_generation"
        })
    
    graph_builder.add_conditional_edges(
        "enhanced_router",
        enhanced_router_decision,
        enhanced_router_routes
    )
    
    # Compound workflow path
    graph_builder.add_edge("planner", "step_controller")
    
    # Smart routing for step_controller based on history setting
    def step_controller_decision(state):
        if use_history:
            next_node = state.get("next")
            if next_node == "parameter":
                return smart_parameter_router(state)
            elif next_node == "generation":
                return smart_generation_router(state)
            else:
                return next_node
        else:
            return state.get("next")
    
    # Define routing options based on history setting
    step_controller_routes = {
        "question": "question",
        "parameter": "parameter",
        "generation": "generation",
        "advance_step": "advance_step",
        "error_handler": "error_handler",
        "compound_summary": "compound_summary"
    }
    
    if use_history:
        step_controller_routes.update({
            "history_parameter": "history_parameter",
            "history_generation": "history_generation"
        })
    
    graph_builder.add_conditional_edges(
        "step_controller",
        step_controller_decision,
        step_controller_routes
    )
    
    # Question handling - use smart routing if history is enabled
    if use_history:
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
    else:
        graph_builder.add_conditional_edges(
            "question",
            lambda state: state.get("message_type"),
            {
                "question_general": "question_general",
                "question_parameter": "question_parameter"
            }
        )
    
    # Question endings - handle both simple and compound
    def question_ending_router(state):
        if use_history:
            return "history_updater"
        else:
            return "advance_step" if state.get("is_compound") else "END"
    
    # Define question ending routes based on history setting
    question_ending_routes = {
        "advance_step": "advance_step",
        "END": END
    }
    
    if use_history:
        question_ending_routes["history_updater"] = "history_updater"
    
    graph_builder.add_conditional_edges(
        "question_general",
        question_ending_router,
        question_ending_routes
    )
    
    graph_builder.add_conditional_edges(
        "question_parameter",
        question_ending_router,
        question_ending_routes
    )
    
    # History-aware question endings
    if use_history:
        graph_builder.add_conditional_edges(
            "history_question_general",
            question_ending_router,
            question_ending_routes
        )
        
        graph_builder.add_conditional_edges(
            "history_question_parameter",
            question_ending_router,
            question_ending_routes
        )
    
    # Generation workflow - use smart routing if history is enabled
    def generation_router(state):
        if state.get("error_info"):
            return "error_handler"
        elif use_history:
            return smart_analysis_router(state)
        else:
            return "analysis"
    
    # Define generation routes based on history setting
    generation_routes = {
        "error_handler": "error_handler",
        "analysis": "analysis"
    }
    
    if use_history:
        generation_routes["history_analysis"] = "history_analysis"
    
    graph_builder.add_conditional_edges(
        "generation",
        generation_router,
        generation_routes
    )
    
    def analysis_ending_router(state):
        if use_history:
            return "history_updater"
        else:
            return "advance_step" if state.get("is_compound") else "END"
    
    # Define analysis ending routes based on history setting
    analysis_ending_routes = {
        "advance_step": "advance_step",
        "END": END
    }
    
    if use_history:
        analysis_ending_routes["history_updater"] = "history_updater"
    
    graph_builder.add_conditional_edges(
        "analysis",
        analysis_ending_router,
        analysis_ending_routes
    )
    
    # History-aware analysis ending
    if use_history:
        graph_builder.add_conditional_edges(
            "history_analysis",
            analysis_ending_router,
            analysis_ending_routes
        )
    
    # Parameter handling - use smart routing if history is enabled
    def parameter_ending_router(state):
        if state.get("error_info"):
            return "error_handler"
        elif use_history:
            return "history_updater"
        else:
            return "advance_step" if state.get("is_compound") else "END"
    
    # Define parameter ending routes based on history setting
    parameter_ending_routes = {
        "error_handler": "error_handler",
        "advance_step": "advance_step",
        "END": END
    }
    
    if use_history:
        parameter_ending_routes["history_updater"] = "history_updater"
    
    graph_builder.add_conditional_edges(
        "parameter",
        parameter_ending_router,
        parameter_ending_routes
    )
    
    # History-aware parameter ending
    if use_history:
        graph_builder.add_conditional_edges(
            "history_parameter",
            parameter_ending_router,
            parameter_ending_routes
        )
    
    # Error handling with retry
    def route_after_error(state):
        if state.get("retry_node"):
            return state["retry_node"]
        elif use_history:
            return "history_updater"
        else:
            return "advance_step" if state.get("is_compound") else "END"
    
    # Define error handler routes based on history setting
    error_handler_routes = {
        "parameter": "parameter",
        "generation": "generation", 
        "advance_step": "advance_step",
        "END": END
    }
    
    if use_history:
        error_handler_routes["history_updater"] = "history_updater"
    
    graph_builder.add_conditional_edges(
        "error_handler",
        route_after_error,
        error_handler_routes
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
    if use_history:
        graph_builder.add_edge("compound_summary", "history_updater")
        graph_builder.add_edge("history_updater", END)
    else:
        graph_builder.add_edge("compound_summary", END)
    
    return graph_builder.compile() 