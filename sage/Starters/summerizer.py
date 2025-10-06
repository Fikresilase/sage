from pathlib import Path
import json
import google.generativeai as genai
import typer
from rich.console import Console
from sage.Starters.env_utils import get_api_key
from sage.Starters.file_utils import mark_files_unsummarized, update_interface_with_summaries
from sage.Starters.AI_summerize import analyze_and_summarize

console = Console()

def summarize_files(interface_file: Path = Path("Sage/interface.json")):
    api_key = get_api_key()
    if not api_key:
        return
    
    if not interface_file.exists():
        console.print(f"[red]Error: {interface_file} not found[/red]")
        return
    
    choice = typer.prompt("Do you want to summarize your files? (y/n)", default="n")
    if choice.strip().lower() not in ["y", "yes"]:
        console.print("[yellow]Skipping file summarization...[/yellow]")
        with interface_file.open("r", encoding="utf-8") as f:
            interface_data = json.load(f)
        mark_files_unsummarized(interface_data)
        with interface_file.open("w", encoding="utf-8") as f:
            json.dump(interface_data, f, indent=4)
        console.print("[green]Marked all files as 'unsummarized'[/green]")
        return
    
    console.print("[cyan]Starting file summarization with Gemini AI...[/cyan]")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        console.print("[green]Using model: gemini-2.5-flash[/green]")
    except Exception as e:
        console.print(f"[red]Error configuring Gemini: {e}[/red]")
        return
    
    with interface_file.open("r", encoding="utf-8") as f:
        interface_data = json.load(f)
    
    final_summaries = analyze_and_summarize(model, interface_data)
    update_interface_with_summaries(interface_data, final_summaries)
    
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(interface_data, f, indent=4)
    
    console.print("[bold green]File summarization complete![/bold green]")
    console.print("[green]Updated interface.json with summaries[/green]")

if __name__ == "__main__":
    typer.run(summarize_files)
