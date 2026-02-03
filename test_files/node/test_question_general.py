import os
from unittest.mock import Mock, patch
import pytest

from langchain_core.messages import HumanMessage
from agent.nodes.question_general import question_general_agent
from agent.core import setup_dependencies


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def get_base_prompts():
    return {
        "question_general_agent": {
            "system": "You are an expert in PV curves. Use this context: {context}",
            "user": "Answer this question: {user_input}",
        }
    }


def get_initial_state(user_message: str, conversation_context=None):
    state = {"messages": [HumanMessage(content=user_message)]}
    if conversation_context is not None:
        state["conversation_context"] = conversation_context
    return state


def create_mock_retriever(context_docs=None):
    if context_docs is None:
        context_docs = [Mock(), Mock(), Mock()]
    retriever = Mock()
    retriever.invoke.return_value = context_docs
    return retriever


def create_mock_llm(response_content: str = "PV curve shows voltage vs load."):
    llm = Mock()
    llm.invoke.return_value = Mock(content=response_content)
    return llm


def _assert_question_general_api_calls_and_response(
    mock_llm,
    mock_retriever,
    prompts,
    user_message,
    result,
    expected_context_len,
    expected_conversation_used,
    expected_exchanges,
    api_response_content,
):
    mock_retriever.invoke.assert_called_once_with(user_message)

    messages = mock_llm.invoke.call_args[0][0]
    assert len(messages) == 2 and messages[0]["role"] == "system" and messages[1]["role"] == "user"
    assert messages[1]["content"] == prompts["question_general_agent"]["user"].format(user_input=user_message)
    assert "Use this context" in messages[0]["content"]

    api_response = mock_llm.invoke.return_value
    data = result["node_response"].data
    assert data["response"] == api_response_content
    assert data["context_retrieved"] == expected_context_len
    assert data["conversation_context_used"] is expected_conversation_used
    assert data["exchanges_included"] == expected_exchanges

    nr = result["node_response"]
    assert nr.node_type == "question_general" and nr.success is True
    assert result["messages"] == [api_response]


# --------------------------------------------------------------
# Unit Tests (Mocked API)
# --------------------------------------------------------------


