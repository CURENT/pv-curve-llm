"""Unit tests for FastMCP server: initialization, tool registration, and session_id handling."""
from unittest.mock import Mock, patch

# Patch at source so the patch is active when tools module is first loaded
with patch("agent.core.setup_dependencies") as _:
    _.return_value = (Mock(), {}, Mock())
    from agent.mcp_server import server
    from agent.mcp_server import tools

from agent.utils.common_utils import create_initial_state
from fastmcp.tools import FunctionTool

# Tool names exposed on the server module (registered with @mcp.tool()).
# When analyze_pv_curve is uncommented in server.py, add "analyze_pv_curve" here.
EXPECTED_TOOL_NAMES = [
    "get_session_id",
    "classify_message",
    "route_request",
    "question_general",
    "question_parameter",
    "modify_parameters",
    "generate_pv_curve",
    "plan_steps",
    "step_controller",
    "advance_step",
    "handle_error",
    "summarize_results",
]


def test_server_initialization():
    from fastmcp import FastMCP
    assert hasattr(server, "mcp")
    assert server.mcp is not None
    assert isinstance(server.mcp, FastMCP)


def test_tool_registration():
    for name in EXPECTED_TOOL_NAMES:
        assert hasattr(server, name), f"Tool {name!r} not found on server module"
        tool = getattr(server, name)
        assert isinstance(tool, FunctionTool), f"Tool {name!r} should be a registered FunctionTool"
    assert len(EXPECTED_TOOL_NAMES) >= 11
    assert hasattr(server, "generate_pv_curve")


@patch("agent.mcp_server.tools.state_manager")
def test_tool_decorators(mock_sm):
    mock_sm.get_state.return_value = create_initial_state()
    # FunctionTool wraps the original function in .fn; call it to verify decorator works
    out = server.get_session_id.fn()
    assert isinstance(out, dict)
    assert "session_id" in out
    assert "success" in out
    assert out["success"] is True


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.classify_message")
def test_missing_session_id(mock_classify, mock_sm):
    mock_sm.get_state.return_value = create_initial_state()
    mock_sm.serialize_state.return_value = {}
    mock_classify.return_value = {"message_type": "question_general"}
    result = tools.classify_message_tool("hello", "")
    assert isinstance(result, dict)
    assert "success" in result


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.classify_message")
def test_invalid_session_id(mock_classify, mock_sm):
    mock_sm.get_state.return_value = create_initial_state()
    mock_sm.serialize_state.return_value = {}
    mock_classify.return_value = {"message_type": "parameter"}
    result = tools.classify_message_tool("set bus 5", None)
    assert isinstance(result, dict)
    assert "success" in result