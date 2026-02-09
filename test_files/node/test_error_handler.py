import os
from unittest.mock import Mock, patch
import pytest
from langchain_core.messages import HumanMessage

from agent.nodes.error_handler import error_handler_agent
from agent.nodes import generation as generation_module
from agent.pv_curve.pv_curve import generate_pv_curve
from agent.schemas.inputs import Inputs
from agent.core import setup_dependencies
from agent.utils.common_utils import create_initial_state
from agent.workflows.workflow import create_workflow


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------


def get_base_prompts():
    return {
        "error_handler": {
            "system": "You are an expert error analyst. Explain the error and suggest fixes."
        },
        "error_handler_user": {
            "user": "Analyze this error:\n\n{error_context}"
        },
    }


def get_error_state(error_info, retry_count=0, failed_node="generation", inputs=None):
    return {
        "error_info": error_info,
        "retry_count": retry_count,
        "failed_node": failed_node,
        "inputs": inputs or Inputs(),
    }


def create_mock_llm(explanation_content="The error was due to invalid parameters."):
    llm = Mock()
    reply = Mock(content=explanation_content)
    llm.invoke.return_value = reply
    return llm


def _assert_error_handler_llm_calls_and_response(mock_llm, prompts, error_info, result, expected_message):
    mock_llm.invoke.assert_called_once()
    messages = mock_llm.invoke.call_args[0][0]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert prompts["error_handler"]["system"] == messages[0]["content"]
    assert error_info.get("error_type", "unknown") in messages[1]["content"] or "error" in messages[1]["content"].lower()
    assert result["node_response"].message == expected_message
    assert result["node_response"].node_type == "error_handler"
    assert result["node_response"].success is True
    assert result["retry_count"] == 0
    assert result["failed_node"] is None


# --------------------------------------------------------------
# Unit Tests (Mocked API)
# --------------------------------------------------------------


@patch("agent.nodes.error_handler.display_executing_node")
def test_handle_simulation_error(mock_display):
    state = get_error_state(
        error_info={"error_type": "simulation_error", "error_message": "Power flow did not converge"},
        retry_count=0,
        failed_node="generation",
    )
    mock_llm = create_mock_llm()
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    mock_display.assert_called_once_with("error_handler")
    mock_llm.invoke.assert_not_called()
    assert result["retry_count"] == 1
    assert result["retry_node"] == "generation"
    assert result["error_info"] is None
    assert "inputs" in result


@patch("agent.nodes.error_handler.display_executing_node")
def test_handle_validation_error(mock_display):
    state = get_error_state(
        error_info={"error_type": "validation_error", "error_message": "step_size must be <= 0.1"},
        failed_node="parameter",
    )
    expected_message = "Step size must be between 0 and 0.1."
    mock_llm = create_mock_llm(explanation_content=expected_message)
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    mock_display.assert_called_once_with("error_handler")
    _assert_error_handler_llm_calls_and_response(
        mock_llm, get_base_prompts(), state["error_info"], result, expected_message
    )


@patch("agent.nodes.error_handler.display_executing_node")
def test_auto_correct_grid(mock_display):
    inputs = Inputs(grid="ieee14")
    state = get_error_state(
        error_info={"error_type": "simulation_error", "error_message": "Unsupported grid 39 in the system"},
        inputs=inputs,
    )
    mock_llm = create_mock_llm()
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    mock_llm.invoke.assert_not_called()
    assert result["inputs"].grid == "ieee39"


@patch("agent.nodes.error_handler.display_executing_node")
def test_auto_correct_grid_ieee14(mock_display):
    inputs = Inputs(grid="ieee39")
    state = get_error_state(
        error_info={"error_type": "simulation_error", "error_message": "grid 14 not found"},
        inputs=inputs,
    )
    mock_llm = create_mock_llm()
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    mock_llm.invoke.assert_not_called()
    assert result["inputs"].grid == "ieee14"


@patch("agent.nodes.error_handler.display_executing_node")
def test_auto_correct_bus(mock_display):
    inputs = Inputs()
    state = get_error_state(
        error_info={"error_type": "simulation_error", "error_message": "bus out of range for this network"},
        inputs=inputs,
    )
    mock_llm = create_mock_llm()
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    mock_llm.invoke.assert_not_called()
    assert result["inputs"].bus_id == 0


@patch("agent.nodes.error_handler.display_executing_node")
def test_retry_mechanism(mock_display):
    state = get_error_state(
        error_info={"error_type": "simulation_error", "error_message": "convergence failed"},
        retry_count=0,
        failed_node="generation",
    )
    mock_llm = create_mock_llm()
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    assert result["retry_count"] == 1
    assert result["retry_node"] == "generation"
    mock_llm.invoke.assert_not_called()


