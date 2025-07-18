from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from typing_extensions import TypedDict, Annotated, Literal
from typing import Union, List
from vector import retriever as _make_retriever
from prompts import get_prompts
from pv_curve.pv_curve import generate_pv_curve
from dotenv import load_dotenv
import os

load_dotenv()

prompts = get_prompts()

# See Modelfile for instructions on how to use a custom model
# TODO: Experiment with deepseek-r1
llm = ChatOllama(
    model="deepseek-r1:7b" or os.getenv("OLLAMA_MODEL") or "llama3.1:8b",
    base_url="http://localhost:11434"
)

retriever = _make_retriever()

# Define allowed grid systems
GridSystem = Literal["ieee14", "ieee24", "ieee30", "ieee39", "ieee57", "ieee118", "ieee300"]

class Inputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grid: GridSystem = "ieee39"
    bus_id: int = Field(default=5, ge=0, le=300)  # Bus to monitor voltage (0-300 range)
    step_size: float = Field(default=0.01, gt=0, le=0.1)  # Load increment per iteration
    max_scale: float = Field(default=3.0, gt=1.0, le=10.0)  # Max load multiplier
    power_factor: float = Field(default=0.95, gt=0, le=1.0)  # Constant power factor
    voltage_limit: float = Field(default=0.4, gt=0, le=1.0)  # Voltage threshold to stop
    capacitive: bool = Field(default=False)  # Whether load is capacitive or inductive
    continuation: bool = Field(default=True)  # Whether to show mirrored curve

class MessageClassifier(BaseModel):
    message_type: Literal["question", "parameter", "generation"] = Field(
        ...,
        description="Classify if the message requires a parameter modification, a PV-curve generation/run, or a question/request that requires a knowledge response."
    )

class QuestionClassifier(BaseModel):
    question_type: Literal["question_general", "question_parameter"] = Field(
        ...,
        description="Classify if the question is a general voltage stability/PV curve question or specifically about parameter meanings/functionality."
    )

InputParameter = Literal["grid", "bus_id", "step_size", "max_scale", "power_factor", "voltage_limit", "capacitive", "continuation"]

class ParameterModification(BaseModel):
    parameter: InputParameter = Field(..., description="The parameter to modify")
    value: Union[str, float, int, bool] = Field(..., description="The new value for the parameter")

class InputModifier(BaseModel):
    modifications: List[ParameterModification] = Field(..., description="List of parameter modifications to apply")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None
    inputs: Inputs
    results: dict | None
    error_info: dict | None

def classify_message(state: State):
    last_message = state["messages"][-1]
    
    classifier_llm = llm.with_structured_output(MessageClassifier)

    print("Classifying input...")
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": prompts["classifier"]["system"]
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    print("Classification complete")

    return {"message_type": result.message_type}

def router(state: State):
    message_type = state.get("message_type", "question")

    if message_type == "parameter":
        return {"next": "parameter"}
    if message_type == "generation":
        return {"next": "generation"}
    
    return {"next": "question"}

def question_agent(state: State):
    last_message = state["messages"][-1]
    
    classifier_llm = llm.with_structured_output(QuestionClassifier)

    print("Classifying question...")
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": prompts["question_classifier"]["system"]
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    print("Question classification complete")

    return {"message_type": result.question_type}

def question_general_agent(state: State):
    last_message = state["messages"][-1]

    print("Retrieving context...")
    context = retriever.invoke(last_message.content)
    print("Context retrieved")

    messages = [
        {"role": "system",
                 "content": prompts["question_general_agent"]["system"].format(context=context)},
        {"role": "user", 
        "content": prompts["question_general_agent"]["user"].format(user_input=last_message.content)}
    ]

    print("Generating response...")
    reply = llm.invoke(messages)
    print("Response generated")
    return {"messages": [reply]}

def question_parameter_agent(state: State):
    last_message = state["messages"][-1]

    print("Answering parameter question...")
    messages = [
        {"role": "system", "content": prompts["question_parameter_agent"]["system"]},
        {"role": "user", "content": last_message.content}
    ]

    reply = llm.invoke(messages)
    print("Parameter question answered")
    return {"messages": [reply]}

