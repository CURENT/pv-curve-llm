from langchain_core.messages import AIMessage
from agent.state.app_state import State
from agent.schemas.response import NodeResponse
from agent.schemas.parameter import InputModifier
from agent.utils.display import display_executing_node, console
from datetime import datetime

def generation_agent(state: State, llm, prompts, retriever, generate_pv_curve):
    
    display_executing_node("generation")
    
    inputs = state["inputs"]
    last_message = state["messages"][-1]
    
    # Extract parameters from user's message if they're present
    # This allows "generate pv curve that power factor is 0.9" to work
    modifier_llm = llm.with_structured_output(InputModifier)
    result = modifier_llm.invoke([
        {"role": "system", "content": prompts["parameter_agent"]["system"].format(current_inputs=inputs)},
        {"role": "user", "content": last_message.content}
    ])
    
    # Update inputs if parameters were found in the message
    if result.modifications:
        updates = {}
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
        
        # Update inputs with extracted parameters
        inputs = inputs.model_copy(update=updates)
    
    # Generate PV curve with plot (skip_plot=False by default)
    results = generate_pv_curve(
        grid=inputs.grid,
        target_bus_idx=inputs.bus_id,
        step_size=inputs.step_size,
        max_scale=inputs.max_scale,
        power_factor=inputs.power_factor,
        voltage_limit=inputs.voltage_limit,
        capacitive=inputs.capacitive,
        skip_plot=False,  # Generate the visual graph
    )
    
    load_type = "capacitive" if inputs.capacitive else "inductive"
    
    generation_content = (
        f"PV curve generated for {inputs.grid.upper()} system (Bus {inputs.bus_id})\n"
        f"Load type: {load_type}, Power factor: {inputs.power_factor}\n"
        f"Plot saved to {results['save_path']}"
    )
    
    # No analysis here - just generation
    reply = AIMessage(content=generation_content)
    
    node_response = NodeResponse(
        node_type="generation",
        success=True,
        data={
            "pv_results": results,
            "grid_system": inputs.grid,
            "bus_monitored": inputs.bus_id,
            "load_margin_mw": results.get("load_margin_mw"),
            "nose_point_voltage_pu": results.get("nose_point", {}).get("voltage_pu"),
        },
        message=generation_content,
        timestamp=datetime.now(),
        metadata={
            "plot_path": results["save_path"],
            "convergence_steps": results["converged_steps"]
        }
    )
    # Return updated inputs if they were modified
    return_value = {"messages": [reply], "results": results, "node_response": node_response}
    if result.modifications:
        return_value["inputs"] = inputs
    return return_value

