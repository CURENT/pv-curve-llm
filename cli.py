from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.panel import Panel

from agent.core import create_graph, setup_dependencies
from agent.session import SessionManager

console = Console()

# Node name to display name mapping
NODE_DISPLAY_NAMES = {
    "compound_classifier": "Analyzing message complexity",
    "history_detection": "Checking conversation history",
    "classifier": "Classifying message type",
    "enhanced_router": "Routing to appropriate handler",
    "planner": "Planning multi-step execution",
    "step_controller": "Controlling execution steps",
    "advance_step": "Advancing to next step",
    "summary": "Generating summary",
    "question": "Processing question",
    "question_general": "Answering general question",
    "question_parameter": "Answering parameter question",
    "parameter": "Updating parameters",
    "generation": "Generating PV curve",
    "analysis": "Analyzing results",
    "error_handler": "Handling error"
}

def display_banner():
    """Display application banner."""
    console.print("""
[bold green]██████╗░░░░░░░██╗░░░██╗  ░█████╗░██╗░░░██╗██████╗░██╗░░░██╗███████╗[/]
[bold green]██╔══██╗░░░░░░██║░░░██║  ██╔══██╗██║░░░██║██╔══██╗██║░░░██║██╔════╝[/]
[bold green]██████╔╝█████╗╚██╗░██╔╝  ██║░░╚═╝██║░░░██║██████╔╝╚██╗░██╔╝█████╗░░[/]
[bold green]██╔═══╝░╚════╝░╚████╔╝░  ██║░░██╗██║░░░██║██╔══██╗░╚████╔╝░██╔══╝░░[/]
[bold green]██║░░░░░░░░░░░░░╚██╔╝░░  ╚█████╔╝╚██████╔╝██║░░██║░░╚██╔╝░░███████╗[/]
[bold green]╚═╝░░░░░░░░░░░░░░╚═╝░░░  ░╚════╝░░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝[/]

[bold green]░██████╗░███████╗███╗░░██╗███████╗██████╗░░█████╗░████████╗░█████╗░██████╗░[/]
[bold green]██╔════╝░██╔════╝████╗░██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗[/]
[bold green]██║░░██╗░█████╗░░██╔██╗██║█████╗░░██████╔╝███████║░░░██║░░░██║░░██║██████╔╝[/]
[bold green]██║░░╚██╗██╔══╝░░██║╚████║██╔══╝░░██╔══██╗██╔══██║░░░██║░░░██║░░██║██╔══██╗[/]
[bold green]╚██████╔╝███████╗██║░╚███║███████╗██║░░██║██║░░██║░░░██║░░░╚█████╔╝██║░░██║[/]
[bold green]░╚═════╝░╚══════╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝[/]
""")

def display_parameters(inputs):
    """Display current parameters in a formatted table."""
    table = Table(title="Current Parameters", show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="green")
    table.add_column("Value", style="white")

    # Required parameters
    table.add_row("[bold]Required", "", style="grey50")
    table.add_row("Grid system", inputs.grid.upper())
    table.add_row("Bus to monitor voltage", str(inputs.bus_id))

    # Optional parameters
    table.add_row("", "")
    table.add_row("[bold]Optional", "", style="grey50")
    table.add_row("Load increment step size", str(inputs.step_size))
    table.add_row("Maximum load multiplier", str(inputs.max_scale))
    table.add_row("Power factor", str(inputs.power_factor))
    table.add_row("Voltage threshold to stop", f"{inputs.voltage_limit} pu")
    table.add_row("Load type", "Capacitive" if inputs.capacitive else "Inductive")

    console.print(table)

def display_divider():
    """Display a simple divider line."""
    console.print("[grey50]" + "─" * console.width + "[/]")

def display_node_update(node_name: str, state_update: dict):
    """Display a live update from a node execution."""
    display_name = NODE_DISPLAY_NAMES.get(node_name, node_name)
    console.print(f"[grey50]→ {display_name}[/]")

    # If the node returned a message in the state, display it
    if "messages" in state_update and state_update["messages"]:
        last_msg = state_update["messages"][-1]
        if hasattr(last_msg, 'content') and last_msg.content:
            # This is the final response from the agent
            console.print()
            console.print(Markdown(last_msg.content))
            console.print()

    # Display node response if available
    if "node_response" in state_update:
        node_resp = state_update["node_response"]
        if hasattr(node_resp, 'message') and node_resp.message:
            console.print(f"[dim]  {node_resp.message}[/]")

    # Display parameter changes
    if "inputs" in state_update:
        console.print(f"[green]  ✓ Parameters updated[/]")

    # Display results
    if "results" in state_update and state_update["results"]:
        results = state_update["results"]
        if isinstance(results, dict):
            if "plot_path" in results:
                console.print(f"[green]  ✓ PV Curve generated: {results['plot_path']}[/]")
            if "load_margin_mw" in results:
                console.print(f"[green]  Load Margin: {results['load_margin_mw']:.2f} MW[/]")
            if "nose_voltage_pu" in results:
                console.print(f"[green]  Nose Voltage: {results['nose_voltage_pu']:.4f} pu[/]")

def run_cli():
    """Run the CLI interface."""
    display_banner()
    console.print("[bold green]Welcome to the PV Curve Agent![/] Type 'quit' or 'q' to exit.\n")

    provider = console.input("[green]Which model provider would you like to use?[/] ([white]openai[/] or [white]ollama[/]): ").strip().lower()
    if provider not in ["openai", "ollama"]:
        provider = "ollama"

    llm, prompts, retriever = setup_dependencies(provider)
    graph = create_graph(provider)

    console.print(f"\n[green]Using model:[/] [white]{llm._model_name}[/]\n")

    session_manager = SessionManager(graph, provider, llm._model_name)

    while True:
        display_divider()
        display_parameters(session_manager.state["inputs"])
        display_divider()
        console.print("\n[grey50]Ask about any input or ask to change its value![/]")
        console.print("[grey50]Examples: 'What grid systems are available?' or 'Change the grid system to IEEE 118'[/]\n")

        user_input = console.input("[bold green]Message:[/] ")

        if user_input.strip().lower() in ["quit", "q"]:
            console.print("\n[grey50]Saving session...[/]")
            session_manager.save_session()
            console.print("[green]Session saved. Goodbye![/]\n")
            break

        console.print()

        # Stream the execution and display live updates
        try:
            for node_name, state_update in session_manager.execute_turn_streaming(user_input):
                display_node_update(node_name, state_update)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/]")

        console.print()

if __name__ == "__main__":
    run_cli()
