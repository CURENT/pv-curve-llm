import os
from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from langchain_core.messages import HumanMessage
from agent.nodes.classify import classify_message
from agent.schemas.classifier import MessageClassifier
from agent.schemas.response import NodeResponse
from agent.core import setup_dependencies

# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------

def create_mock_llm(message_type: str = "question_general", side_effect=None):
    """Create a mock LLM that returns a MessageClassifier object."""
    mock_llm = Mock()
    structured_llm = Mock()
    
    if side_effect:
        structured_llm.invoke.side_effect = side_effect
    else:
        structured_llm.invoke.return_value = MessageClassifier(message_type=message_type)
    
    mock_llm.with_structured_output.return_value = structured_llm
    return mock_llm


def get_base_prompts():
    """Get base prompts dictionary."""
    return {
        "classifier": {
            "system": "Classify the user message into one of five categories..."
        }
    }


def get_initial_state(user_message: str):
    """Create initial state with user message."""
    return {
        "messages": [HumanMessage(content=user_message)]
    }


def _assert_classify_api_calls_and_response(mock_llm, prompts, user_message, result):

    mock_llm.with_structured_output.assert_called_once_with(MessageClassifier)
    
    structured_llm = mock_llm.with_structured_output.return_value
    assert structured_llm.invoke.called, "invoke should be called"
    
    call_args = structured_llm.invoke.call_args[0][0]
    assert isinstance(call_args, list), "invoke should receive a list of messages"
    assert len(call_args) == 2, "Should have exactly 2 messages (system + user)"
    assert call_args[0]["role"] == "system", "First message should be system"
    assert call_args[0]["content"] == prompts["classifier"]["system"], "System prompt should match"
    assert call_args[1]["role"] == "user", "Second message should be user"
    assert call_args[1]["content"] == user_message, "User message should match input"
    
    api_response = structured_llm.invoke.return_value
    assert result["node_response"].data["message_type"] == api_response.message_type, \
        "Should extract message_type from API response"
    assert result["message_type"] == api_response.message_type, \
        "Should return extracted message_type"
    
    node_response = result["node_response"]
    assert isinstance(node_response, NodeResponse), "Should create NodeResponse object"
    assert node_response.node_type == "classifier", "Should set correct node_type"
    assert node_response.success is True, "Should set success=True"
    assert isinstance(node_response.timestamp, datetime), "Should include timestamp"
    assert api_response.message_type in node_response.message, \
        "Message should contain the classification from API response"


# --------------------------------------------------------------
# Unit Tests (Mocked API)
# --------------------------------------------------------------

@patch('agent.nodes.classify.display_executing_node')
def test_classify_general_question(mock_display):
    """Test that API is called with correct parameters and response is handled correctly."""
    mock_llm = create_mock_llm(message_type="question_general")
    prompts = get_base_prompts()
    user_message = "What is pv curve?"
    state = get_initial_state(user_message)
    
    result = classify_message(state, mock_llm, prompts)
    
    _assert_classify_api_calls_and_response(mock_llm, prompts, user_message, result)


@patch('agent.nodes.classify.display_executing_node')
def test_classify_parameter_request(mock_display):
    """Test that API is called with correct parameters and response is handled correctly."""
    mock_llm = create_mock_llm(message_type="parameter")
    prompts = get_base_prompts()
    user_message = "Set power factor to 0.9"
    state = get_initial_state(user_message)
    
    result = classify_message(state, mock_llm, prompts)
    
    _assert_classify_api_calls_and_response(mock_llm, prompts, user_message, result)


@patch('agent.nodes.classify.display_executing_node')
def test_classify_generation_request(mock_display):
    """Test that API is called with correct parameters and response is handled correctly."""
    mock_llm = create_mock_llm(message_type="generation")
    prompts = get_base_prompts()
    user_message = "Generate pv curve"
    state = get_initial_state(user_message)
    
    result = classify_message(state, mock_llm, prompts)
    
    _assert_classify_api_calls_and_response(mock_llm, prompts, user_message, result)


@patch('agent.nodes.classify.display_executing_node')
def test_classify_question_parameter(mock_display):
    """Test that API is called with correct parameters and response is handled correctly."""
    mock_llm = create_mock_llm(message_type="question_parameter")
    prompts = get_base_prompts()
    user_message = "What does power factor mean?"
    state = get_initial_state(user_message)
    
    result = classify_message(state, mock_llm, prompts)
    
    _assert_classify_api_calls_and_response(mock_llm, prompts, user_message, result)


@patch('agent.nodes.classify.display_executing_node')
def test_classify_analysis(mock_display):
    """Test that API is called with correct parameters and response is handled correctly."""
    mock_llm = create_mock_llm(message_type="analysis")
    prompts = get_base_prompts()
    user_message = "Analyze the results"
    state = get_initial_state(user_message)
    
    result = classify_message(state, mock_llm, prompts)
    
    _assert_classify_api_calls_and_response(mock_llm, prompts, user_message, result)


@patch('agent.nodes.classify.display_executing_node')
def test_api_failure_handling(mock_display):
    """Test that API exceptions are propagated correctly."""
    mock_llm = create_mock_llm(side_effect=Exception("API Connection Failed"))
    prompts = get_base_prompts()
    state = get_initial_state("This should fail")
    
    with pytest.raises(Exception, match="API Connection Failed"):
        classify_message(state, mock_llm, prompts)
    
    mock_llm.with_structured_output.assert_called_once_with(MessageClassifier)


