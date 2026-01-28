"""FastMCP Server for PV Curve Agent."""

from fastmcp import FastMCP
from agent.mcp_server import tools

# Create FastMCP server instance
# "pv-curve-agent" is the server name (can be anything)
mcp = FastMCP("pv-curve-agent")


# Register all 11 tools with @mcp.tool() decorators
# Each tool is a thin wrapper that calls the corresponding function in tools.py

@mcp.tool()
def get_session_id() -> dict:
    """
    Get or create a session ID for this conversation.
    Call this ONCE at the start of each new conversation.
    
    IMPORTANT: After calling this, remember the returned session_id and use it
    for all subsequent tool calls in this conversation. Do NOT call this again
    in the same conversation - just reuse the session_id you got.
    
    Returns:
        Dict with session_id to use for all subsequent tool calls
    """
    from datetime import datetime
    import uuid
    
    # Generate unique session_id
    session_id = f"claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Initialize state
    state = tools.state_manager.get_state(session_id)
    
    return {
        "session_id": session_id,
        "message": f"Session ID: {session_id}. Remember this and use it for ALL tool calls in this conversation.",
        "current_parameters": state["inputs"].model_dump() if hasattr(state["inputs"], "model_dump") else {},
        "success": True
    }


@mcp.tool()
def classify_message(user_message: str, session_id: str) -> dict:
    """
    Classify user message into one of: question_general, question_parameter, parameter, generation, analysis.
    
    Args:
        user_message: The user's input message to classify
        session_id: Unique session identifier for this conversation
        
    Returns:
        Dict with message_type and updated state
    """
    return tools.classify_message_tool(user_message, session_id)


@mcp.tool()
def route_request(session_id: str) -> dict:
    """
    Route the current request to the appropriate next tool. 
    Call this after classify_message or after each action step.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dict with next_tool, is_compound, reasoning, and updated state
    """
    return tools.route_request_tool(session_id)


@mcp.tool()
def question_general(user_message: str, session_id: str) -> dict:
    """
    Answer general questions about power systems and PV curves using RAG-enhanced knowledge base.
    
    Args:
        user_message: The user's question about power systems
        session_id: Unique session identifier
        
    Returns:
        Dict with response and updated state
    """
    return tools.question_general_tool(user_message, session_id)


@mcp.tool()
def question_parameter(user_message: str, session_id: str) -> dict:
    """
    Answer questions about input parameters, their ranges, and effects.
    
    Args:
        user_message: Question about parameters
        session_id: Unique session identifier
        
    Returns:
        Dict with response and updated state
    """
    return tools.question_parameter_tool(user_message, session_id)


@mcp.tool()
def modify_parameters(user_message: str, session_id: str) -> dict:
    """
    Modify input parameters (grid, bus_id, power_factor, etc.) based on user request.
    
    Args:
        user_message: User's parameter modification request (e.g., 'Set grid to ieee118')
        session_id: Unique session identifier
        
    Returns:
        Dict with updated parameters and state
    """
    return tools.modify_parameters_tool(user_message, session_id)


@mcp.tool()
def generate_pv_curve(user_message: str, session_id: str) -> dict:
    """
    Generate PV curve with visual plot for the current system configuration.
    
    Args:
        user_message: User's generation request (optional, can include parameters)
        session_id: Unique session identifier
        
    Returns:
        Dict with PV curve results, image file URL, and updated state
    """
    return tools.generate_pv_curve_tool(user_message, session_id)


# @mcp.tool()
# def analyze_pv_curve(user_message: str, session_id: str) -> dict:
#     """
#     Generate analysis of PV curve results without creating a visual plot.
#     Provides detailed analysis of voltage stability, load margin, and system behavior.
    
#     Args:
#         user_message: User's analysis request (optional)
#         session_id: Unique session identifier
        
#     Returns:
#         Dict with analysis results and updated state
#     """
#     return tools.analyze_pv_curve_tool(user_message, session_id)


@mcp.tool()
def plan_steps(user_message: str, session_id: str) -> dict:
    """
    Create a multi-step plan for complex requests (comparisons, multiple actions).
    
    Args:
        user_message: Complex multi-step request
        session_id: Unique session identifier
        
    Returns:
        Dict with plan and updated state
    """
    return tools.plan_steps_tool(user_message, session_id)


@mcp.tool()
def step_controller(session_id: str) -> dict:
    """
    Control execution of the current step in a multi-step plan.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dict with next_tool, current_step, step_info, and updated state
    """
    return tools.step_controller_tool(session_id)


@mcp.tool()
def advance_step(session_id: str) -> dict:
    """
    Advance to the next step in a multi-step plan.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dict with next_tool, current_step, and updated state
    """
    return tools.advance_step_tool(session_id)


@mcp.tool()
def handle_error(session_id: str) -> dict:
    """
    Handle errors and attempt automatic recovery.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dict with error resolution and updated state
    """
    return tools.handle_error_tool(session_id)


@mcp.tool()
def summarize_results(session_id: str) -> dict:
    """
    Summarize results from a completed multi-step workflow.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dict with summary and updated state
    """
    return tools.summarize_results_tool(session_id)


# Entry point: Run the server when this file is executed
if __name__ == "__main__":
    mcp.run()