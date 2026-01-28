import os
from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from langchain_core.messages import HumanMessage
from agent.nodes.planner import planner_agent
from agent.schemas.planner import MultiStepPlan, StepType, StepParameters
from agent.schemas.response import NodeResponse
from agent.core import setup_dependencies

# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------

def create_mock_llm_plan(plan=None, side_effect=None):
    if plan is None and side_effect is None:
        raise ValueError("provide plan or side_effect")
    mock_llm = Mock()
    structured_llm = Mock()
    if side_effect:
        structured_llm.invoke.side_effect = side_effect
    else:
        structured_llm.invoke.return_value = plan
    mock_llm.with_structured_output.return_value = structured_llm
    return mock_llm


def get_base_prompts():
    return {
        "planner": {
            "system": "Break down the user's compound request into sequential steps.",
            "user": "Break down this request: {user_input}",
        }
    }


def get_initial_state(user_message: str, inputs=None):
    state = {"messages": [HumanMessage(content=user_message)]}
    if inputs is not None:
        state["inputs"] = inputs
    return state


def _assert_planner_api_calls_and_response(mock_llm, prompts, user_message, result, api_plan):
    mock_llm.with_structured_output.assert_called_once_with(MultiStepPlan)
    structured_llm = mock_llm.with_structured_output.return_value
    assert structured_llm.invoke.called
    call_args = structured_llm.invoke.call_args[0][0]
    assert isinstance(call_args, list)
    assert len(call_args) == 2
    assert call_args[0]["role"] == "system"
    assert prompts["planner"]["system"] in call_args[0]["content"]
    assert call_args[1]["role"] == "user"
    assert call_args[1]["content"] == prompts["planner"]["user"].format(user_input=user_message)

    assert result["plan"] is api_plan
    assert result["current_step"] == 0
    assert result["step_results"] == []
    assert result["node_response"].data["steps_count"] == len(api_plan.steps)
    assert result["node_response"].data["plan_description"] == api_plan.description
    assert result["node_response"].data["plan"] == api_plan.model_dump()

    node_response = result["node_response"]
    assert isinstance(node_response, NodeResponse)
    assert node_response.node_type == "planner"
    assert node_response.success is True
    assert isinstance(node_response.timestamp, datetime)
    assert str(len(api_plan.steps)) in node_response.message
    assert api_plan.description in node_response.message


# --------------------------------------------------------------
# Unit Tests (Mocked API)
# --------------------------------------------------------------


@patch("agent.nodes.planner.display_executing_node")
def test_plan_simple_two_step(mock_display):
    user_message = "Set power factor to 0.9, then generate the PV curve"
    api_plan = MultiStepPlan(
        steps=[
            StepType(action="parameter", content="Set power factor to 0.9", parameters=StepParameters(power_factor=0.9)),
            StepType(action="generation", content="Generate PV curve", parameters=None),
        ],
        description="Set PF then generate",
    )
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = planner_agent(state, mock_llm, prompts)

    _assert_planner_api_calls_and_response(mock_llm, prompts, user_message, result, api_plan)
    assert len(result["plan"].steps) == 2
    assert result["plan"].steps[0].action == "parameter"
    assert result["plan"].steps[1].action == "generation"
    mock_display.assert_called_once_with("planner")


@patch("agent.nodes.planner.display_executing_node")
def test_plan_three_step(mock_display):
    user_message = "Set the grid to ieee39, then generate the curve, then analyze the results"
    api_plan = MultiStepPlan(
        steps=[
            StepType(action="parameter", content="Set grid to ieee39", parameters=StepParameters(grid="ieee39")),
            StepType(action="generation", content="Generate PV curve", parameters=None),
            StepType(action="analysis", content="Analyze the results", parameters=None),
        ],
        description="Parameter, generate, analyze",
    )
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = planner_agent(state, mock_llm, prompts)

    _assert_planner_api_calls_and_response(mock_llm, prompts, user_message, result, api_plan)
    assert len(result["plan"].steps) == 3
    assert result["plan"].steps[0].action == "parameter"
    assert result["plan"].steps[1].action == "generation"
    assert result["plan"].steps[2].action == "analysis"


@patch("agent.nodes.planner.display_executing_node")
def test_plan_with_parameters(mock_display):
    user_message = "Set the grid to ieee39, bus to 10, and power factor to 0.95, then generate the PV curve"
    api_plan = MultiStepPlan(
        steps=[
            StepType(
                action="parameter",
                content="Set grid, bus, power factor",
                parameters=StepParameters(grid="ieee39", bus_id=10, power_factor=0.95),
            ),
            StepType(action="generation", content="Generate PV curve", parameters=None),
        ],
        description="Set multiple parameters then generate",
    )
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = planner_agent(state, mock_llm, prompts)

    _assert_planner_api_calls_and_response(mock_llm, prompts, user_message, result, api_plan)
    params = result["plan"].steps[0].parameters
    assert params.grid == "ieee39"
    assert params.bus_id == 10
    assert params.power_factor == 0.95


