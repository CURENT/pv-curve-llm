import os
from datetime import datetime
from unittest.mock import patch
import pytest

from agent.nodes.summary import summary_agent
from agent.schemas.planner import MultiStepPlan, StepType
from agent.schemas.response import NodeResponse
from langchain_core.messages import HumanMessage
from agent.core import setup_dependencies
from agent.utils.common_utils import create_initial_state
from agent.nodes.planner import planner_agent

# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def get_initial_state(plan=None, step_results=None):
    return {
        "plan": plan,
        "step_results": step_results if step_results is not None else [],
    }


def _make_plan(description: str, actions: list):
    steps = [StepType(action=a, content=f"Step {a}") for a in actions]
    return MultiStepPlan(description=description, steps=steps)


def _assert_summary_shape_and_content(result, expected_steps_count, expected_plan_description, step_results):
    assert "messages" in result and len(result["messages"]) == 1
    assert "node_response" in result
    nr = result["node_response"]
    assert isinstance(nr, NodeResponse)
    assert nr.node_type == "summary"
    assert nr.success is True
    assert nr.data["steps_completed"] == expected_steps_count
    assert nr.data["plan_description"] == expected_plan_description
    assert expected_plan_description in nr.data["summary"]
    assert nr.message == nr.data["summary"]
    assert isinstance(nr.timestamp, datetime)

    # Same truncation as summary node: result[:100] + "..." if len > 100
    for i, sr in enumerate(step_results):
        result_text = sr["result"][:100] + "..." if len(sr["result"]) > 100 else sr["result"]
        assert f"Step {i+1}" in nr.data["summary"]
        assert result_text in nr.data["summary"] or sr["result"][:100] in nr.data["summary"]


# --------------------------------------------------------------
# Unit Tests (Mocked display only; no API in summary node)
# --------------------------------------------------------------


@patch("agent.nodes.summary.display_executing_node")
def test_summary_basic(mock_display):
    plan = _make_plan("Set param then generate", ["parameter", "generation"])
    step_results = [{"action": "parameter", "result": "Updated step_size to 0.02"}]
    state = get_initial_state(plan=plan, step_results=step_results)

    result = summary_agent(state)

    mock_display.assert_called_once_with("summary")
    _assert_summary_shape_and_content(result, 1, "Set param then generate", step_results)


@patch("agent.nodes.summary.display_executing_node")
def test_summary_multiple_steps(mock_display):
    plan = _make_plan("Two-step flow", ["parameter", "generation"])
    step_results = [
        {"action": "parameter", "result": "Set grid to ieee39"},
        {"action": "generation", "result": "PV curve generated."},
    ]
    state = get_initial_state(plan=plan, step_results=step_results)

    result = summary_agent(state)

    _assert_summary_shape_and_content(result, 2, "Two-step flow", step_results)


@patch("agent.nodes.summary.display_executing_node")
def test_summary_with_results(mock_display):
    plan = _make_plan("Generate and analyze", ["generation", "analysis"])
    step_results = [
        {"action": "generation", "result": "PV curve generated for ieee39. Plot saved."},
        {"action": "analysis", "result": "Load margin 125 MW; nose voltage 0.85 pu."},
    ]
    state = get_initial_state(plan=plan, step_results=step_results)

    result = summary_agent(state)

    _assert_summary_shape_and_content(result, 2, "Generate and analyze", step_results)


@patch("agent.nodes.summary.display_executing_node")
def test_summary_empty_plan(mock_display):
    step_results = [{"action": "unknown", "result": "Something ran."}]
    state = get_initial_state(plan=None, step_results=step_results)

    result = summary_agent(state)

    mock_display.assert_called_once_with("summary")
    assert result["node_response"].data["plan_description"] == "Unknown"
    assert "Unknown" in result["node_response"].data["summary"]
    assert "Step 1 (unknown): Something ran." in result["node_response"].data["summary"]
    assert result["node_response"].data["steps_completed"] == 1


@patch("agent.nodes.summary.display_executing_node")
def test_summary_format(mock_display):
    plan = _make_plan("One step", ["generation"])
    long_result = "A" * 150
    step_results = [{"action": "generation", "result": long_result}]
    state = get_initial_state(plan=plan, step_results=step_results)

    result = summary_agent(state)

    summary = result["node_response"].data["summary"]
    assert "A" * 100 + "..." in summary
    assert long_result not in summary
    assert "Step 1 (generation):" in summary


# --------------------------------------------------------------
# Integration Tests (real summary logic; no external API)
# --------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.parametrize("scenario", ["two_step", "three_step_with_pv"])
@patch("agent.nodes.summary.display_executing_node")
def test_integration_summary_scenarios(mock_display, scenario):
    if scenario == "two_step":
        plan = _make_plan("Two-step run", ["parameter", "generation"])
        step_results = [
            {"action": "parameter", "result": "Updated power_factor to 0.9"},
            {"action": "generation", "result": "PV curve generated."},
        ]
    else:
        plan = _make_plan("Three steps with PV", ["parameter", "generation", "analysis"])
        step_results = [
            {"action": "parameter", "result": "Set bus_id to 5"},
            {"action": "generation", "result": "PV curve for ieee39 saved."},
            {"action": "analysis", "result": "Analysis complete."},
        ]

    state = get_initial_state(plan=plan, step_results=step_results)
    result = summary_agent(state)

    assert result["node_response"].success is True
    assert result["node_response"].data["steps_completed"] == len(step_results)
    assert result["node_response"].data["plan_description"] == plan.description
    for sr in step_results:
        assert sr["result"][:50] in result["node_response"].data["summary"] or sr["result"] in result["node_response"].data["summary"]


# --------------------------------------------------------------
# Integration Test (real API: planner LLM → plan → summary)
# --------------------------------------------------------------


def _has_api_access():
    if os.getenv("OPENAI_API_KEY"):
        return True
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture
def integration_llm_and_prompts():
    if not _has_api_access():
        pytest.skip("No API access (OPENAI_API_KEY or Ollama)")
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"
    llm, prompts, _ = setup_dependencies(provider)
    return llm, prompts


@pytest.mark.integration
@patch("agent.nodes.summary.display_executing_node")
@patch("agent.nodes.planner.display_executing_node")
def test_integration_summary_with_real_plan_from_api(
    mock_planner_display, mock_summary_display, integration_llm_and_prompts
):
    llm, prompts = integration_llm_and_prompts
    state = create_initial_state()
    state["messages"] = [HumanMessage(content="Set step size to 0.02 then generate PV curve")]

    planner_updates = planner_agent(state, llm, prompts)
    state["plan"] = planner_updates["plan"]
    state["step_results"] = [
        {"action": step.action, "result": f"Completed: {step.content}"}
        for step in planner_updates["plan"].steps
    ]

    result = summary_agent(state)

    mock_planner_display.assert_called_once_with("planner")
    mock_summary_display.assert_called_once_with("summary")
    assert result["node_response"].node_type == "summary"
    assert result["node_response"].success is True
    assert result["node_response"].data["steps_completed"] == len(state["step_results"])
    assert result["node_response"].data["plan_description"] == state["plan"].description
    assert state["plan"].description in result["node_response"].data["summary"]
    for i, step in enumerate(state["plan"].steps):
        assert f"Step {i+1}" in result["node_response"].data["summary"]
        assert step.action in result["node_response"].data["summary"]