def parameter_agent(state: State):
    last_message = state["messages"][-1]
    modifier_llm = llm.with_structured_output(InputModifier)
    
    current_inputs: Inputs = state["inputs"]
    
    print("Modifying inputs...")
    try:
        result = modifier_llm.invoke([
            {
                "role": "system",
                "content": prompts["parameter_agent"]["system"].format(current_inputs=current_inputs)
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ])
        print("Inputs modified")
    except Exception as e:
        error_info = {
            "error_type": "parameter_parsing",
            "error_message": str(e),
            "user_input": last_message.content,
            "current_inputs": current_inputs.model_dump(),
            "context": "Failed to parse parameter modification request"
        }
        return {"error_info": error_info}
    
    try:
        updates = {}
        reply_parts = []
        
        for modification in result.modifications:
            converted_value = modification.value
            if modification.parameter in ["bus_id"]:
                converted_value = int(modification.value)
            elif modification.parameter in ["step_size", "max_scale", "power_factor", "voltage_limit"]:
                converted_value = float(modification.value)
            elif modification.parameter in ["capacitive", "continuation"]:
                if isinstance(modification.value, str):
                    converted_value = modification.value.lower() in ["true", "yes", "1", "on"]
                else:
                    converted_value = bool(modification.value)
            
            updates[modification.parameter] = converted_value
            
            param_msg = f"{modification.parameter} to {converted_value}"
            if modification.parameter == "grid":
                param_msg += f" (Grid system changed)"
            elif modification.parameter == "bus_id":
                param_msg += f" (Monitoring bus)"
            reply_parts.append(param_msg)
        
        new_inputs = current_inputs.model_copy(update=updates)
        

        if len(reply_parts) == 1:
            reply_content = f"Updated {reply_parts[0]}"
        else:
            reply_content = f"Updated {len(reply_parts)} parameters:\n" + "\n".join(f"• {part}" for part in reply_parts)
        
        reply = AIMessage(content=reply_content)
        return {"messages": [reply], "inputs": new_inputs}
        
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            msg = error.get('msg', 'Invalid value')
            error_details.append(f"{field}: {msg}")
        
        error_info = {
            "error_type": "validation_error",
            "error_message": '; '.join(error_details),
            "user_input": last_message.content,
            "current_inputs": current_inputs.model_dump(),
            "context": "Parameter validation failed",
            "validation_errors": e.errors()
        }
        return {"error_info": error_info}
    except ValueError as e:
        error_info = {
            "error_type": "type_conversion",
            "error_message": str(e),
            "user_input": last_message.content,
            "current_inputs": current_inputs.model_dump(),
            "context": "Failed to convert parameter value to correct type"
        }
        return {"error_info": error_info}

def generation_agent(state: State):
    print("Generating PV curve...")

    inputs = state["inputs"]

    try:
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

        print("PV curve generated")
        
        load_type = "capacitive" if inputs.capacitive else "inductive"
        curve_type = "with continuation curve" if inputs.continuation else "upper branch only"
        
        reply_content = (
            f"PV curve generated for {inputs.grid.upper()} system (Bus {inputs.bus_id})\n"
            f"Load type: {load_type}, Power factor: {inputs.power_factor}\n"
            f"Plot saved to {results['save_path']} ({curve_type})"
        )
        
        reply = AIMessage(content=reply_content)
        return {"messages": [reply], "results": results}
    
    except Exception as e:
        error_info = {
            "error_type": "simulation_error",
            "error_message": str(e),
            "current_inputs": inputs.model_dump(),
            "context": "PV curve simulation failed"
        }
        return {"error_info": error_info}

def analysis_agent(state: State):
    print("Analyzing PV curve results...")
    
    results = state.get("results")
    if not results:
        reply = AIMessage(content="No PV curve results available for analysis.")
        return {"messages": [reply]}
    
    inputs = state["inputs"]
    analysis_query = (
        f"PV curve voltage stability analysis nose point load margin "
        f"voltage drop {inputs.grid} power system stability assessment "
        f"power factor {inputs.power_factor} voltage collapse"
    )
    
    print("Retrieving analysis context...")
    context = retriever.invoke(analysis_query)
    print("Analysis context retrieved")
    
    messages = [
        {
            "role": "system",
            "content": prompts["analysis_agent"]["system"].format(context=context)
        },
        {
            "role": "user",
            "content": prompts["analysis_agent"]["user"].format(
                results=results,
                grid_system=results['grid_system'].upper()
            )
        }
    ]
    
    print("Generating analysis...")
    reply = llm.invoke(messages)
    print("Analysis complete")
    return {"messages": [reply]}

def error_handler_agent(state: State):
    print("Analyzing error...")
    
    error_info = state.get("error_info", {})
    
    # Format error context for the LLM
    error_context = f"""
Error Type: {error_info.get('error_type', 'unknown')}
Error Message: {error_info.get('error_message', 'No message available')}
Context: {error_info.get('context', 'No context available')}

Current Inputs: {error_info.get('current_inputs', 'Not available')}

User Input: {error_info.get('user_input', 'Not available')}

Additional Info: {error_info.get('validation_errors', 'None')}
"""
    
    messages = [
        {"role": "system", "content": prompts["error_handler"]["system"]},
        {"role": "user", "content": f"Please analyze this error and provide a helpful explanation:\n\n{error_context}"}
    ]
    
    reply = llm.invoke(messages)
    print("Error analysis complete")
    return {"messages": [reply]}

graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("question", question_agent)
graph_builder.add_node("question_general", question_general_agent)
graph_builder.add_node("question_parameter", question_parameter_agent)
graph_builder.add_node("parameter", parameter_agent)
graph_builder.add_node("generation", generation_agent)
graph_builder.add_node("analysis", analysis_agent)
graph_builder.add_node("error_handler", error_handler_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {
        "question": "question",
        "parameter": "parameter",
        "generation": "generation"
    }
)

graph_builder.add_conditional_edges(
    "question",
    lambda state: state.get("message_type"),
    {
        "question_general": "question_general",
        "question_parameter": "question_parameter"
    }
)

graph_builder.add_edge("question_general", END)
graph_builder.add_edge("question_parameter", END)
graph_builder.add_edge("generation", "analysis")
graph_builder.add_edge("analysis", END)
graph_builder.add_edge("error_handler", END)

graph_builder.add_conditional_edges(
    "parameter",
    lambda state: "error_handler" if state.get("error_info") else "END",
    {
        "error_handler": "error_handler",
        "END": END
    }
)

graph_builder.add_conditional_edges(
    "generation",
    lambda state: "error_handler" if state.get("error_info") else "analysis",
    {
        "error_handler": "error_handler",
        "analysis": "analysis"
    }
)

graph = graph_builder.compile()

def format_inputs_display(inputs: Inputs) -> str:
    param_labels = {
        "grid": "Grid system",
        "bus_id": "Bus to monitor voltage",
        "step_size": "Load increment step size",
        "max_scale": "Maximum load multiplier",
        "power_factor": "Power factor",
        "voltage_limit": "Voltage threshold to stop",
        "capacitive": "Load type",
        "continuation": "Curve type"
    }
    
    formatted_lines = []
    for param, value in inputs.model_dump().items():
        label = param_labels.get(param, param)
        
        if param == "capacitive":
            display_value = "Capacitive" if value else "Inductive"
        elif param == "continuation":
            display_value = "Continuous" if value else "Stops at nose point"
        elif param == "grid":
            display_value = value.upper()
        else:
            display_value = str(value)
            
        formatted_lines.append(f"{label}: {display_value}")
    
    return "\n".join(formatted_lines)

def run_agent():
    print("Welcome to the PV Curve Agent! Type 'quit' or 'q' to exit.")
    print(f"Using model: {llm.model}")

    state = {"messages": [], "message_type": None, "inputs": Inputs(), "results": None, "error_info": None}

    while True:
        print(f"\nCurrent inputs:\n{format_inputs_display(state['inputs'])}")
        
        user_input = input("\nMessage: ")
        if user_input.strip().lower() in ["quit", "q"]:
            print("Quitting...")
            break

        state["messages"] = state.get("messages", []) + [
            HumanMessage(content=user_input)
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")

if __name__ == "__main__":
    run_agent()