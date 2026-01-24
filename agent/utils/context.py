from agent.state.app_state import State

def get_conversation_context(state: State, max_exchanges: int = 5):
    conversation_context = state.get("conversation_context", [])
    if conversation_context:
        return conversation_context[-max_exchanges:]
    return []

