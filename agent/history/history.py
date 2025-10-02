import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ChatHistoryManager:
    """Manages chat history storage and retrieval using JSON files."""
    
    def __init__(self, history_file: str = "chat_history.json"):
        """
        Initialize the chat history manager.
        
        Args:
            history_file: Path to the JSON file where chat history will be stored
        """
        self.history_file = Path(history_file)
        self.history_data = {
            "sessions": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_sessions": 0
            }
        }
        self._load_history()
    
    def _load_history(self) -> None:
        """Load existing chat history from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load existing history file: {e}")
                self.history_data = {
                    "sessions": [],
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_sessions": 0
                    }
                }
    
    def _save_history(self) -> None:
        """Save current chat history to JSON file."""
        self.history_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        try:
            # Ensure directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def start_new_session(self, session_name: Optional[str] = None) -> str:
        """
        Start a new chat session.
        
        Args:
            session_name: Optional name for the session. If None, generates a timestamp-based name.
            
        Returns:
            Session ID for the new session
        """
        if session_name is None:
            session_name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_id = f"session_{len(self.history_data['sessions']) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        new_session = {
            "session_id": session_id,
            "session_name": session_name,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "messages": [],
            "conversation_history": [],
            "cached_results": [],
            "metadata": {
                "total_messages": 0,
                "total_conversations": 0,
                "total_cached_results": 0
            }
        }
        
        self.history_data["sessions"].append(new_session)
        self.history_data["metadata"]["total_sessions"] = len(self.history_data["sessions"])
        self._save_history()
        
        return session_id
    
    def add_message(self, session_id: str, user_input: str, assistant_response: str, 
                   inputs_used: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message exchange to the chat history.
        
        Args:
            session_id: ID of the session to add the message to
            user_input: User's input message
            assistant_response: Assistant's response
            inputs_used: Optional inputs/parameters used for this exchange
        """
        session = self._get_session(session_id)
        if not session:
            print(f"Warning: Session {session_id} not found")
            return
        
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "assistant_response": assistant_response,
            "inputs_used": inputs_used or {}
        }
        
        session["messages"].append(message_entry)
        session["last_updated"] = datetime.now().isoformat()
        session["metadata"]["total_messages"] = len(session["messages"])
        
        # Also add to conversation_history for backward compatibility
        conversation_entry = {
            "user_input": user_input,
            "assistant_response": assistant_response,
            "inputs_used": inputs_used or {}
        }
        session["conversation_history"].append(conversation_entry)
        session["metadata"]["total_conversations"] = len(session["conversation_history"])
        
        self._save_history()
    
    def add_conversation_history(self, session_id: str, conversation_history: List[Dict[str, Any]]) -> None:
        """
        Add conversation history from the agent state.
        
        Args:
            session_id: ID of the session to add the history to
            conversation_history: List of conversation entries from agent state
        """
        session = self._get_session(session_id)
        if not session:
            print(f"Warning: Session {session_id} not found")
            return
        
        # Add timestamp to each entry if not present
        for entry in conversation_history:
            if "timestamp" not in entry:
                entry["timestamp"] = datetime.now().isoformat()
        
        session["conversation_history"] = conversation_history
        session["last_updated"] = datetime.now().isoformat()
        session["metadata"]["total_conversations"] = len(session["conversation_history"])
        
        self._save_history()
    
    def add_cached_results(self, session_id: str, cached_results: List[Dict[str, Any]]) -> None:
        """
        Add cached results from the agent state.
        
        Args:
            session_id: ID of the session to add the results to
            cached_results: List of cached results from agent state
        """
        session = self._get_session(session_id)
        if not session:
            print(f"Warning: Session {session_id} not found")
            return
        
        # Add timestamp to each entry if not present
        for entry in cached_results:
            if "timestamp" not in entry:
                entry["timestamp"] = datetime.now().isoformat()
        
        session["cached_results"] = cached_results
        session["last_updated"] = datetime.now().isoformat()
        session["metadata"]["total_cached_results"] = len(session["cached_results"])
        
        self._save_history()
    
    def _get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by its ID."""
        for session in self.history_data["sessions"]:
            if session["session_id"] == session_id:
                return session
        return None
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete history for a specific session.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session data or None if not found
        """
        return self._get_session(session_id)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get metadata for all sessions."""
        return [
            {
                "session_id": session["session_id"],
                "session_name": session["session_name"],
                "created_at": session["created_at"],
                "last_updated": session["last_updated"],
                "total_messages": session["metadata"]["total_messages"],
                "total_conversations": session["metadata"]["total_conversations"],
                "total_cached_results": session["metadata"]["total_cached_results"]
            }
            for session in self.history_data["sessions"]
        ]
    
    def get_latest_session(self) -> Optional[Dict[str, Any]]:
        """Get the most recently updated session."""
        if not self.history_data["sessions"]:
            return None
        
        return max(self.history_data["sessions"], 
                  key=lambda x: x["last_updated"])
    
    def export_session(self, session_id: str, export_file: Optional[str] = None) -> str:
        """
        Export a specific session to a separate JSON file.
        
        Args:
            session_id: ID of the session to export
            export_file: Optional custom filename. If None, generates based on session name.
            
        Returns:
            Path to the exported file
        """
        session = self._get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if export_file is None:
            safe_name = "".join(c for c in session["session_name"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            export_file = f"{safe_name}_{session_id}.json"
        
        export_path = Path(export_file)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        return str(export_path)
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all data for a specific session.
        
        Args:
            session_id: ID of the session to clear
            
        Returns:
            True if successful, False if session not found
        """
        session = self._get_session(session_id)
        if not session:
            return False
        
        session["messages"] = []
        session["conversation_history"] = []
        session["cached_results"] = []
        session["last_updated"] = datetime.now().isoformat()
        session["metadata"] = {
            "total_messages": 0,
            "total_conversations": 0,
            "total_cached_results": 0
        }
        
        self._save_history()
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session completely.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if successful, False if session not found
        """
        for i, session in enumerate(self.history_data["sessions"]):
            if session["session_id"] == session_id:
                del self.history_data["sessions"][i]
                self.history_data["metadata"]["total_sessions"] = len(self.history_data["sessions"])
                self._save_history()
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about the chat history."""
        total_messages = sum(session["metadata"]["total_messages"] for session in self.history_data["sessions"])
        total_conversations = sum(session["metadata"]["total_conversations"] for session in self.history_data["sessions"])
        total_cached_results = sum(session["metadata"]["total_cached_results"] for session in self.history_data["sessions"])
        
        return {
            "total_sessions": self.history_data["metadata"]["total_sessions"],
            "total_messages": total_messages,
            "total_conversations": total_conversations,
            "total_cached_results": total_cached_results,
            "created_at": self.history_data["metadata"]["created_at"],
            "last_updated": self.history_data["metadata"]["last_updated"],
            "history_file": str(self.history_file)
        }


