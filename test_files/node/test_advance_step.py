import pytest
from unittest.mock import patch

from langchain_core.messages import AIMessage
from agent.nodes.advance_step import advance_step
from agent.schemas.planner import MultiStepPlan, StepType


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def create_plan(steps, description: str = "test plan"):
    """Create a MultiStepPlan from a list of StepType."""
    return MultiStepPlan(steps=steps, description=description)


def get_state(plan=None, current_step: int = 0, step_results=None, messages=None):
    """Create state for advance_step."""
    return {
        "plan": plan,
        "current_step": current_step,
        "step_results": step_results if step_results is not None else [],
        "messages": messages if messages is not None else [],
    }


# --------------------------------------------------------------
# Unit Tests
# --------------------------------------------------------------


@patch("agent.nodes.advance_step.display_executing_node")
def test_advance_to_next_step(mock_display):
    plan = create_plan(
        steps=[
            StepType(action="parameter", content="Set grid", parameters=None),
            StepType(action="generation", content="Generate", parameters=None),
        ]
    )
    state = get_state(plan=plan, current_step=0, messages=[AIMessage(content="Updated grid to ieee39")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == 1
    assert result["next"] == "step_controller"
    assert len(result["step_results"]) == 1
    assert result["step_results"][0]["step"] == 0
    assert result["step_results"][0]["action"] == "parameter"
    assert result["step_results"][0]["result"] == "Updated grid to ieee39"


@patch("agent.nodes.advance_step.display_executing_node")
def test_store_step_result(mock_display):
    plan = create_plan(steps=[StepType(action="generation", content="Generate", parameters=None)])
    state = get_state(plan=plan, current_step=0, messages=[AIMessage(content="PV curve generated.")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert len(result["step_results"]) == 1
    assert result["step_results"][0]["step"] == 0
    assert result["step_results"][0]["action"] == "generation"
    assert result["step_results"][0]["result"] == "PV curve generated."


@patch("agent.nodes.advance_step.display_executing_node")
def test_plan_completion(mock_display):
    plan = create_plan(steps=[StepType(action="generation", content="Generate", parameters=None)])
    state = get_state(plan=plan, current_step=0, messages=[AIMessage(content="Done")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == 1
    assert result["next"] == "summary"


@patch("agent.nodes.advance_step.display_executing_node")
def test_continue_planning(mock_display):
    plan = create_plan(
        steps=[
            StepType(action="parameter", content="Set", parameters=None),
            StepType(action="generation", content="Generate", parameters=None),
        ]
    )
    state = get_state(plan=plan, current_step=0, messages=[AIMessage(content="Updated")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == 1
    assert result["next"] == "step_controller"


@patch("agent.nodes.advance_step.display_executing_node")
def test_with_no_plan(mock_display):
    state = get_state(plan=None, current_step=0, messages=[AIMessage(content="Something")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == 1
    assert result["next"] == "summary"
    assert len(result["step_results"]) == 1
    assert result["step_results"][0]["action"] == "unknown"


@patch("agent.nodes.advance_step.display_executing_node")
def test_advance_with_no_messages(mock_display):
    plan = create_plan(steps=[StepType(action="parameter", content="Set", parameters=None)])
    state = get_state(plan=plan, current_step=0, messages=[])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == 1
    assert result["step_results"] == []
    assert result["next"] == "summary"


@patch("agent.nodes.advance_step.display_executing_node")
def test_empty_plan_routes_to_summary(mock_display):
    plan = create_plan(steps=[])
    state = get_state(plan=plan, current_step=0, messages=[AIMessage(content="Done")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == 1
    assert result["next"] == "summary"


# --------------------------------------------------------------
# Integration Tests
# --------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.parametrize(
    "num_steps, current_step, expected_next",
    [
        (2, 0, "step_controller"),
        (2, 1, "summary"),
        (3, 1, "step_controller"),
    ],
)
@patch("agent.nodes.advance_step.display_executing_node")
def test_integration_advance_step_routing(mock_display, num_steps, current_step, expected_next):
    steps = [StepType(action="parameter", content=f"Step {i}", parameters=None) for i in range(num_steps)]
    plan = create_plan(steps=steps)
    state = get_state(plan=plan, current_step=current_step, messages=[AIMessage(content="OK")])

    result = advance_step(state)

    mock_display.assert_called_once_with("advance_step")
    assert result["current_step"] == current_step + 1
    assert result["next"] == expected_next
    assert len(result["step_results"]) == 1
