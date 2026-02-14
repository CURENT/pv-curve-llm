"""Integration test: verify each MCP tool is mapped to the correct node (smoke test)."""
from unittest.mock import Mock, patch

import pytest

from agent.utils.common_utils import create_initial_state

# Patch before importing tools so setup_dependencies doesn't run
with patch("agent.core.setup_dependencies") as _:
    _.return_value = (Mock(), {}, Mock())
    from agent.mcp_server import tools

# (tool_name, node_name) - node_name is the attribute in agent.mcp_server.tools
NODE_TOOL_MAPPING = [
    ("classify_message_tool", "classify_message"),
    ("route_request_tool", "router"),
    ("question_general_tool", "question_general_agent"),
    ("question_parameter_tool", "question_parameter_agent"),
    ("modify_parameters_tool", "parameter_agent"),
    ("generate_pv_curve_tool", "generation_agent"),
    ("analyze_pv_curve_tool", "analysis_agent"),
    ("plan_steps_tool", "planner_agent"),
    ("step_controller_tool", "step_controller"),
    ("advance_step_tool", "advance_step"),
    ("handle_error_tool", "error_handler_agent"),
    ("summarize_results_tool", "summary_agent"),
]


def _call_tool(tool_name, session_id="s1", user_message="x"):
    tool_fn = getattr(tools, tool_name)
    if tool_name in (
        "route_request_tool",
        "step_controller_tool",
        "advance_step_tool",
        "handle_error_tool",
        "summarize_results_tool",
    ):
        return tool_fn(session_id)
    return tool_fn(user_message, session_id)


@pytest.mark.integration
@pytest.mark.parametrize("tool_name,node_name", NODE_TOOL_MAPPING)
@patch("agent.mcp_server.tools.state_manager")
def test_all_nodes_mapped(mock_sm, tool_name, node_name):
    mock_sm.get_state.return_value = create_initial_state()
    mock_sm.serialize_state.return_value = {}
    state = mock_sm.get_state.return_value

    def merge(sid, updates):
        if "messages" in updates:
            state.setdefault("messages", []).extend(updates["messages"])
        state.update({k: v for k, v in (updates or {}).items() if k != "messages"})

    mock_sm.update_state.side_effect = merge

    with patch(f"agent.mcp_server.tools.{node_name}") as mock_node:
        mock_node.return_value = {}
        result = _call_tool(tool_name)
        mock_node.assert_called_once()
        assert isinstance(result, dict)
        assert result.get("success") is True