import os
from unittest.mock import Mock, patch
import pytest

from langchain_core.messages import HumanMessage
from agent.nodes.question_parameter import question_parameter_agent
from agent.core import setup_dependencies


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def get_base_prompts():
    return {
        "question_parameter_agent": {
            "system": "Explain PV curve parameters. ",
        }
    }


def get_initial_state(user_message: str, conversation_context=None):
    state = {"messages": [HumanMessage(content=user_message)]}
    if conversation_context is not None:
        state["conversation_context"] = conversation_context
    return state


def create_mock_llm(response_content: str = "Power factor is the ratio of real to apparent power."):
    llm = Mock()
    llm.invoke.return_value = Mock(content=response_content)
    return llm


def _assert_question_parameter_api_calls_and_response(
    mock_llm,
    prompts,
    user_message,
    result,
    expected_parameter_context_used,
    expected_exchanges,
    api_response_content,
):
    """Assert LLM was called correctly and result matches API response."""
    assert mock_llm.invoke.called
    messages = mock_llm.invoke.call_args[0][0]
    assert len(messages) == 2 and messages[0]["role"] == "system" and messages[1]["role"] == "user"
    assert messages[1]["content"] == user_message
    assert prompts["question_parameter_agent"]["system"] in messages[0]["content"]

    data = result["node_response"].data
    assert data["response"] == api_response_content
    assert data["parameter_context_used"] is expected_parameter_context_used
    assert data["exchanges_included"] == expected_exchanges

    nr = result["node_response"]
    assert nr.node_type == "question_parameter" and nr.success is True
    assert result["messages"] == [mock_llm.invoke.return_value]


# --------------------------------------------------------------
# Unit Tests (Mocked API)
# --------------------------------------------------------------


