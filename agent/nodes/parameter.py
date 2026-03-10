from langchain_core.messages import AIMessage
from agent.state.app_state import State
from agent.schemas.parameter import InputModifier
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node
import pandapower.networks as pn
from agent.utils.common_utils import apply_contingency_lines_update

_NET_MAP = {
    "ieee14": pn.case14,
    "ieee24": pn.case24_ieee_rts,
    "ieee30": pn.case30,
    "ieee39": pn.case39,
    "ieee57": pn.case57,
    "ieee118": pn.case118,
    "ieee300": pn.case300,
}


def _validate_contingency_pairs_for_grid(grid, pairs):
    """Raise ValueError if any (from_bus, to_bus) pair does not exist as a line/trafo in the grid."""
    if grid not in _NET_MAP:
        return

    net = _NET_MAP[grid]()
    for fb, tb in pairs:
        fb0, tb0 = fb - 1, tb - 1
        line_mask = (
            ((net.line["from_bus"] == fb0) & (net.line["to_bus"] == tb0)) |
            ((net.line["from_bus"] == tb0) & (net.line["to_bus"] == fb0))
        )
        trafo_mask = (
            ((net.trafo["hv_bus"] == fb0) & (net.trafo["lv_bus"] == tb0)) |
            ((net.trafo["hv_bus"] == tb0) & (net.trafo["lv_bus"] == fb0))
        ) if not net.trafo.empty else None

        if not line_mask.any() and (trafo_mask is None or not trafo_mask.any()):
            raise ValueError(
                f"No line or transformer found between bus {fb} and bus {tb} in grid '{grid}'."
            )


def _validate_gen_voltage_setpoints(grid, setpoints_dict, voltage_limit_min, voltage_max_pu=1.2):
    """Raise ValueError if a gen index is not a generator or vm_pu is outside [voltage_limit_min, voltage_max_pu]."""
    if grid not in _NET_MAP:
        return
    net = _NET_MAP[grid]()
    valid_gen_1based = list(net.gen.index + 1)
    for gen_idx, vm_pu in setpoints_dict.items():
        if gen_idx not in valid_gen_1based:
            raise ValueError(
                f"Generator index {gen_idx} not found in grid '{grid}'. Valid indices: {valid_gen_1based}."
            )
        if not (voltage_limit_min <= vm_pu <= voltage_max_pu):
            raise ValueError(
                f"Generator {gen_idx} voltage {vm_pu} pu must be between {voltage_limit_min} and {voltage_max_pu} pu."
            )


def _parse_gen_voltage_setpoints_string(s):
    """Parse '1:1.05,2:1.02' -> {1: 1.05, 2: 1.02}. Return None for empty/none/clear.

    Also accepts a dict[int, float] and normalizes it.
    """
    if isinstance(s, dict):
        out = {}
        for k, v in s.items():
            try:
                out[int(k)] = float(v)
            except (TypeError, ValueError):
                continue
        return out if out else None

    val = str(s).strip().lower()
    if val in ("", "none", "clear"):
        return None
    out = {}
    for part in val.split(","):
        part = part.strip()
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        try:
            out[int(k.strip())] = float(v.strip())
        except ValueError:
            continue
    return out if out else None


def parameter_agent(state: State, llm, prompts):
    
    display_executing_node("parameter")
    
    last_message = state["messages"][-1]
    modifier_llm = llm.with_structured_output(InputModifier)
    current_inputs = state["inputs"]
    
    result = modifier_llm.invoke([
        {"role": "system", "content": prompts["parameter_agent"]["system"].format(current_inputs=current_inputs)},
        {"role": "user", "content": last_message.content}
    ])
    
    updates = {}
    reply_parts = []

    if not result.modifications:
        reply_content = "No parameter changes detected"
        reply = AIMessage(content=reply_content)
        node_response = NodeResponse(
            node_type="parameter",
            success=True,
            data={"updated_parameters": [], "current_inputs": current_inputs.model_dump()},
            message=reply_content,
            timestamp=datetime.now()
        )
        return {"messages": [reply], "node_response": node_response}

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
        elif modification.parameter == "contingency_lines":
            val = str(modification.value).strip().lower()
            if val in ("", "none", "clear"):
                converted_value = None
            else:
                try:
                    pairs = [tuple(int(b) for b in pair.split("-")) for pair in val.split(";")]
                    if not all(len(p) == 2 for p in pairs):
                        continue

                    # Validate that each pair corresponds to an existing line/trafo in the selected grid
                    grid = state["inputs"].grid
                    _validate_contingency_pairs_for_grid(grid, pairs)

                    converted_value = pairs
                except (ValueError, AttributeError):
                    raise
        elif modification.parameter == "gen_voltage_setpoints":
            converted_value = _parse_gen_voltage_setpoints_string(modification.value)
            if converted_value is None and str(modification.value).strip().lower() not in ("", "none", "clear"):
                continue
            if converted_value is not None:
                _validate_gen_voltage_setpoints(
                    current_inputs.grid,
                    converted_value,
                    voltage_limit_min=current_inputs.voltage_limit,
                )

        if modification.parameter == "contingency_lines":
            converted_value = apply_contingency_lines_update(
                getattr(current_inputs, "contingency_lines", None), converted_value
            )
        updates[modification.parameter] = converted_value
        reply_parts.append(f"{modification.parameter} to {converted_value}")
    
    new_inputs = current_inputs.model_copy(update=updates)
    
    if len(reply_parts) == 1:
        reply_content = f"Updated {reply_parts[0]}"
    else:
        reply_content = f"Updated {len(reply_parts)} parameters:\n" + "\n".join(f"• {part}" for part in reply_parts)

    reply = AIMessage(content=reply_content)
    node_response = NodeResponse(
        node_type="parameter",
        success=True,
        data={
            "updated_parameters": list(updates.keys()),
            "current_inputs": new_inputs.model_dump(),
            "changes": updates
        },
        message=reply_content,
        timestamp=datetime.now()
    )
    return {"messages": [reply], "inputs": new_inputs, "node_response": node_response}