@patch("agent.nodes.error_handler.display_executing_node")
def test_max_retries(mock_display):
    state = get_error_state(
        error_info={"error_type": "simulation_error", "error_message": "convergence failed"},
        retry_count=2,
        failed_node="generation",
    )
    expected_message = "Max retries reached; here is what went wrong."
    mock_llm = create_mock_llm(explanation_content=expected_message)
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    mock_llm.invoke.assert_called_once()
    assert result["retry_count"] == 0
    assert result["failed_node"] is None
    assert result["node_response"].message == expected_message


@patch("agent.nodes.error_handler.display_executing_node")
def test_error_explanation(mock_display):
    state = get_error_state(
        error_info={
            "error_type": "validation_error",
            "error_message": "Invalid bus_id",
            "context": "parameter node",
        },
        failed_node="parameter",
    )
    api_reply = "Bus ID must be between 0 and 300 for this grid."
    mock_llm = create_mock_llm(explanation_content=api_reply)
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    _assert_error_handler_llm_calls_and_response(
        mock_llm, get_base_prompts(), state["error_info"], result, api_reply
    )


@patch("agent.nodes.error_handler.display_executing_node")
def test_error_handler_empty_state(mock_display):
    state = {}
    mock_llm = create_mock_llm()
    result = error_handler_agent(state, mock_llm, get_base_prompts())

    assert result["node_response"].node_type == "error_handler"
    assert result["retry_count"] == 0
    assert result["failed_node"] is None
    mock_llm.invoke.assert_called_once()


@patch("agent.nodes.error_handler.display_executing_node")
def test_error_handler_missing_prompts_key(mock_display):
    state = get_error_state(error_info={"error_type": "unknown"}, failed_node="generation")
    mock_llm = create_mock_llm()
    prompts = {}

    with pytest.raises((KeyError, AttributeError)):
        error_handler_agent(state, mock_llm, prompts)


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
        pytest.skip("No API access (OPENAI_API_KEY or Ollama)")
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"
    llm, prompts, retriever = setup_dependencies(provider)
    return llm, prompts, retriever


def _make_generate_pv_curve_that_raises(message="Power flow did not converge"):
    def _raise(*args, **kwargs):
        raise ValueError(message)
    return _raise


def _generation_agent_returns_error_on_failure(state, _llm, _prompts, _retriever, generate_pv_curve_fn):
    try:
        return generation_module.generation_agent(state, _llm, _prompts, _retriever, generate_pv_curve_fn)
    except Exception as e:
        return {
            "error_info": {"error_type": "simulation_error", "error_message": str(e)},
            "failed_node": "generation",
        }


def _parameter_agent_returns_validation_error(state, _llm, _prompts):
    return {
        "error_info": {
            "error_type": "validation_error",
            "error_message": "step_size must be less than or equal to 0.1",
        },
        "failed_node": "parameter",
    }


def _stream_graph_collect_error_handler(graph, state):
    nodes_run = []
    error_handler_update = None
    for chunk in graph.stream(state, stream_mode="updates"):
        for node_name, update in chunk.items():
            nodes_run.append(node_name)
            if node_name == "error_handler":
                error_handler_update = update
    return nodes_run, error_handler_update


@pytest.mark.integration
@patch("agent.nodes.error_handler.display_executing_node")
@patch("agent.workflows.workflow.classify_message")
def test_integration_user_input_to_simulation_error_then_error_handler(
    mock_classify, mock_display, integration_llm_and_prompts
):
    llm, prompts, retriever = integration_llm_and_prompts
    mock_classify.return_value = {"message_type": "generation", "node_response": Mock()}

    state = create_initial_state()
    state["messages"] = [HumanMessage(content="generate pv curve")]

    with patch("agent.workflows.workflow.generation_agent", _generation_agent_returns_error_on_failure):
        graph = create_workflow(llm, prompts, retriever, _make_generate_pv_curve_that_raises())
        nodes_run, error_handler_update = _stream_graph_collect_error_handler(graph, state)

    assert "error_handler" in nodes_run
    assert error_handler_update is not None
    if "retry_node" in error_handler_update:
        assert error_handler_update["retry_node"] == "generation"
    else:
        assert error_handler_update.get("retry_count") == 0 and "messages" in error_handler_update


@pytest.mark.integration
@patch("agent.nodes.error_handler.display_executing_node")
@patch("agent.workflows.workflow.classify_message")
def test_integration_user_input_to_validation_error_then_error_handler(
    mock_classify, mock_display, integration_llm_and_prompts
):
    llm, prompts, retriever = integration_llm_and_prompts
    mock_classify.return_value = {"message_type": "parameter", "node_response": Mock()}

    state = create_initial_state()
    state["messages"] = [HumanMessage(content="set step size to 0.5")]

    with patch("agent.workflows.workflow.parameter_agent", _parameter_agent_returns_validation_error):
        graph = create_workflow(llm, prompts, retriever, generate_pv_curve)
        nodes_run, error_handler_update = _stream_graph_collect_error_handler(graph, state)

    assert "error_handler" in nodes_run
    assert error_handler_update is not None
    assert error_handler_update.get("retry_count") == 0
    assert "messages" in error_handler_update and len(error_handler_update["messages"]) > 0