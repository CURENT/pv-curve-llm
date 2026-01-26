"""State management for MCP server with session-based storage."""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from agent.state.app_state import State
from agent.schemas.inputs import Inputs
from agent.schemas.planner import MultiStepPlan
from agent.utils.common_utils import create_initial_state


class StateManager:
    """Manages session state for MCP tools."""
    
    def __init__(self):
        # In-memory storage: session_id -> state dict
        # Example: {"session_123": {...state...}, "session_456": {...state...}}
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_state(self, session_id: str) -> State:
        """
        Get state for a session, creating it if it doesn't exist.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            State dictionary for this session
        """
        # If session doesn't exist, create a new one with default state
        if session_id not in self._sessions:
            self._sessions[session_id] = create_initial_state()
        
        # Return the state for this session
        return self._sessions[session_id]
    
    def update_state(self, session_id: str, updates: Dict[str, Any]) -> None:
        """
        Update state for a session with new values.
        
        Args:
            session_id: Unique identifier for the session
            updates: Dictionary of state fields to update
        """
        # Get current state (creates if doesn't exist)
        state = self.get_state(session_id)
        
        # Handle messages specially - append instead of replace
        if "messages" in updates:
            # Initialize messages list if it doesn't exist
            if "messages" not in state:
                state["messages"] = []
            
            # Append new messages to existing ones
            # This is important because LangGraph uses message accumulation
            state["messages"].extend(updates["messages"])
            
            # Remove from updates so we don't process it again
            del updates["messages"]
        
        # Update all other fields normally
        # Example: updates = {"message_type": "generation", "inputs": new_inputs}
        # This will set state["message_type"] = "generation" and state["inputs"] = new_inputs
        state.update(updates)
        
        # Save the updated state back
        self._sessions[session_id] = state
    
    def serialize_state(self, state: State) -> Dict[str, Any]:
        """
        Convert State to JSON-serializable dict.
        
        This is needed because:
        - LangChain messages are objects, not JSON
        - Pydantic models need to be converted to dicts
        - JSON can't handle Python objects directly
        
        Args:
            state: The State dictionary to serialize
            
        Returns:
            JSON-serializable dictionary
        """
        serialized = {}
        
        # 1. Serialize messages (LangChain message objects -> dicts)
        serialized["messages"] = []
        for msg in state.get("messages", []):
            if isinstance(msg, BaseMessage):
                # Convert LangChain message to dict
                # Example: HumanMessage("hello") -> {"type": "HumanMessage", "content": "hello"}
                serialized["messages"].append({
                    "type": msg.__class__.__name__,  # "HumanMessage" or "AIMessage"
                    "content": msg.content
                })
            else:
                # Already a dict, keep as is
                serialized["messages"].append(msg)
        
        # 2. Serialize inputs (Pydantic model -> dict)
        if state.get("inputs"):
            if hasattr(state["inputs"], "model_dump"):
                # Pydantic v2 method
                serialized["inputs"] = state["inputs"].model_dump()
            else:
                # Already a dict
                serialized["inputs"] = state["inputs"]
        else:
            serialized["inputs"] = None
        
        # 3. Serialize plan (Pydantic model -> dict)
        if state.get("plan"):
            if hasattr(state["plan"], "model_dump"):
                # MultiStepPlan is a Pydantic model
                serialized["plan"] = state["plan"].model_dump()
            else:
                # Already a dict
                serialized["plan"] = state["plan"]
        else:
            serialized["plan"] = None
        
        # 4. Serialize simple fields (already JSON-compatible)
        serialized["message_type"] = state.get("message_type")
        serialized["results"] = state.get("results")
        serialized["error_info"] = state.get("error_info")
        serialized["current_step"] = state.get("current_step", 0)
        serialized["step_results"] = state.get("step_results", [])
        serialized["is_compound"] = state.get("is_compound", False)
        serialized["retry_count"] = state.get("retry_count", 0)
        serialized["failed_node"] = state.get("failed_node")
        serialized["conversation_context"] = state.get("conversation_context", [])
        
        return serialized
    
    def deserialize_state(self, data: Dict[str, Any]) -> State:
        """
        Convert JSON dict back to State with proper Python objects.
        
        This reverses serialize_state():
        - Converts message dicts back to LangChain message objects
        - Converts input dicts back to Inputs Pydantic model
        - Converts plan dict back to MultiStepPlan Pydantic model
        
        Args:
            data: JSON dictionary (from serialize_state)
            
        Returns:
            State dictionary with proper Python objects
        """
        state = {}
        
        # 1. Deserialize messages (dicts -> LangChain message objects)
        state["messages"] = []
        for msg_data in data.get("messages", []):
            if isinstance(msg_data, dict):
                # Get message type and content
                msg_type = msg_data.get("type", "HumanMessage")
                content = msg_data.get("content", "")
                
                # Create appropriate LangChain message object
                if msg_type == "HumanMessage":
                    state["messages"].append(HumanMessage(content=content))
                elif msg_type == "AIMessage":
                    state["messages"].append(AIMessage(content=content))
                else:
                    # Default to HumanMessage if unknown type
                    state["messages"].append(HumanMessage(content=content))
            else:
                # Already a message object, keep as is
                state["messages"].append(msg_data)
        
        # 2. Deserialize inputs (dict -> Inputs Pydantic model)
        if data.get("inputs"):
            # Create Inputs object from dict
            # Example: {"grid": "ieee39", "bus_id": 5} -> Inputs(grid="ieee39", bus_id=5)
            state["inputs"] = Inputs(**data["inputs"])
        else:
            # Default Inputs if not provided
            state["inputs"] = Inputs()
        
        # 3. Deserialize plan (dict -> MultiStepPlan Pydantic model)
        if data.get("plan"):
            # Convert dict back to MultiStepPlan object
            # Example: {"steps": [...], "description": "..."} -> MultiStepPlan(steps=[...], description="...")
            state["plan"] = MultiStepPlan(**data["plan"])
        else:
            state["plan"] = None
        
        # 4. Deserialize simple fields (already correct types)
        state["message_type"] = data.get("message_type")
        state["results"] = data.get("results")
        state["error_info"] = data.get("error_info")
        state["current_step"] = data.get("current_step", 0)
        state["step_results"] = data.get("step_results", [])
        state["is_compound"] = data.get("is_compound", False)
        state["retry_count"] = data.get("retry_count", 0)
        state["failed_node"] = data.get("failed_node")
        state["conversation_context"] = data.get("conversation_context", [])
        
        return state


# Create a global instance that all tools will use
# This ensures all tools share the same session storage
state_manager = StateManager()