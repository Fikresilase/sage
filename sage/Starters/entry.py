from pathlib import Path
import typer
from rich.console import Console

console = Console()

def setup_sage(root_path: Path = Path(".")):
    """
    Utility function that asks user if they want to install Sage.
    If yes, checks/creates .env file and Sage folder in the given root path.
    """
    choice = typer.prompt("Do you want to install Sage? (yes/no)", default="no")

    if choice.strip().lower() not in ["y", "yes"]:
        console.print("[yellow]Exiting...[/yellow]")
        raise typer.Exit()

    # Ensure .env file exists
    env_file = root_path / ".env"
    if not env_file.exists():
        env_file.touch()
        console.print(f"[green]Created[/green] {env_file}")
    else:
        console.print(f"[cyan]Found[/cyan] {env_file}")

    # Ensure Sage folder exists
    sage_dir = root_path / "Sage"
    if not sage_dir.exists():
        sage_dir.mkdir()
        console.print(f"[green]Created[/green] {sage_dir}")
    else:
        console.print(f"[cyan]Found[/cyan] {sage_dir}")

    console.print("[bold green]Sage setup complete![/bold green]")
