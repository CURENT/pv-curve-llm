from langchain_core.messages import AIMessage
import andes
from agent.state.app_state import State
from agent.schemas.parameter import InputModifier
from agent.schemas.response import NodeResponse
from datetime import datetime
from agent.utils.display import display_executing_node
from agent.utils.common_utils import apply_contingency_lines_update

_CASE_MAP = {
    "ieee14": "ieee14/ieee14.json",
    "ieee39": "ieee39/ieee39.json",
    "ieee118": "matpower/case118.m",
    "ieee300": "matpower/case300.m",
}


def _validate_contingency_pairs_for_grid(grid, pairs):
    """Raise ValueError if any (from_bus, to_bus) pair does not exist as a line in the grid."""
    if grid not in _CASE_MAP:
        return

    ss = andes.load(andes.get_case(_CASE_MAP[grid]), setup=False)
    line_pairs = set()
    for uid in range(len(ss.Line.bus1.v)):
        b1 = int(ss.Line.bus1.v[uid])
        b2 = int(ss.Line.bus2.v[uid])
        line_pairs.add(tuple(sorted((b1, b2))))

    for fb, tb in pairs:
        if tuple(sorted((int(fb), int(tb)))) not in line_pairs:
            raise ValueError(
                f"No line found between bus {fb} and bus {tb} in grid '{grid}'."
            )


def _validate_gen_voltage_setpoints(grid, setpoints_dict, voltage_limit_min, voltage_max_pu=1.2):
    """Raise ValueError if a gen index is not a generator or vm_pu is outside [voltage_limit_min, voltage_max_pu]."""
    if grid not in _CASE_MAP:
        return

    ss = andes.load(andes.get_case(_CASE_MAP[grid]), setup=False)
    valid_gen_1based = [int(idx) for idx in ss.PV.idx.v.tolist()]
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
    
    # Grid change invalidates old line outages (unless AI also set new ones this turn)
    if "grid" in updates and updates["grid"] != current_inputs.grid:
        if "contingency_lines" not in updates:
            updates["contingency_lines"] = None
            
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

