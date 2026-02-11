"""Unit tests for MCP tool wrappers. One test per tool: node called, state updated, return shape."""
from unittest.mock import Mock, patch

from langchain_core.messages import HumanMessage, AIMessage

from agent.utils.common_utils import create_initial_state
from agent.schemas.inputs import Inputs
from agent.schemas.planner import MultiStepPlan, StepType

# Patch setup_dependencies before tools module runs so tests don't need real Ollama.
with patch("agent.mcp_server.tools.setup_dependencies") as _mock_setup:
    _mock_setup.return_value = (Mock(), {}, Mock())
    from agent.mcp_server import tools


def _mock_state():
    return create_initial_state()


# ---------------------------------------------------------------------------
# One test per tool: node called with state, update_state called, return shape
# ---------------------------------------------------------------------------


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.classify_message")
def test_classify_message_tool(mock_classify, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_classify.return_value = {"message_type": "generation"}

    out = tools.classify_message_tool("generate curve", "s1")

    call_state = mock_classify.call_args[0][0]
    assert call_state["messages"][-1].content == "generate curve"
    mock_classify.assert_called_once()
    mock_sm.update_state.assert_called_once_with("s1", {"message_type": "generation"})
    assert out["message_type"] == "generation"
    assert out["success"] is True
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.router")
def test_route_request_tool(mock_router, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_router.return_value = {"next": "question_general", "is_compound": False, "node_response": {"message": "route"}}

    out = tools.route_request_tool("s1")

    mock_router.assert_called_once()
    mock_sm.update_state.assert_called_once_with("s1", mock_router.return_value)
    assert out["next_tool"] == "question_general"
    assert out["is_compound"] is False
    assert out["success"] is True
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.question_general_agent")
def test_question_general_tool(mock_agent, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    last_message_at_call = []

    def capture_and_return(state, *args, **kwargs):
        last_message_at_call.append(state["messages"][-1].content if state.get("messages") else None)
        return {"messages": [AIMessage(content="Answer.")]}

    mock_agent.side_effect = capture_and_return

    def merge(sid, updates):
        st = mock_sm.get_state.return_value
        if "messages" in updates:
            st["messages"].extend(updates["messages"])

    mock_sm.update_state.side_effect = merge

    out = tools.question_general_tool("what is pv curve?", "s1")

    assert last_message_at_call[0] == "what is pv curve?"
    mock_agent.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["response"] == "Answer."
    assert out["success"] is True
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.question_parameter_agent")
def test_question_parameter_tool(mock_agent, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    last_message_at_call = []

    def capture_and_return(state, *args, **kwargs):
        last_message_at_call.append(state["messages"][-1].content if state.get("messages") else None)
        return {"messages": [AIMessage(content="Bus ID is the monitor bus.")]}

    mock_agent.side_effect = capture_and_return

    def merge(sid, updates):
        st = mock_sm.get_state.return_value
        if "messages" in updates:
            st["messages"].extend(updates["messages"])

    mock_sm.update_state.side_effect = merge

    out = tools.question_parameter_tool("explain bus_id", "s1")

    assert last_message_at_call[0] == "explain bus_id"
    mock_agent.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["response"] == "Bus ID is the monitor bus."
    assert out["success"] is True


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.parameter_agent")
def test_modify_parameters_tool(mock_agent, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.get_state.return_value["inputs"] = Inputs(grid="ieee14", bus_id=3)
    mock_sm.serialize_state.return_value = {}
    mock_agent.return_value = {}

    out = tools.modify_parameters_tool("set grid to ieee39", "s1")

    assert mock_agent.call_args[0][0]["messages"][-1].content == "set grid to ieee39"
    mock_agent.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert "updated_parameters" in out
    assert "current_inputs" in out
    assert out["current_inputs"]["grid"] == "ieee14"
    assert out["success"] is True


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.generation_agent")
def test_generate_pv_curve_tool(mock_gen, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.get_state.return_value["messages"] = [HumanMessage(content="generate")]
    mock_sm.serialize_state.return_value = {}
    last_message_at_call = []

    def capture_and_return(state, *args, **kwargs):
        last_message_at_call.append(state["messages"][-1].content if state.get("messages") else None)
        return {"messages": [AIMessage(content="Done")], "results": {"save_path": "/tmp/plot.png"}}

    mock_gen.side_effect = capture_and_return

    def merge(sid, updates):
        st = mock_sm.get_state.return_value
        if "messages" in updates:
            st["messages"].extend(updates["messages"])
        if "results" in updates:
            st["results"] = updates["results"]

    mock_sm.update_state.side_effect = merge

    out = tools.generate_pv_curve_tool("generate", "s1")

    assert last_message_at_call[0] == "generate"
    mock_gen.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["success"] is True
    assert out["results"] == {"save_path": "/tmp/plot.png"}
    assert out["image_file_url"] == "file:///tmp/plot.png"
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.analysis_agent")
def test_analyze_pv_curve_tool(mock_analysis, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.get_state.return_value["messages"] = [HumanMessage(content="analyze")]
    mock_sm.serialize_state.return_value = {}
    mock_analysis.return_value = {
        "messages": [AIMessage(content="Analysis.")],
        "node_response": Mock(model_dump=lambda: {"data": {"analysis": "Voltage margin 0.2 pu."}}),
    }

    def merge(sid, updates):
        st = mock_sm.get_state.return_value
        if "messages" in updates:
            st["messages"].extend(updates["messages"])

    mock_sm.update_state.side_effect = merge

    out = tools.analyze_pv_curve_tool("analyze", "s1")

    mock_analysis.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["success"] is True
    assert out["analysis"] == "Voltage margin 0.2 pu."
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.planner_agent")
def test_plan_steps_tool(mock_planner, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    plan = MultiStepPlan(description="Two steps", steps=[StepType(action="parameter", content="set grid"), StepType(action="generation", content="generate")])
    mock_planner.return_value = {"plan": plan}

    def merge(sid, updates):
        mock_sm.get_state.return_value.update(updates)

    mock_sm.update_state.side_effect = merge

    out = tools.plan_steps_tool("set grid then generate", "s1")

    assert mock_planner.call_args[0][0]["messages"][-1].content == "set grid then generate"
    mock_planner.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["success"] is True
    assert out["plan"]["description"] == "Two steps"
    assert out["steps_count"] == 2


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.step_controller")
def test_step_controller_tool(mock_sc, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_sc.return_value = {"next": "advance_step", "node_response": {"data": {"action": "parameter"}}}

    out = tools.step_controller_tool("s1")

    mock_sc.assert_called_once()
    mock_sm.update_state.assert_called_once_with("s1", mock_sc.return_value)
    assert out["next_tool"] == "advance_step"
    assert out["success"] is True
    assert "step_info" in out
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.advance_step")
def test_advance_step_tool(mock_advance, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_advance.return_value = {"next": "summary"}

    def merge(sid, updates):
        mock_sm.get_state.return_value.update(updates)

    mock_sm.update_state.side_effect = merge

    out = tools.advance_step_tool("s1")

    mock_advance.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["next_tool"] == "summary"
    assert "current_step" in out
    assert out["success"] is True


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.error_handler_agent")
def test_handle_error_tool(mock_handler, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_handler.return_value = {"retry_node": "generation", "messages": [AIMessage(content="Retry.")]}

    def merge(sid, updates):
        st = mock_sm.get_state.return_value
        if "messages" in updates:
            st["messages"].extend(updates["messages"])

    mock_sm.update_state.side_effect = merge

    out = tools.handle_error_tool("s1")

    mock_handler.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["retry_node"] == "generation"
    assert out["success"] is True
    assert "state" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.summary_agent")
def test_summarize_results_tool(mock_summary, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_summary.return_value = {"messages": [AIMessage(content="Summary of 2 steps.")]}

    def merge(sid, updates):
        st = mock_sm.get_state.return_value
        if "messages" in updates:
            st["messages"].extend(updates["messages"])

    mock_sm.update_state.side_effect = merge

    out = tools.summarize_results_tool("s1")

    mock_summary.assert_called_once()
    mock_sm.update_state.assert_called_once()
    assert out["summary"] == "Summary of 2 steps."
    assert out["success"] is True


# ---------------------------------------------------------------------------
# Error handling: tools that catch exceptions return success=False
# ---------------------------------------------------------------------------


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.generation_agent")
def test_generate_pv_curve_tool_error(mock_gen, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_gen.side_effect = RuntimeError("simulation failed")

    out = tools.generate_pv_curve_tool("gen", "s1")

    assert out["success"] is False
    assert "simulation failed" in out["response"]
    assert out["results"] is None
    assert "error" in out


@patch("agent.mcp_server.tools.state_manager")
@patch("agent.mcp_server.tools.analysis_agent")
def test_analyze_pv_curve_tool_error(mock_analysis, mock_sm):
    mock_sm.get_state.return_value = _mock_state()
    mock_sm.serialize_state.return_value = {}
    mock_analysis.side_effect = ValueError("analysis failed")

    out = tools.analyze_pv_curve_tool("analyze", "s1")

    assert out["success"] is False
    assert "analysis failed" in out["response"]
    assert out["analysis"] is None
