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

def create_compound_workflow(llm, prompts, retriever, generate_pv_curve):
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
    
    # History-sensitive nodes
    graph_builder.add_node("history_sensitive", lambda state: history_sensitive_agent(state, llm, prompts, retriever))
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
    
    graph_builder.add_conditional_edges(
        "enhanced_router",
        lambda state: state.get("next"),
        {
            "question": "question",
            "parameter": "parameter",
            "generation": "generation",
            "planner": "planner"
        }
    )
    
    # Compound workflow path
    graph_builder.add_edge("planner", "step_controller")
    
    graph_builder.add_conditional_edges(
        "step_controller",
        lambda state: state.get("next"),
        {
            "question": "question",
            "parameter": "parameter",
            "generation": "generation",
            "advance_step": "advance_step",
            "error_handler": "error_handler",
            "compound_summary": "compound_summary"
        }
    )
    
    # Question handling
    graph_builder.add_conditional_edges(
        "question",
        lambda state: state.get("message_type"),
        {
            "question_general": "question_general",
            "question_parameter": "question_parameter"
        }
    )
    
    # Question endings - handle both simple and compound
    graph_builder.add_conditional_edges(
        "question_general",
        lambda state: "advance_step" if state.get("is_compound") else "END",
        {
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    graph_builder.add_conditional_edges(
        "question_parameter",
        lambda state: "advance_step" if state.get("is_compound") else "END",
        {
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    # Generation workflow
    graph_builder.add_conditional_edges(
        "generation",
        lambda state: "error_handler" if state.get("error_info") else "analysis",
        {
            "error_handler": "error_handler",
            "analysis": "analysis"
        }
    )
    
    graph_builder.add_conditional_edges(
        "analysis",
        lambda state: "advance_step" if state.get("is_compound") else "END",
        {
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    # Parameter handling
    graph_builder.add_conditional_edges(
        "parameter",
        lambda state: "error_handler" if state.get("error_info") else ("advance_step" if state.get("is_compound") else "END"),
        {
            "error_handler": "error_handler",
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    # Error handling with retry
    def route_after_error(state):
        if state.get("retry_node"):
            return state["retry_node"]
        return "advance_step" if state.get("is_compound") else "END"
    
    graph_builder.add_conditional_edges(
        "error_handler",
        route_after_error,
        {
            "parameter": "parameter",
            "generation": "generation", 
            "advance_step": "advance_step",
            "END": END
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
    graph_builder.add_edge("compound_summary", END)
    
    return graph_builder.compile() 