@patch("agent.nodes.planner.display_executing_node")
def test_plan_with_inputs_context(mock_display):
    user_message = "Set bus to 10, then generate"
    api_plan = MultiStepPlan(
        steps=[
            StepType(action="parameter", content="Set bus to 10", parameters=StepParameters(bus_id=10)),
            StepType(action="generation", content="Generate", parameters=None),
        ],
        description="Set bus then generate",
    )
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = get_base_prompts()
    inputs = {"grid": "ieee39", "bus_id": 5, "power_factor": 0.95}
    state = get_initial_state(user_message, inputs=inputs)

    result = planner_agent(state, mock_llm, prompts)

    call_args = mock_llm.with_structured_output.return_value.invoke.call_args[0][0]
    assert "Current Parameters" in call_args[0]["content"]
    assert "ieee39" in call_args[0]["content"]
    assert result["plan"] is api_plan


@patch("agent.nodes.planner.display_executing_node")
def test_plan_comparison(mock_display):
    user_message = "I want to compare two runs: set power factor to 0.9 and generate a curve, then set power factor to 0.8 and generate another curve"
    api_plan = MultiStepPlan(
        steps=[
            StepType(action="parameter", content="Set power factor 0.9", parameters=StepParameters(power_factor=0.9)),
            StepType(action="generation", content="Generate curve", parameters=None),
            StepType(action="parameter", content="Set power factor 0.8", parameters=StepParameters(power_factor=0.8)),
            StepType(action="generation", content="Generate curve", parameters=None),
        ],
        description="Compare two configurations",
    )
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = planner_agent(state, mock_llm, prompts)

    _assert_planner_api_calls_and_response(mock_llm, prompts, user_message, result, api_plan)
    assert len(result["plan"].steps) == 4


@patch("agent.nodes.planner.display_executing_node")
def test_plan_analysis_step(mock_display):
    user_message = "Set the grid to ieee39, then generate the curve and analyze the results"
    api_plan = MultiStepPlan(
        steps=[
            StepType(action="parameter", content="Set grid to ieee39", parameters=StepParameters(grid="ieee39")),
            StepType(action="generation", content="Generate PV curve", parameters=None),
            StepType(action="analysis", content="Analyze the results", parameters=None),
        ],
        description="Parameter, generate, analysis",
    )
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = planner_agent(state, mock_llm, prompts)

    _assert_planner_api_calls_and_response(mock_llm, prompts, user_message, result, api_plan)
    actions = [s.action for s in result["plan"].steps]
    assert "analysis" in actions


@patch("agent.nodes.planner.display_executing_node")
def test_plan_api_failure(mock_display):
    mock_llm = create_mock_llm_plan(side_effect=Exception("API Connection Failed"))
    prompts = get_base_prompts()
    state = get_initial_state("Set power factor to 0.9 then generate the curve")

    with pytest.raises(Exception, match="API Connection Failed"):
        planner_agent(state, mock_llm, prompts)

    mock_llm.with_structured_output.assert_called_once_with(MultiStepPlan)


@patch("agent.nodes.planner.display_executing_node")
def test_plan_empty_messages(mock_display):
    mock_llm = create_mock_llm_plan(plan=MultiStepPlan(steps=[], description="Empty"))
    prompts = get_base_prompts()
    state = {"messages": []}

    with pytest.raises(IndexError):
        planner_agent(state, mock_llm, prompts)


@patch("agent.nodes.planner.display_executing_node")
def test_plan_missing_prompts_key(mock_display):
    api_plan = MultiStepPlan(steps=[StepType(action="parameter", content="Set X", parameters=None)], description="One")
    mock_llm = create_mock_llm_plan(plan=api_plan)
    prompts = {}
    state = get_initial_state("Set power factor to 0.9")

    with pytest.raises(KeyError):
        planner_agent(state, mock_llm, prompts)


@patch("agent.nodes.planner.display_executing_node")
def test_plan_missing_messages_key(mock_display):
    mock_llm = create_mock_llm_plan(plan=MultiStepPlan(steps=[], description=""))
    prompts = get_base_prompts()
    state = {}

    with pytest.raises(KeyError):
        planner_agent(state, mock_llm, prompts)


# --------------------------------------------------------------
# Integration Tests (Real API)
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
        pytest.skip("No API access available (requires OPENAI_API_KEY or running Ollama)")
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"
    llm, prompts, _ = setup_dependencies(provider)
    return llm, prompts


@pytest.mark.integration
@pytest.mark.parametrize("user_message", [
    "Set power factor to 0.9 then generate PV curve",
    "Set grid to ieee39 after that generate curve",
    "Change bus to 10 then generate",
])
@patch("agent.nodes.planner.display_executing_node")
def test_integration_plan_two_step(mock_display, integration_llm_and_prompts, user_message):
    llm, prompts = integration_llm_and_prompts
    state = get_initial_state(user_message)
    result = planner_agent(state, llm, prompts)

    assert result["node_response"].success is True
    assert len(result["plan"].steps) >= 2
    assert result["current_step"] == 0
    assert result["step_results"] == []
    actions = [s.action for s in result["plan"].steps]
    assert "parameter" in actions or "generation" in actions


@pytest.mark.integration
@pytest.mark.parametrize("user_message", [
    "Set the grid to ieee39, then generate the curve, then analyze the results",
    "Set power factor to 0.9 and bus to 10, generate the curve, then analyze the results",
])
@patch("agent.nodes.planner.display_executing_node")
def test_integration_plan_multi_step(mock_display, integration_llm_and_prompts, user_message):
    llm, prompts = integration_llm_and_prompts
    state = get_initial_state(user_message)
    result = planner_agent(state, llm, prompts)

    assert result["node_response"].success is True
    assert len(result["plan"].steps) >= 2
    assert result["node_response"].data["steps_count"] == len(result["plan"].steps)