# Convenience functions for easy integration
def create_history_manager(history_file: str = "chat_history.json") -> ChatHistoryManager:
    """Create a new ChatHistoryManager instance."""
    return ChatHistoryManager(history_file)


def save_conversation_to_json(conversation_history: List[Dict[str, Any]], 
                            cached_results: List[Dict[str, Any]] = None,
                            session_name: Optional[str] = None,
                            history_file: str = "chat_history.json") -> str:
    """
    Convenience function to save conversation history to JSON.
    
    Args:
        conversation_history: List of conversation entries
        cached_results: Optional list of cached results
        session_name: Optional name for the session
        history_file: Path to the history JSON file
        
    Returns:
        Session ID of the created session
    """
    manager = ChatHistoryManager(history_file)
    session_id = manager.start_new_session(session_name)
    
    if conversation_history:
        manager.add_conversation_history(session_id, conversation_history)
    
    if cached_results:
        manager.add_cached_results(session_id, cached_results)
    
    return session_id


def load_latest_session(history_file: str = "chat_history.json") -> Optional[Dict[str, Any]]:
    """
    Convenience function to load the latest session from JSON.
    
    Args:
        history_file: Path to the history JSON file
        
    Returns:
        Latest session data or None if no sessions exist
    """
    manager = ChatHistoryManager(history_file)
    return manager.get_latest_session()


if __name__ == "__main__":
    # Example usage
    manager = ChatHistoryManager("example_chat_history.json")
    
    # Start a new session
    session_id = manager.start_new_session("Test Session")
    print(f"Created session: {session_id}")
    
    # Add some messages
    manager.add_message(session_id, "Hello", "Hi there! How can I help you?")
    manager.add_message(session_id, "What is a PV curve?", "A PV curve shows the relationship between power and voltage...")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"Statistics: {stats}")
    
    # Export the session
    export_path = manager.export_session(session_id)
    print(f"Exported session to: {export_path}")