@patch('agent.nodes.question_general.display_executing_node')
def test_basic_question(mock_display):
    user_message = "What is a PV curve?"
    api_response_content = "A PV curve shows voltage versus load."
    mock_llm = create_mock_llm(api_response_content)
    mock_retriever = create_mock_retriever([Mock(), Mock(), Mock()])
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = question_general_agent(state, mock_llm, prompts, mock_retriever)

    mock_display.assert_called_once_with("question_general")
    _assert_question_general_api_calls_and_response(
        mock_llm,
        mock_retriever,
        prompts,
        user_message,
        result,
        expected_context_len=3,
        expected_conversation_used=False,
        expected_exchanges=0,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_general.display_executing_node')
def test_with_rag_context(mock_display):
    user_message = "Explain load margin."
    context_docs = [Mock(), Mock(), Mock(), Mock()]
    api_response_content = "Load margin is the distance to voltage collapse."
    mock_llm = create_mock_llm(api_response_content)
    mock_retriever = create_mock_retriever(context_docs)
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = question_general_agent(state, mock_llm, prompts, mock_retriever)

    mock_display.assert_called_once_with("question_general")
    _assert_question_general_api_calls_and_response(
        mock_llm,
        mock_retriever,
        prompts,
        user_message,
        result,
        expected_context_len=4,
        expected_conversation_used=False,
        expected_exchanges=0,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_general.display_executing_node')
def test_with_conversation_history(mock_display):
    user_message = "Compare the last two results."
    exchange = {
        "user_input": "Generate for bus 5",
        "assistant_response": "Done.",
        "inputs_state": {"grid": "ieee39", "bus_id": 5, "power_factor": 0.9},
        "results": {"load_margin_mw": 100},
    }
    prompts = get_base_prompts()
    state = get_initial_state(user_message, conversation_context=[exchange])
    api_response_content = "Bus 5 had higher load margin."
    mock_llm = create_mock_llm(api_response_content)
    mock_retriever = create_mock_retriever([])

    result = question_general_agent(state, mock_llm, prompts, mock_retriever)

    mock_display.assert_called_once_with("question_general")
    _assert_question_general_api_calls_and_response(
        mock_llm,
        mock_retriever,
        prompts,
        user_message,
        result,
        expected_context_len=0,
        expected_conversation_used=True,
        expected_exchanges=1,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_general.display_executing_node')
def test_comparison_question(mock_display):
    user_message = "Compare bus 5 and bus 10."
    exchanges = [
        {"user_input": "Generate bus 5", "assistant_response": "OK", "inputs_state": {}, "results": {}},
        {"user_input": "Generate bus 10", "assistant_response": "OK", "inputs_state": {}, "results": {}},
    ]
    prompts = get_base_prompts()
    state = get_initial_state(user_message, conversation_context=exchanges)
    api_response_content = "Bus 10 has a lower nose point voltage."
    mock_llm = create_mock_llm(api_response_content)
    mock_retriever = create_mock_retriever([Mock()])

    result = question_general_agent(state, mock_llm, prompts, mock_retriever)

    mock_display.assert_called_once_with("question_general")
    _assert_question_general_api_calls_and_response(
        mock_llm,
        mock_retriever,
        prompts,
        user_message,
        result,
        expected_context_len=1,
        expected_conversation_used=True,
        expected_exchanges=2,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_general.display_executing_node')
def test_no_context(mock_display):
    user_message = "What is voltage stability?"
    api_response_content = "Voltage stability is..."
    mock_llm = create_mock_llm(api_response_content)
    mock_retriever = create_mock_retriever([])
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    result = question_general_agent(state, mock_llm, prompts, mock_retriever)

    mock_display.assert_called_once_with("question_general")
    _assert_question_general_api_calls_and_response(
        mock_llm,
        mock_retriever,
        prompts,
        user_message,
        result,
        expected_context_len=0,
        expected_conversation_used=False,
        expected_exchanges=0,
        api_response_content=api_response_content,
    )


@patch('agent.nodes.question_general.display_executing_node')
def test_api_failure(mock_display):
    user_message = "What is a nose point?"
    mock_llm = create_mock_llm()
    mock_llm.invoke.side_effect = Exception("API Connection Failed")
    mock_retriever = create_mock_retriever([])
    prompts = get_base_prompts()
    state = get_initial_state(user_message)

    with pytest.raises(Exception, match="API Connection Failed"):
        question_general_agent(state, mock_llm, prompts, mock_retriever)

    mock_retriever.invoke.assert_called_once_with(user_message)


@patch('agent.nodes.question_general.display_executing_node')
def test_empty_state_handling(mock_display):
    mock_llm = create_mock_llm()
    mock_retriever = create_mock_retriever([])
    state = {"messages": []}

    with pytest.raises((IndexError, KeyError)):
        question_general_agent(state, mock_llm, get_base_prompts(), mock_retriever)


@patch('agent.nodes.question_general.display_executing_node')
def test_state_missing_messages_key(mock_display):
    mock_llm = create_mock_llm()
    mock_retriever = create_mock_retriever([])
    state = {}

    with pytest.raises((KeyError, IndexError)):
        question_general_agent(state, mock_llm, get_base_prompts(), mock_retriever)


@patch('agent.nodes.question_general.display_executing_node')
def test_missing_prompts_key(mock_display):
    """Test behavior when prompts dict is missing question_general_agent key."""
    mock_llm = create_mock_llm()
    mock_retriever = create_mock_retriever([])
    prompts = {}
    state = get_initial_state("Test message")

    with pytest.raises((KeyError, AttributeError)):
        question_general_agent(state, mock_llm, prompts, mock_retriever)


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
def integration_llm_prompts_and_retriever():
    """Fixture to set up real LLM, prompts, and retriever for integration tests."""
    if not _has_api_access():
        pytest.skip("No API access (OPENAI_API_KEY or Ollama)")
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"
    llm, prompts, retriever = setup_dependencies(provider)
    return llm, prompts, retriever


@pytest.mark.integration
@pytest.mark.parametrize("message", ["What is a PV curve?", "What is load margin?", "What is a nose point?"])
@patch('agent.nodes.question_general.display_executing_node')
def test_integration_question_general(mock_display, integration_llm_prompts_and_retriever, message):
    """Integration test: verify real API answers general questions with non-empty response."""
    llm, prompts, retriever = integration_llm_prompts_and_retriever
    state = get_initial_state(message)
    result = question_general_agent(state, llm, prompts, retriever)

    response = result["node_response"]
    assert response.success is True
    assert response.node_type == "question_general"
    assert len(response.data["response"]) > 0, f"Expected non-empty response for '{message}'"