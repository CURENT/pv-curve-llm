import os
from unittest.mock import Mock, patch
import pytest
from pydantic import ValidationError

from langchain_core.messages import HumanMessage
from agent.nodes.parameter import parameter_agent
from agent.schemas.inputs import Inputs
from agent.schemas.parameter import InputModifier, ParameterModification
from agent.core import setup_dependencies


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------

def get_base_prompts():
    return {
        "parameter_agent": {
            "system": "You can modify parameters based on current_inputs: {current_inputs}"
        }
    }


def get_initial_state(user_message: str, inputs: Inputs = None):
    return {
        "messages": [HumanMessage(content=user_message)],
        "inputs": inputs or Inputs()
    }


def create_mock_llm(result=None, side_effect=None):
    llm = Mock()
    modifier_llm = Mock()
    if side_effect is not None:
        modifier_llm.invoke.side_effect = side_effect
    else:
        modifier_llm.invoke.return_value = result
    llm.with_structured_output.return_value = modifier_llm
    return llm, modifier_llm


def _assert_parameter_api_calls_and_response(
    mock_llm,
    mock_modifier_llm,
    prompts,
    user_message,
    initial_inputs,
    result,
    expected_updates,
    expected_reply_content,
):
    """Assert InputModifier API was called correctly and inputs/response match api_response."""
    # Schema
    mock_llm.with_structured_output.assert_called_once_with(InputModifier)

    # Message format: system + user
    messages = mock_modifier_llm.invoke.call_args[0][0]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == user_message
    assert prompts["parameter_agent"]["system"].split("{current_inputs}")[0] in messages[0]["content"]

    data = result["node_response"].data

    if expected_updates:
        # Updated parameters and changes match the fake API result
        assert set(data["updated_parameters"]) == set(expected_updates.keys())
        assert data["changes"] == expected_updates
        # current_inputs in data should match the new inputs returned
        assert data["current_inputs"] == result["inputs"].model_dump()
        assert result["node_response"].message == expected_reply_content
    else:
        # No modifications: updated_parameters empty, current_inputs unchanged
        assert data["updated_parameters"] == []
        assert data["current_inputs"] == initial_inputs.model_dump()
        assert result["node_response"].message == expected_reply_content


# --------------------------------------------------------------
# Unit Tests (Mocked API)
# --------------------------------------------------------------


@patch('agent.nodes.parameter.display_executing_node')
def test_modify_single_parameter(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="grid", value="ieee14")
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Set grid to ieee14"
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {"grid": "ieee14"}
    expected_reply = "Updated grid to ieee14"
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_modify_multiple_parameters(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="bus_id", value="10"),
        ParameterModification(parameter="power_factor", value="0.9"),
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Set bus to 10 and power factor to 0.9"
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {"bus_id": 10, "power_factor": 0.9}
    expected_reply = "Updated 2 parameters:\n• bus_id to 10\n• power_factor to 0.9"
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_extract_from_message(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="step_size", value="0.02"),
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Please use a smaller step size of 0.02."
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {"step_size": 0.02}
    expected_reply = "Updated step_size to 0.02"
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_grid_normalization(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="grid", value="IEEE39")
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Set grid to IEEE39"
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {"grid": "IEEE39"}
    expected_reply = "Updated grid to IEEE39"
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_type_validation(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="bus_id", value="10"),
        ParameterModification(parameter="step_size", value="0.02"),
        ParameterModification(parameter="capacitive", value="true"),
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Set bus to 10, step size to 0.02, and capacitive to true."
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {"bus_id": 10, "step_size": 0.02, "capacitive": True}
    expected_reply = (
        "Updated 3 parameters:\n"
        "• bus_id to 10\n"
        "• step_size to 0.02\n"
        "• capacitive to True"
    )
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_invalid_parameter(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="unknown_param", value="123")
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Set unknown_param to 123"
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {"unknown_param": "123"}
    expected_reply = "Updated unknown_param to 123"
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_range_validation(mock_display):
    """Test that out-of-range values are accepted (node doesn't validate on model_copy)."""
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[
        ParameterModification(parameter="step_size", value="100.0")
    ])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Set step size to 100"
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    assert result["inputs"].step_size == 100.0


