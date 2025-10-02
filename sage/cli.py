# sage/cli.py
import typer
from rich.console import Console
# Create a Typer application instance
app = typer.Typer()
# Create a Rich Console instance for beautiful output
console = Console()

@app.command()
def main():
    """
    The main entry point for the Sage CLI.
    """
    console.print("[bold green]Sage - Your CLI Coding Assistant[/bold green]")
    console.print("Welcome! How can I help you today?")

if __name__ == "__main__":
    app()