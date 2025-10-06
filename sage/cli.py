import typer
from rich.console import Console
from sage.Starters.entry import setup_sage
from sage.Starters.summerizer import summarize_files

console = Console()
app = typer.Typer()

@app.command()
def main():
    """Sage CLI - Complete project setup and analysis"""
    console.print("[bold green]Sage CLI[/bold green]")
    console.print("Welcome! Setting up and analyzing your project now...")
    try:
        # Setup Sage
        setup_sage()
        # Summarize files
        summarize_files()
    except typer.Exit:
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    app()