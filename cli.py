from agent.core import create_graph, setup_dependencies
from agent.session import SessionManager
from agent.utils.display import display_banner, display_parameters, display_divider, display_node_update, console

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