@patch('agent.nodes.classify.display_executing_node')
def test_empty_state_handling(mock_display):
    """Test behavior when no messages exist in state."""
    mock_llm = create_mock_llm()
    prompts = get_base_prompts()
    state = {"messages": []}
    
    with pytest.raises((IndexError, KeyError)):
        classify_message(state, mock_llm, prompts)


@patch('agent.nodes.classify.display_executing_node')
def test_missing_prompts_key(mock_display):
    """Test behavior when prompts dictionary is missing 'classifier' key."""
    mock_llm = create_mock_llm()
    prompts = {}
    state = get_initial_state("Test message")
    
    with pytest.raises((KeyError, AttributeError)):
        classify_message(state, mock_llm, prompts)


@patch('agent.nodes.classify.display_executing_node')
def test_state_missing_messages_key(mock_display):
    """Test behavior when state dictionary is missing 'messages' key."""
    mock_llm = create_mock_llm()
    prompts = get_base_prompts()
    state = {}
    
    with pytest.raises((KeyError, IndexError)):
        classify_message(state, mock_llm, prompts)


# --------------------------------------------------------------
# Integration Tests (Real API)
# --------------------------------------------------------------

def _has_api_access():
    """Check if API access is available."""
    if os.getenv("OPENAI_API_KEY"):
        return True
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


@pytest.fixture
def integration_llm_and_prompts():
    """Fixture to set up real LLM and prompts for integration tests."""
    if not _has_api_access():
        pytest.skip("No API access available (requires OPENAI_API_KEY or running Ollama)")
    
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"
    llm, prompts, _ = setup_dependencies(provider)
    return llm, prompts


@pytest.mark.integration
@pytest.mark.parametrize("message", [
    "What is a PV curve?",
    "Explain voltage stability"
])
@patch('agent.nodes.classify.display_executing_node')
def test_integration_classify_question_general(mock_display, integration_llm_and_prompts, message):
    """Integration test: Verify real API classifies general questions correctly."""
    llm, prompts = integration_llm_and_prompts
    
    state = get_initial_state(message)
    result = classify_message(state, llm, prompts)
    
    response = result["node_response"]
    assert response.success is True
    assert response.data["message_type"] == "question_general", \
        f"Expected 'question_general' for '{message}', got '{response.data['message_type']}'"


@pytest.mark.integration
@pytest.mark.parametrize("message", [
    "Set grid to ieee39",
    "Change bus to 10",
    "Set power factor to 0.9",
    "Update voltage limit to 0.5"
])
@patch('agent.nodes.classify.display_executing_node')
def test_integration_classify_parameter(mock_display, integration_llm_and_prompts, message):
    """Integration test: Verify real API classifies parameter modification requests correctly."""
    llm, prompts = integration_llm_and_prompts
    
    state = get_initial_state(message)
    result = classify_message(state, llm, prompts)
    
    response = result["node_response"]
    assert response.success is True
    assert response.data["message_type"] == "parameter", \
        f"Expected 'parameter' for '{message}', got '{response.data['message_type']}'"


@pytest.mark.integration
@pytest.mark.parametrize("message", [
    "Generate PV curve",
    "Create a PV curve",
    "Generate PV curve for ieee39",
    "Plot the voltage stability curve"
])
@patch('agent.nodes.classify.display_executing_node')
def test_integration_classify_generation(mock_display, integration_llm_and_prompts, message):
    """Integration test: Verify real API classifies generation requests correctly."""
    llm, prompts = integration_llm_and_prompts
    
    state = get_initial_state(message)
    result = classify_message(state, llm, prompts)
    
    response = result["node_response"]
    assert response.success is True
    assert response.data["message_type"] == "generation", \
        f"Expected 'generation' for '{message}', got '{response.data['message_type']}'"


@pytest.mark.integration
@pytest.mark.parametrize("message", [
    "What does power factor mean?",
    "What is the bus ID?",
    "What grid systems are available?",
    "How does power factor work?",
    "What is a reasonable step size?",
    "What is the difference between inductive and capacitive load?"
])
@patch('agent.nodes.classify.display_executing_node')
def test_integration_classify_question_parameter(mock_display, integration_llm_and_prompts, message):
    """Integration test: Verify real API classifies parameter questions correctly."""
    llm, prompts = integration_llm_and_prompts
    
    state = get_initial_state(message)
    result = classify_message(state, llm, prompts)
    
    response = result["node_response"]
    assert response.success is True
    assert response.data["message_type"] == "question_parameter", \
        f"Expected 'question_parameter' for '{message}', got '{response.data['message_type']}'"


@pytest.mark.integration
@pytest.mark.parametrize("message", [
    "Analyze the results",
    "What does this PV curve tell us?",
    "Analyze the voltage stability",
    "Interpret the load margin"
])
@patch('agent.nodes.classify.display_executing_node')
def test_integration_classify_analysis(mock_display, integration_llm_and_prompts, message):
    """Integration test: Verify real API classifies analysis requests correctly."""
    llm, prompts = integration_llm_and_prompts
    
    state = get_initial_state(message)
    result = classify_message(state, llm, prompts)
    
    response = result["node_response"]
    assert response.success is True
    assert response.data["message_type"] == "analysis", \
        f"Expected 'analysis' for '{message}', got '{response.data['message_type']}'"