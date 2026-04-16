"""
Tests for WebSessionManager state synchronisation.

These tests do NOT require a real LLM.  They verify the invariant that
`WebSessionManager.current_inputs` and `WebSessionManager.session_manager.state["inputs"]`
are always kept in sync via `set_inputs()`.

Background:
  The web layer runs `execute_turn_streaming` in a background thread.
  The event-loop consumer updates `current_inputs` via `set_inputs()`.
  `set_inputs()` must also update `session_manager.state["inputs"]` so the
  *next* LangGraph turn starts with the correct cumulative state — e.g.
  contingency_lines should accumulate, not reset to None on every turn.
"""
from unittest.mock import MagicMock, patch
from agent.schemas.inputs import Inputs
from web.backend.services.agent_service import WebSessionManager


def _make_manager() -> WebSessionManager:
    """Build a WebSessionManager with every heavy dependency mocked out."""
    mock_llm = MagicMock()
    mock_llm._model_name = "mock-model"
    mock_llm.with_structured_output.return_value = mock_llm

    mock_workflow = MagicMock()

    with (
        patch("web.backend.services.agent_service.build_llm", return_value=mock_llm),
        patch("web.backend.services.agent_service.get_settings", return_value=MagicMock(plots_path="/tmp")),
        patch("agent.core.setup_dependencies", return_value=(mock_llm, {}, MagicMock())),
        patch("agent.workflows.workflow.create_workflow", return_value=mock_workflow),
        patch("agent.prompts.get_prompts", return_value={}),
        patch("agent.vector.retriever", return_value=MagicMock()),
        patch("agent.pv_curve.pv_curve.generate_pv_curve", return_value=MagicMock()),
        patch("os.makedirs"),
    ):
        manager = WebSessionManager.__new__(WebSessionManager)
        from agent.session import SessionManager
        manager.session_manager = SessionManager(mock_workflow, "mock", "mock-model")
        manager.current_inputs = Inputs()
        return manager


def test_set_inputs_syncs_both_copies():
    """set_inputs() must keep current_inputs and session_manager.state in sync."""
    manager = _make_manager()

    new_inputs = Inputs(contingency_lines=[(2, 3)])
    manager.set_inputs(new_inputs)

    assert manager.current_inputs.contingency_lines == [(2, 3)]
    assert manager.session_manager.state["inputs"].contingency_lines == [(2, 3)]


def test_cumulative_contingency_lines_via_set_inputs():
    """
    Simulates what execute_streaming does on two consecutive parameter-node updates.

    Turn 1: parameter node sets contingency_lines = [(2, 3)]
    Turn 2: parameter node should see [(2, 3)] in state["inputs"] and
            produce [(2, 3), (3, 4)] — NOT just [(3, 4)].
    """
    manager = _make_manager()

    # --- Simulate what execute_streaming does after turn 1 ---
    inputs_after_turn1 = Inputs(contingency_lines=[(2, 3)])
    manager.set_inputs(inputs_after_turn1)

    # The state the graph reads at the start of turn 2
    state_inputs_for_turn2 = manager.session_manager.state["inputs"]

    assert state_inputs_for_turn2.contingency_lines == [(2, 3)], (
        "session_manager.state['inputs'] was not updated after turn 1; "
        "turn 2 would start with contingency_lines=None and lose the first outage."
    )

    # Simulate turn 2: apply_contingency_lines_update with correct current state
    from agent.utils.common_utils import apply_contingency_lines_update
    result = apply_contingency_lines_update(
        state_inputs_for_turn2.contingency_lines,
        [(3, 4)],
    )
    assert result == [(2, 3), (3, 4)], (
        f"Expected cumulative [(2,3),(3,4)] but got {result}"
    )
