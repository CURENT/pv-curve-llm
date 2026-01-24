from langgraph.graph import StateGraph, START, END
from agent.state.app_state import State
from agent.nodes.classify import classify_message
from agent.nodes.route import router
from agent.nodes.question_general import question_general_agent
from agent.nodes.question_parameter import question_parameter_agent
from agent.nodes.parameter import parameter_agent
from agent.nodes.generation import generation_agent
from agent.nodes.analysis import analysis_agent
from agent.nodes.planner import planner_agent
from agent.nodes.step_controller import step_controller
from agent.nodes.advance_step import advance_step
from agent.nodes.summary import summary_agent
from agent.nodes.error_handler import error_handler_agent

def create_workflow(llm, prompts, retriever, generate_pv_curve):
    graph_builder = StateGraph(State)
    
    graph_builder.add_node("classifier", lambda state: classify_message(state, llm, prompts))
    graph_builder.add_node("router", router)
    graph_builder.add_node("planner", lambda state: planner_agent(state, llm, prompts))
    graph_builder.add_node("step_controller", step_controller)
    graph_builder.add_node("advance_step", advance_step)
    graph_builder.add_node("summary", summary_agent)
    graph_builder.add_node("question_general", lambda state: question_general_agent(state, llm, prompts, retriever))
    graph_builder.add_node("question_parameter", lambda state: question_parameter_agent(state, llm, prompts))
    graph_builder.add_node("parameter", lambda state: parameter_agent(state, llm, prompts))
    graph_builder.add_node("generation", lambda state: generation_agent(state, llm, prompts, retriever, generate_pv_curve))
    graph_builder.add_node("analysis", lambda state: analysis_agent(state, llm, prompts, retriever, generate_pv_curve))
    graph_builder.add_node("error_handler", lambda state: error_handler_agent(state, llm, prompts))
    
    graph_builder.add_edge(START, "classifier")
    graph_builder.add_edge("classifier", "router")
    
    graph_builder.add_conditional_edges(
        "router",
        lambda state: state.get("next"),
        {
            "question_general": "question_general",
            "question_parameter": "question_parameter",
            "parameter": "parameter",
            "generation": "generation",
            "analysis": "analysis",
            "planner": "planner"
        }
    )
    
    graph_builder.add_edge("planner", "step_controller")
    
    graph_builder.add_conditional_edges(
        "step_controller",
        lambda state: state.get("next"),
        {
            "question_general": "question_general",
            "question_parameter": "question_parameter",
            "parameter": "parameter",
            "generation": "generation",
            "analysis": "analysis",
            "advance_step": "advance_step",
            "error_handler": "error_handler",
            "summary": "summary"
        }
    )
    
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
    
    graph_builder.add_conditional_edges(
        "generation",
        lambda state: "error_handler" if state.get("error_info") else ("advance_step" if state.get("is_compound") else "END"),
        {
            "error_handler": "error_handler",
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    graph_builder.add_conditional_edges(
        "analysis",
        lambda state: "error_handler" if state.get("error_info") else ("advance_step" if state.get("is_compound") else "END"),
        {
            "error_handler": "error_handler",
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    graph_builder.add_conditional_edges(
        "parameter",
        lambda state: "error_handler" if state.get("error_info") else ("advance_step" if state.get("is_compound") else "END"),
        {
            "error_handler": "error_handler",
            "advance_step": "advance_step",
            "END": END
        }
    )
    
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
            "analysis": "analysis",
            "advance_step": "advance_step",
            "END": END
        }
    )
    
    graph_builder.add_conditional_edges(
        "advance_step",
        lambda state: state.get("next"),
        {
            "step_controller": "step_controller",
            "summary": "summary"
        }
    )
    
    graph_builder.add_edge("summary", END)
    
    return graph_builder.compile()

