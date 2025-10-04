import typer
from rich.console import Console
from sage.Starters.entry import setup_sage

console = Console()

def main():
    console.print("[bold green]Sage CLI[/bold green]")
    console.print("Welcome! Setting up your project now...")
    try:
        setup_sage()
    except typer.Exit:
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    typer.run(main)
