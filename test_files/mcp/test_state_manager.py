from langchain_core.messages import HumanMessage, AIMessage

from agent.mcp_server.state_manager import StateManager
from agent.utils.common_utils import create_initial_state
from agent.schemas.inputs import Inputs
from agent.schemas.planner import MultiStepPlan, StepType


def _base_serialized_data():
    return {
        "messages": [],
        "inputs": {"grid": "ieee39", "bus_id": 5},
        "plan": None,
        "message_type": None,
        "results": None,
        "error_info": None,
        "current_step": 0,
        "step_results": [],
        "is_compound": False,
        "retry_count": 0,
        "failed_node": None,
        "conversation_context": [],
    }


# --------------------------------------------------------------
# Unit Tests
# --------------------------------------------------------------


def test_get_new_session():
    manager = StateManager()
    state = manager.get_state("new_session")
    expected = create_initial_state()
    assert state.keys() == expected.keys()
    assert state["messages"] == []
    assert state["current_step"] == 0
    assert isinstance(state["inputs"], Inputs)
    assert state["plan"] is None


def test_get_existing_session():
    manager = StateManager()
    state1 = manager.get_state("s1")
    state2 = manager.get_state("s1")
    assert state1 is state2
    manager.update_state("s1", {"message_type": "generation"})
    state3 = manager.get_state("s1")
    assert state3["message_type"] == "generation"


def test_update_state():
    manager = StateManager()
    manager.get_state("s1")
    manager.update_state("s1", {"message_type": "generation", "current_step": 2})
    state = manager.get_state("s1")
    assert state["message_type"] == "generation"
    assert state["current_step"] == 2


def test_update_messages():
    manager = StateManager()
    manager.get_state("s1")
    manager.update_state("s1", {"messages": [HumanMessage(content="hello")]})
    manager.update_state("s1", {"messages": [AIMessage(content="hi back")]})
    state = manager.get_state("s1")
    assert len(state["messages"]) == 2
    assert state["messages"][0].content == "hello"
    assert state["messages"][1].content == "hi back"


def test_serialize_state():
    manager = StateManager()
    state = create_initial_state()
    state["messages"] = [HumanMessage(content="x"), AIMessage(content="y")]
    data = manager.serialize_state(state)
    assert isinstance(data, dict)
    assert data["messages"] == [{"type": "HumanMessage", "content": "x"}, {"type": "AIMessage", "content": "y"}]
    assert isinstance(data["inputs"], dict)
    assert "grid" in data["inputs"]
    assert data.get("plan") is None


def test_deserialize_state():
    manager = StateManager()
    data = _base_serialized_data()
    data["messages"] = [{"type": "HumanMessage", "content": "a"}, {"type": "AIMessage", "content": "b"}]
    data["message_type"] = "generation"
    state = manager.deserialize_state(data)
    assert len(state["messages"]) == 2
    assert state["messages"][0].content == "a"
    assert state["messages"][1].content == "b"
    assert isinstance(state["inputs"], Inputs)
    assert state["inputs"].grid == "ieee39"
    assert state["plan"] is None
    assert state["message_type"] == "generation"


def test_serialize_pydantic_models():
    manager = StateManager()
    state = create_initial_state()
    state["inputs"] = Inputs(grid="ieee14", bus_id=3)
    state["plan"] = MultiStepPlan(description="Two steps", steps=[StepType(action="parameter", content="set grid")])
    data = manager.serialize_state(state)
    assert data["inputs"]["grid"] == "ieee14"
    assert data["inputs"]["bus_id"] == 3
    assert data["plan"]["description"] == "Two steps"
    assert len(data["plan"]["steps"]) == 1
    assert data["plan"]["steps"][0]["action"] == "parameter"


def test_deserialize_pydantic_models():
    manager = StateManager()
    data = _base_serialized_data()
    data["inputs"] = {"grid": "ieee14", "bus_id": 3}
    data["plan"] = {"description": "Two steps", "steps": [{"action": "parameter", "content": "set grid"}]}
    state = manager.deserialize_state(data)
    assert isinstance(state["inputs"], Inputs)
    assert state["inputs"].grid == "ieee14"
    assert state["inputs"].bus_id == 3
    assert isinstance(state["plan"], MultiStepPlan)
    assert state["plan"].description == "Two steps"
    assert len(state["plan"].steps) == 1
    assert state["plan"].steps[0].action == "parameter"


def test_deserialize_missing_keys():
    manager = StateManager()
    data = {}
    state = manager.deserialize_state(data)
    assert state["messages"] == []
    assert isinstance(state["inputs"], Inputs)
    assert state["plan"] is None
    assert state["message_type"] is None
    assert state["current_step"] == 0
    assert state["step_results"] == []
    assert state["is_compound"] is False
    assert state["retry_count"] == 0


def test_multiple_sessions():
    manager = StateManager()
    manager.update_state("session_a", {"message_type": "generation"})
    manager.update_state("session_b", {"message_type": "parameter"})
    assert manager.get_state("session_a")["message_type"] == "generation"
    assert manager.get_state("session_b")["message_type"] == "parameter"


def test_serialize_deserialize_round_trip():
    manager = StateManager()
    state = create_initial_state()
    state["messages"] = [HumanMessage(content="hello"), AIMessage(content="world")]
    state["inputs"] = Inputs(grid="ieee14", bus_id=1)
    state["message_type"] = "generation"
    state["current_step"] = 1
    data = manager.serialize_state(state)
    restored = manager.deserialize_state(data)
    assert len(restored["messages"]) == 2
    assert restored["messages"][0].content == "hello"
    assert restored["messages"][1].content == "world"
    assert restored["inputs"].grid == "ieee14"
    assert restored["inputs"].bus_id == 1
    assert restored["message_type"] == "generation"
    assert restored["current_step"] == 1