# History-Sensitive Node System

This document describes the history-sensitive functionality added to the LangGraph-based PV Curve Agent, which enables the agent to maintain conversation context and simulation results across interactions.

## Overview

The history-sensitive system consists of several components that work together to make the agent more intelligent and contextually aware:

1. **HistoryContext Class**: Manages historical context extraction and formatting
2. **History-Sensitive Agents**: Enhanced versions of existing agents that consider historical context
3. **State Management**: Extended state models to track conversation history and simulation patterns
4. **Workflow Integration**: New workflow that uses history-aware nodes

## Components

### 1. HistoryContext Class

Located in `history_sensitive_node.py`, this class provides methods to extract and format historical context:

- `extract_conversation_context()`: Extracts recent conversation history
- `extract_simulation_context()`: Extracts previous simulation results
- `extract_parameter_evolution_context()`: Tracks parameter changes over time

### 2. History-Sensitive Agents

#### `history_sensitive_agent()`
Enhanced general question agent that:
- Considers previous conversations
- References past simulation results
- Provides contextually aware responses
- Maintains conversation continuity

#### `history_aware_parameter_agent()`
Enhanced parameter agent that:
- Analyzes parameter usage history
- Suggests parameter combinations based on past results
- Warns about problematic parameter combinations
- Provides informed recommendations

#### `history_aware_generation_agent()`
Enhanced generation agent that:
- Compares current simulation with previous results
- Provides comparative analysis
- Includes historical context in responses

#### `history_aware_analysis_agent()`
Enhanced analysis agent that:
- Performs comparative analysis with previous results
- Identifies trends and patterns
- Suggests next steps based on history

### 3. State Management

Extended state model includes new fields:

```python
class State(TypedDict):
    # ... existing fields ...
    parameter_evolution: List[dict]  # Track parameter changes over time
    simulation_trends: List[dict]    # Track simulation patterns and trends
    user_preferences: Dict[str, Any] # Learn user preferences from history
    context_summary: str             # Current context summary for quick reference
```

### 4. Workflow Integration

The `compound_workflow.py` now provides:
- `create_compound_workflow()`: Unified workflow with optional history-aware features
- `create_hybrid_workflow()`: Hybrid workflow that can switch between modes

## Usage

### Basic Usage

```python
from agent.workflows.compound_workflow import create_compound_workflow

# Create unified workflow with history-aware features
graph = create_compound_workflow(llm, prompts, retriever, generate_pv_curve, use_history=True)

# Use in main agent loop
state = create_initial_state()
new_state = graph.invoke(state, config={"recursion_limit": 50})
```

### Hybrid Mode

```python
from agent.workflows.compound_workflow import create_compound_workflow

# Create unified workflow (can switch between history-aware and regular modes)
graph = create_compound_workflow(llm, prompts, retriever, generate_pv_curve, use_history=True)
```

## Key Features

### 1. Conversation Memory
- Remembers previous questions and answers
- Maintains context across multiple interactions
- References past conversations when relevant

### 2. Simulation History
- Tracks all PV curve simulations performed
- Compares current results with previous ones
- Identifies patterns and trends in results

### 3. Parameter Learning
- Learns from parameter usage patterns
- Suggests parameter combinations based on history
- Warns about parameter combinations that caused issues

### 4. Contextual Responses
- Provides more intelligent responses based on history
- Maintains conversation continuity
- Offers personalized recommendations

## Configuration

### History Limits
```python
history_context = HistoryContext(
    max_conversation_history=10,  # Keep last 10 conversations
    max_simulation_results=5      # Keep last 5 simulation results
)
```

### State Tracking
The system automatically tracks:
- User inputs and assistant responses
- Simulation parameters and results
- Parameter evolution over time
- User preferences and patterns

## Testing

Run the test script to verify functionality:

```bash
python test_history_aware.py
```

This will run a series of test interactions to demonstrate:
1. Basic conversation memory
2. Parameter history tracking
3. Simulation result comparison
4. Contextual awareness

## Benefits

1. **Improved User Experience**: Agent remembers previous interactions and provides more relevant responses
2. **Better Recommendations**: Suggests parameter combinations based on past successful simulations
3. **Contextual Awareness**: References previous conversations and results when appropriate
4. **Learning Capability**: Learns from user preferences and parameter usage patterns
5. **Continuity**: Maintains conversation flow across multiple interactions

## Integration with Existing System

The history-sensitive system is designed to be:
- **Backward Compatible**: Existing workflows continue to work
- **Optional**: Can be enabled/disabled as needed
- **Extensible**: Easy to add new history-aware features
- **Performant**: Minimal overhead when history is not needed

## Future Enhancements

Potential improvements include:
- Machine learning-based preference learning
- Advanced pattern recognition in simulation results
- Predictive parameter suggestions
- User behavior analysis
- Automated report generation based on history
