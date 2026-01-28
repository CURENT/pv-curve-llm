from datetime import datetime
from unittest.mock import patch
import pytest

from langchain_core.messages import HumanMessage
from agent.nodes.route import router
from agent.schemas.response import NodeResponse

# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def get_initial_state(user_message: str, message_type: str = "question_general"):
    """Create initial state with user message and message_type."""
    return {
        "messages": [HumanMessage(content=user_message)],
        "message_type": message_type,
    }


def _assert_route_response(
    result, expected_next: str, expected_is_compound: bool, message_type: str
):
    """Assert routing response structure and values."""
    assert "next" in result
    assert "is_compound" in result
    assert "node_response" in result
    assert result["next"] == expected_next
    assert result["is_compound"] == expected_is_compound

    node_response = result["node_response"]
    assert isinstance(node_response, NodeResponse)
    assert node_response.node_type == "router"
    assert node_response.success is True
    assert isinstance(node_response.timestamp, datetime)
    assert node_response.data["next"] == expected_next
    assert node_response.data["message_type"] == message_type
    assert node_response.data["is_compound"] == expected_is_compound
    assert expected_next in node_response.message


# --------------------------------------------------------------
# Unit Tests (Routing Logic)
# --------------------------------------------------------------


@patch("agent.nodes.route.display_executing_node")
def test_route_question_general(mock_display):
    state = get_initial_state("What is a PV curve?", message_type="question_general")
    result = router(state)
    _assert_route_response(result, "question_general", False, "question_general")
    mock_display.assert_called_once_with("router")


@patch("agent.nodes.route.display_executing_node")
def test_route_question_parameter(mock_display):
    state = get_initial_state(
        "What does power factor mean?", message_type="question_parameter"
    )
    result = router(state)
    _assert_route_response(result, "question_parameter", False, "question_parameter")


@patch("agent.nodes.route.display_executing_node")
def test_route_parameter(mock_display):
    state = get_initial_state("Set power factor to 0.9", message_type="parameter")
    result = router(state)
    _assert_route_response(result, "parameter", False, "parameter")


@patch("agent.nodes.route.display_executing_node")
def test_route_generation(mock_display):
    state = get_initial_state("Generate PV curve", message_type="generation")
    result = router(state)
    _assert_route_response(result, "generation", False, "generation")


@patch("agent.nodes.route.display_executing_node")
def test_route_analysis(mock_display):
    state = get_initial_state("Analyze the results", message_type="analysis")
    result = router(state)
    _assert_route_response(result, "analysis", False, "analysis")


@pytest.mark.parametrize(
    "user_message,message_type",
    [
        ("Set power factor to 0.9 then generate PV curve", "parameter"),
        ("Set grid to ieee39 after that generate curve", "parameter"),
        ("Change bus to 10 next generate", "parameter"),
    ],
)
@patch("agent.nodes.route.display_executing_node")
def test_route_compound_detection(mock_display, user_message, message_type):
    state = get_initial_state(user_message, message_type=message_type)
    result = router(state)
    _assert_route_response(result, "planner", True, message_type)


@pytest.mark.parametrize(
    "user_message,message_type",
    [
        ("Set power factor to 0.9 and generate", "parameter"),
        ("Set grid ieee39 and generate", "parameter"),
    ],
)
@patch("agent.nodes.route.display_executing_node")
def test_route_set_and_generate_routes_to_planner(mock_display, user_message, message_type):
    state = get_initial_state(user_message, message_type=message_type)
    result = router(state)
    _assert_route_response(result, "planner", True, message_type)


@pytest.mark.parametrize(
    "user_message,message_type,expected_next",
    [
        ("What's the difference between ieee39 and ieee14?", "question_general", "question_general"),
        ("Compare this and previous pv-curve", "analysis", "analysis"),
        ("Compare current pv-curve and previous pv-curve", "analysis", "analysis"),
    ],
)
@patch("agent.nodes.route.display_executing_node")
def test_route_comparison_stays_single_question(
    mock_display, user_message, message_type, expected_next
):
    """Comparison-only wording (no multi-step keywords, no multiple actions) stays as single question/analysis."""
    state = get_initial_state(user_message, message_type=message_type)
    result = router(state)
    _assert_route_response(result, expected_next, False, message_type)