@patch('agent.nodes.question_parameter.display_executing_node')
def test_explain_parameter(mock_display):
    user_message = "What is power factor?"
    api_response_content = "Power factor is the ratio of real to apparent power."
    mock_llm = create_mock_llm(api_response_content)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = question_parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("question_parameter")
    _assert_question_parameter_api_calls_and_response(
        mock_llm,
        prompts,
        user_message,
        result,
        expected_parameter_context_used=False,
        expected_exchanges=0,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_parameter.display_executing_node')
def test_explain_multiple(mock_display):
    user_message = "What are power factor and step size?"
    api_response_content = "Power factor is... Step size controls..."
    mock_llm = create_mock_llm(api_response_content)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = question_parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("question_parameter")
    _assert_question_parameter_api_calls_and_response(
        mock_llm,
        prompts,
        user_message,
        result,
        expected_parameter_context_used=False,
        expected_exchanges=0,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_parameter.display_executing_node')
def test_with_current_inputs(mock_display):
    user_message = "What does bus_id do?"
    exchange = {
        "user_input": "Set bus to 5",
        "assistant_response": "Done.",
        "inputs_state": {"grid": "ieee39", "bus_id": 5, "power_factor": 0.9},
    }
    prompts = get_base_prompts()
    state = get_initial_state(user_message, conversation_context=[exchange])
    api_response_content = "Bus ID selects the load bus for the PV curve."
    mock_llm = create_mock_llm(api_response_content)

    result = question_parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("question_parameter")
    messages = mock_llm.invoke.call_args[0][0]
    assert "Previous Parameter" in messages[0]["content"]
    _assert_question_parameter_api_calls_and_response(
        mock_llm,
        prompts,
        user_message,
        result,
        expected_parameter_context_used=True,
        expected_exchanges=1,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_parameter.display_executing_node')
def test_context_includes_contingency_and_gen_setpoints(mock_display):
    user_message = "What parameters do we have now?"
    exchange = {
        "user_input": "Set outage and generator voltage",
        "assistant_response": "Done.",
        "inputs_state": {
            "grid": "ieee39",
            "bus_id": 5,
            "power_factor": 0.95,
            "contingency_lines": [(2, 3), (3, 4)],
            "gen_voltage_setpoints": {2: 1.02, 1: 1.05},
        },
    }
    prompts = get_base_prompts()
    state = get_initial_state(user_message, conversation_context=[exchange])
    mock_llm = create_mock_llm("Current parameters listed.")

    question_parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("question_parameter")
    messages = mock_llm.invoke.call_args[0][0]
    system_prompt = messages[0]["content"]
    assert "- Transmission Lines Out: 2-3, 3-4" in system_prompt
    assert "- Generator Voltage Setpoints: 1:1.05, 2:1.02" in system_prompt


@patch('agent.nodes.question_parameter.display_executing_node')
def test_with_history(mock_display):
    user_message = "Compare step size in those runs."
    exchanges = [
        {"user_input": "Set step size 0.01", "inputs_state": {"step_size": 0.01}},
        {"user_input": "Set step size 0.02", "inputs_state": {"step_size": 0.02}},
    ]
    prompts = get_base_prompts()
    state = get_initial_state(user_message, conversation_context=exchanges)
    api_response_content = "First run used 0.01, second used 0.02."
    mock_llm = create_mock_llm(api_response_content)

    result = question_parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("question_parameter")
    _assert_question_parameter_api_calls_and_response(
        mock_llm,
        prompts,
        user_message,
        result,
        expected_parameter_context_used=True,
        expected_exchanges=2,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_parameter.display_executing_node')
def test_invalid_parameter(mock_display):
    user_message = "What is xyz parameter?"
    api_response_content = "I don't have information on that parameter."
    mock_llm = create_mock_llm(api_response_content)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = question_parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("question_parameter")
    _assert_question_parameter_api_calls_and_response(
        mock_llm,
        prompts,
        user_message,
        result,
        expected_parameter_context_used=False,
        expected_exchanges=0,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_parameter.display_executing_node')
def test_api_failure(mock_display):
    user_message = "What is power factor?"
    mock_llm = create_mock_llm()
    mock_llm.invoke.side_effect = Exception("API Connection Failed")
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    with pytest.raises(Exception, match="API Connection Failed"):
        question_parameter_agent(state, mock_llm, prompts)


@patch('agent.nodes.question_parameter.display_executing_node')
def test_empty_state_handling(mock_display):
    mock_llm = create_mock_llm()
    prompts = get_base_prompts()
    state = {"messages": []}

    with pytest.raises((IndexError, KeyError)):
        question_parameter_agent(state, mock_llm, prompts)


@patch('agent.nodes.question_parameter.display_executing_node')
def test_state_missing_messages_key(mock_display):
    mock_llm = create_mock_llm()
    prompts = get_base_prompts()
    state = {}

    with pytest.raises((KeyError, IndexError)):
        question_parameter_agent(state, mock_llm, prompts)


@patch('agent.nodes.question_parameter.display_executing_node')
def test_missing_prompts_key(mock_display):
    mock_llm = create_mock_llm()
    prompts = {}
    state = get_initial_state("What is grid?")

    with pytest.raises((KeyError, AttributeError)):
        question_parameter_agent(state, mock_llm, prompts)


# --------------------------------------------------------------
# Integration Tests (Real API)
# --------------------------------------------------------------


def _has_api_access():
    """Check if API access is available (OPENAI_API_KEY or Ollama)."""
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
    """Fixture to set up real LLM and prompts for integration tests."""
    if not _has_api_access():
        pytest.skip("No API access (OPENAI_API_KEY or Ollama)")
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"
    llm, prompts, _ = setup_dependencies(provider)
    return llm, prompts


@pytest.mark.integration
@pytest.mark.parametrize("message", [
    "What is power factor?",
    "What is step size?",
    "What does bus_id mean?",
])
@patch('agent.nodes.question_parameter.display_executing_node')
def test_integration_question_parameter(mock_display, integration_llm_and_prompts, message):
    llm, prompts = integration_llm_and_prompts
    state = get_initial_state(message)
    result = question_parameter_agent(state, llm, prompts)

    response = result["node_response"]
    assert response.success is True
    assert response.node_type == "question_parameter"
    assert len(response.data["response"]) > 0, f"Expected non-empty response for '{message}'"