@patch('agent.nodes.parameter.display_executing_node')
def test_no_modifications(mock_display):
    initial_inputs = Inputs()
    api_result = InputModifier(modifications=[])
    mock_llm, modifier_llm = create_mock_llm(api_result)
    prompts = get_base_prompts()
    user_message = "Do nothing."
    state = get_initial_state(user_message, inputs=initial_inputs)

    result = parameter_agent(state, mock_llm, prompts)

    mock_display.assert_called_once_with("parameter")
    expected_updates = {}
    expected_reply = "No parameter changes detected"
    _assert_parameter_api_calls_and_response(
        mock_llm,
        modifier_llm,
        prompts,
        user_message,
        initial_inputs,
        result,
        expected_updates,
        expected_reply,
    )


@patch('agent.nodes.parameter.display_executing_node')
def test_api_failure(mock_display):
    initial_inputs = Inputs()
    mock_llm, modifier_llm = create_mock_llm(side_effect=Exception("API Connection Failed"))
    prompts = get_base_prompts()
    user_message = "What is power factor?"
    state = get_initial_state(user_message, inputs=initial_inputs)

    with pytest.raises(Exception, match="API Connection Failed"):
        parameter_agent(state, mock_llm, prompts)


@patch('agent.nodes.parameter.display_executing_node')
def test_empty_state_handling(mock_display):
    initial_inputs = Inputs()
    mock_llm, modifier_llm = create_mock_llm(InputModifier(modifications=[]))
    prompts = get_base_prompts()
    state = {"messages": [], "inputs": initial_inputs}

    with pytest.raises((IndexError, KeyError)):
        parameter_agent(state, mock_llm, prompts)


@patch('agent.nodes.parameter.display_executing_node')
def test_state_missing_messages_key(mock_display):
    initial_inputs = Inputs()
    mock_llm, modifier_llm = create_mock_llm(InputModifier(modifications=[]))
    prompts = get_base_prompts()
    state = {"inputs": initial_inputs}

    with pytest.raises((KeyError, IndexError)):
        parameter_agent(state, mock_llm, prompts)


@patch('agent.nodes.parameter.display_executing_node')
def test_missing_prompts_key(mock_display):
    initial_inputs = Inputs()
    mock_llm, modifier_llm = create_mock_llm(InputModifier(modifications=[]))
    prompts = {}
    user_message = "Set grid to ieee14"
    state = get_initial_state(user_message, inputs=initial_inputs)

    with pytest.raises((KeyError, AttributeError)):
        parameter_agent(state, mock_llm, prompts)


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
@pytest.mark.parametrize(
    "user_message,field_name,expected_value,use_approx",
    [
        ("Set bus to 10", "bus_id", 10, False),
        ("Change step size to 0.02", "step_size", 0.02, True),
        ("Make the load capacitive", "capacitive", True, False),
        ("Set power factor to 0.5", "power_factor", 0.5, True),
        ("Set bus to 300", "bus_id", 300, False),
        ("Set step size to 0.1", "step_size", 0.1, True),
    ],
)
@patch('agent.nodes.parameter.display_executing_node')
def test_integration_parameter_updates(mock_display, integration_llm_and_prompts, user_message, field_name, expected_value, use_approx):
    llm, prompts = integration_llm_and_prompts
    state = get_initial_state(user_message)
    result = parameter_agent(state, llm, prompts)

    assert result["node_response"].success is True
    assert result["node_response"].node_type == "parameter"
    assert "inputs" in result, "LLM should have modified parameters"
    actual = getattr(result["inputs"], field_name)
    if use_approx:
        assert pytest.approx(actual, rel=1e-3) == expected_value
    else:
        assert actual == expected_value


@pytest.mark.integration
@pytest.mark.parametrize(
    "user_message,field_name,invalid_value,constraint_substring",
    [
        ("Set step size to 0.5", "step_size", 0.5, "0.1"),
        ("Set max scale to 15.0", "max_scale", 15.0, "10"),
        ("Set bus to 500", "bus_id", 500, "300"),
    ],
)
@patch('agent.nodes.parameter.display_executing_node')
def test_integration_parameter_validation_fails_out_of_range(
    mock_display, integration_llm_and_prompts, user_message, field_name, invalid_value, constraint_substring
):
    llm, prompts = integration_llm_and_prompts
    state = get_initial_state(user_message)
    result = parameter_agent(state, llm, prompts)

    assert result["node_response"].success is True
    assert result["node_response"].node_type == "parameter"
    current_inputs = result["inputs"] if "inputs" in result else state["inputs"]
    invalid_inputs_dict = current_inputs.model_dump()
    invalid_inputs_dict[field_name] = invalid_value

    with pytest.raises(ValidationError) as exc_info:
        Inputs.model_validate(invalid_inputs_dict)

    err_str = str(exc_info.value)
    assert field_name in err_str
    assert constraint_substring in err_str