@pytest.mark.parametrize(
    "user_message,message_type",
    [
        ("Set power factor to 0.9 set bus to 10", "parameter"),
        ("Set grid to ieee39 generate PV curve", "generation"),
    ],
)
@patch("agent.nodes.route.display_executing_node")
def test_route_multiple_actions_no_keywords(mock_display, user_message, message_type):
    state = get_initial_state(user_message, message_type=message_type)
    result = router(state)
    _assert_route_response(result, "planner", True, message_type)


@patch("agent.nodes.route.display_executing_node")
def test_route_default_fallback(mock_display):
    state = get_initial_state("Unknown message type", message_type="unknown_type")
    result = router(state)
    _assert_route_response(result, "question_general", False, "unknown_type")


@patch("agent.nodes.route.display_executing_node")
def test_route_empty_state_messages(mock_display):
    state = {"messages": [], "message_type": "question_general"}
    result = router(state)
    _assert_route_response(result, "question_general", False, "question_general")


@patch("agent.nodes.route.display_executing_node")
def test_route_missing_message_type(mock_display):
    state = {"messages": [HumanMessage(content="Test message")]}
    result = router(state)
    _assert_route_response(result, "question_general", False, "question_general")


@patch("agent.nodes.route.display_executing_node")
def test_route_missing_messages_key(mock_display):
    state = {"message_type": "question_general"}
    result = router(state)
    _assert_route_response(result, "question_general", False, "question_general")


# --------------------------------------------------------------
# Integration Tests (Real State)
# --------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.parametrize(
    "message,message_type,expected_next",
    [
        ("What is a PV curve?", "question_general", "question_general"),
        ("What does power factor mean?", "question_parameter", "question_parameter"),
        ("Set power factor to 0.9", "parameter", "parameter"),
        ("Generate PV curve", "generation", "generation"),
        ("Analyze the results", "analysis", "analysis"),
    ],
)
@patch("agent.nodes.route.display_executing_node")
def test_integration_route_by_message_type(
    mock_display, message, message_type, expected_next
):
    state = get_initial_state(message, message_type=message_type)
    result = router(state)
    assert result["next"] == expected_next, (
        f"Expected next='{expected_next}' for message_type='{message_type}', "
        f"got '{result['next']}'"
    )
    assert result["is_compound"] is False, (
        f"Expected is_compound=False for simple routing, got {result['is_compound']}"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "message,message_type",
    [
        ("Set power factor to 0.9 then generate", "parameter"),
        ("Change bus to 10 after that generate curve", "parameter"),
        ("Set grid ieee39 next generate", "parameter"),
        ("Set power factor 0.9 also generate", "parameter"),
        ("Set bus 10 and then generate", "parameter"),
        ("Set grid ieee39 followed by generate", "parameter"),
        ("Set power factor 0.9 after generate", "parameter"),
        ("Compare set power factor 0.9 and generate", "parameter"),
        ("Set grid ieee39 versus ieee14 and generate", "parameter"),
        ("Set bus 10 vs 20 and generate", "parameter"),
        ("Both set power factor and generate", "parameter"),
        ("Different settings then generate", "parameter"),
        ("Multiple parameters set and generate", "parameter"),
    ],
)
@patch("agent.nodes.route.display_executing_node")
def test_integration_route_compound_requests(mock_display, message, message_type):
    state = get_initial_state(message, message_type=message_type)
    result = router(state)
    assert result["next"] == "planner", (
        f"Expected next='planner' for compound request '{message}', got '{result['next']}'"
    )
    assert result["is_compound"] is True, (
        f"Expected is_compound=True for compound request, got {result['is_compound']}"
    )
