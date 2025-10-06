from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

from agent.vector import retriever as _make_retriever
from agent.prompts import get_prompts
from agent.pv_curve.pv_curve import generate_pv_curve
from agent.history.history import ChatHistoryManager

from agent.models.state_models import Inputs
from agent.utils.common_utils import format_inputs_display, create_initial_state
from agent.workflows.compound_workflow import create_compound_workflow
from agent.terminal_ui import divider, info, answer

load_dotenv()




def setup_dependencies(provider="ollama"):
    prompts = get_prompts()
    
    if provider == "openai":
        llm = ChatOpenAI(
            model="o3-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        llm._model_name = "o3-mini"
    else:
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL") or "pv-curve" or "llama3.1:8b",
            base_url="http://localhost:11434"
        )
        llm._model_name = llm.model
    
    retriever = _make_retriever()
    
    return llm, prompts, retriever

def create_graph(provider="ollama", use_history=True):
    llm, prompts, retriever = setup_dependencies(provider)
    return create_compound_workflow(llm, prompts, retriever, generate_pv_curve, use_history)


def run_agent():
    print("Welcome to the PV Curve Agent! Type 'quit' or 'q' to exit.")
    
    provider = input("Which model provider would you like to use? Please type 'openai' or 'ollama': ").strip().lower()
    if provider not in ["openai", "ollama"]:
        provider = "ollama"
    
    llm, prompts, retriever = setup_dependencies(provider)
    graph = create_graph(provider, use_history=True)  # Enable history-aware mode
    
    print(f"Using model: {llm._model_name}")
  
    # Initialize chat history manager
    history_manager = ChatHistoryManager("agent/history/chat_history.json")
    session_id = history_manager.start_new_session(f"PV_Curve_Session_{provider}")
    print(f"Chat history will be saved to: {history_manager.history_file}")
  
    state = create_initial_state()

    while True:
        divider()
        print(f"Current parameters:\n{format_inputs_display(state['inputs'])}")
        divider()

        user_input = input("\nMessage: ")
        if user_input.strip().lower() in ["quit", "q"]:
            info("Quitting...")
            # Save final conversation history and cached results before exiting
            if state.get("conversation_history"):
                history_manager.add_conversation_history(session_id, state["conversation_history"])
            if state.get("cached_results"):
                history_manager.add_cached_results(session_id, state["cached_results"])
            
            # Show statistics
            stats = history_manager.get_statistics()
            print(f"\nSession saved with {stats['total_messages']} messages across {stats['total_sessions']} sessions")

            break

        state["messages"] = state.get("messages", []) + [HumanMessage(content=user_input)]
        
        try:
            # Add user input tracking for history updates
            state["last_user_input"] = user_input
            
            new_state = graph.invoke(state, config={"recursion_limit": 50})
            
            if new_state.get("messages") and len(new_state["messages"]) > 0:
                last_message = new_state["messages"][-1]
                answer(last_message.content)
                
                # Track assistant response and inputs for history updates
                new_state["last_assistant_response"] = last_message.content
                new_state["last_inputs_used"] = new_state["inputs"].model_dump()
                
                # Add message to history manager
                history_manager.add_message(
                    session_id, 
                    user_input, 
                    last_message.content, 
                    new_state["inputs"].model_dump()
                )
                
                # Keep the old conversation history system for backward compatibility
                conversation_history = state.get("conversation_history", [])
                conversation_history.append({
                    "user_input": user_input,
                    "assistant_response": last_message.content,
                    "inputs_used": new_state["inputs"].model_dump()
                })
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-10:]
                
                if new_state.get("results"):
                    cached_results = state.get("cached_results", [])
                    cached_results.append({
                        "inputs": new_state["inputs"].model_dump(),
                        "results": new_state["results"],
                        "timestamp": user_input
                    })
                    if len(cached_results) > 5:
                        cached_results = cached_results[-5:]
                    new_state["cached_results"] = cached_results
                
                new_state["conversation_history"] = conversation_history
            
            state = new_state
        except Exception as e:
            info(f"Error: {e}")
            state["error_info"] = None

if __name__ == "__main__":
    run_agent()