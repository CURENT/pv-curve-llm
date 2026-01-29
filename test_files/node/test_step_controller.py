import pytest
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage
from agent.nodes.step_controller import step_controller
from agent.schemas.inputs import Inputs
from agent.schemas.planner import MultiStepPlan, StepType, StepParameters
from agent.schemas.response import NodeResponse


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def create_plan(steps, description: str = "test plan"):
    """Create a MultiStepPlan from a list of StepType."""
    return MultiStepPlan(steps=steps, description=description)


def get_state(plan: MultiStepPlan | None, current_step: int = 0, inputs: Inputs | None = None):
    """Create initial state for step_controller."""
    return {
        "plan": plan,
        "current_step": current_step,
        "inputs": inputs or Inputs(),
    }


# --------------------------------------------------------------
# Unit Tests (parameter steps)
# --------------------------------------------------------------


@patch("agent.nodes.step_controller.display_executing_node")
def test_execute_parameter_step_updates_inputs_and_node_response(mock_display):
    inputs = Inputs(grid="ieee39", bus_id=5, power_factor=0.95)

    step_params = StepParameters(
        grid="IEEE 118",   # will be normalized to ieee118
        bus_id="10",       # string -> int
        power_factor="0.9" # string -> float
    )
    plan = create_plan(
        steps=[
            StepType(
                action="parameter",
                content="Update parameters",
                parameters=step_params,
            )
        ],
        description="update params",
    )
    state = get_state(plan, current_step=0, inputs=inputs)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")
    assert result["next"] == "advance_step"

    reply = result["messages"][0]
    assert isinstance(reply, AIMessage)
    assert "Updated" in reply.content

    new_inputs = result["inputs"]
    assert isinstance(new_inputs, Inputs)
    assert new_inputs.grid == "ieee118"
    assert new_inputs.bus_id == 10
    assert new_inputs.power_factor == pytest.approx(0.9)

    node_response = result["node_response"]
    assert isinstance(node_response, NodeResponse)
    assert node_response.node_type == "step_controller"
    assert node_response.success is True
    assert node_response.data["step_executed"] == "parameter"
    assert set(node_response.data["updated_parameters"]) == {"grid", "bus_id", "power_factor"}
    assert node_response.data["current_inputs"]["grid"] == "ieee118"
    assert node_response.data["current_inputs"]["bus_id"] == 10
    assert node_response.data["current_inputs"]["power_factor"] == pytest.approx(0.9)

# --------------------------------------------------------------
# Unit Tests (non-parameter steps)
# --------------------------------------------------------------


@patch("agent.nodes.step_controller.display_executing_node")
def test_execute_generation_step_routes_to_generation(mock_display):
    plan = create_plan(
        steps=[
            StepType(
                action="generation",
                content="Generate PV curve",
                parameters=None,
            )
        ]
    )
    state = get_state(plan, current_step=0)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")

    msg = result["messages"][0]
    assert isinstance(msg, HumanMessage)
    assert msg.content == "Generate PV curve"
    assert result["message_type"] == "generation"
    assert result["next"] == "generation"
    assert "node_response" not in result


@patch("agent.nodes.step_controller.display_executing_node")
def test_execute_analysis_step_routes_to_analysis(mock_display):
    plan = create_plan(
        steps=[
            StepType(
                action="analysis",
                content="Analyze the results",
                parameters=None,
            )
        ]
    )
    state = get_state(plan, current_step=0)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")

    msg = result["messages"][0]
    assert isinstance(msg, HumanMessage)
    assert msg.content == "Analyze the results"
    assert result["message_type"] == "analysis"
    assert result["next"] == "analysis"
    assert "node_response" not in result


@patch("agent.nodes.step_controller.display_executing_node")
def test_execute_question_step_routes_to_question_general(mock_display):
    plan = create_plan(
        steps=[
            StepType(
                action="question",
                content="What does this PV curve tell us?",
                parameters=None,
            )
        ]
    )
    state = get_state(plan, current_step=0)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")

    msg = result["messages"][0]
    assert isinstance(msg, HumanMessage)
    assert msg.content == "What does this PV curve tell us?"
    # special case in code: question → question_general
    assert result["message_type"] == "question"
    assert result["next"] == "question_general"
    assert "node_response" not in result


@patch("agent.nodes.step_controller.display_executing_node")
def test_execute_parameter_step_with_no_parameters_routes_to_parameter(mock_display):
    plan = create_plan(
        steps=[
            StepType(
                action="parameter",
                content="Set something (no params extracted)",
                parameters=None,
            )
        ]
    )
    state = get_state(plan, current_step=0)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")
    msg = result["messages"][0]
    assert isinstance(msg, HumanMessage)
    assert msg.content == "Set something (no params extracted)"
    assert result["message_type"] == "parameter"
    assert result["next"] == "parameter"
    assert "node_response" not in result


# --------------------------------------------------------------
# Unit Tests (plan completion / edge cases)
# --------------------------------------------------------------


@patch("agent.nodes.step_controller.display_executing_node")
def test_missing_plan_routes_to_summary(mock_display):
    state = get_state(plan=None, current_step=0)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")
    assert result == {"next": "summary"}


@patch("agent.nodes.step_controller.display_executing_node")
def test_current_step_past_end_routes_to_summary(mock_display):
    # one-step plan, but current_step points past the end
    plan = create_plan(
        steps=[
            StepType(action="generation", content="Generate", parameters=None)
        ]
    )
    state = get_state(plan, current_step=1)  # len(steps) == 1 → index 1 is past the end

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")
    assert result == {"next": "summary"}

# --------------------------------------------------------------
# Integration Tests (parametrized step types)
# --------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.parametrize(
    "action, content, expected_next",
    [
        ("generation", "Generate PV curve", "generation"),
        ("analysis", "Analyze the results", "analysis"),
        ("question", "What is a PV curve?", "question_general"),
    ],
)
@patch("agent.nodes.step_controller.display_executing_node")
def test_integration_step_controller_routing(mock_display, action, content, expected_next):
    plan = create_plan(
        steps=[StepType(action=action, content=content, parameters=None)]
    )
    state = get_state(plan, current_step=0)

    result = step_controller(state)

    mock_display.assert_called_once_with("step_controller")

    msg = result["messages"][0]
    assert isinstance(msg, HumanMessage)
    assert msg.content == content
    assert result["next"] == expected_next

