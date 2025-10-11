from pathlib import Path
import json
import typer
from rich.console import Console
from openai import OpenAI
from sage.Starters.env_utils import get_api_key, get_model
from sage.Starters.file_utils import mark_files_unsummarized, update_interface_with_summaries
from sage.Starters.AI_summerize import analyze_and_summarize

console = Console()

# Define your main color and related colors
MAIN_COLOR = "#8B5CF6" 
ACCENT_COLOR = "#ffffff"        
USER_COLOR = "#1D5ACA"   

def summarize_files(interface_file: Path = Path("Sage/interface.json")):
    api_key = get_api_key()
    if not api_key:
        return
    
    # Get model from environment
    model_name = get_model()
    if not model_name:
        console.print("[red]Error: MODEL not found in .env file[/red]")
        return
    
    if not interface_file.exists():
        console.print(f"[red]Error: {interface_file} not found[/red]")
        return
    
    choice = typer.prompt("Do you want to summarize your files? (y/n)", default="y")
    if choice.strip().lower() not in ["y", "yes"]:
        console.print(f"[{ACCENT_COLOR}]Skipping file summarization...[/]")
        with interface_file.open("r", encoding="utf-8") as f:
            interface_data = json.load(f)
        mark_files_unsummarized(interface_data)
        with interface_file.open("w", encoding="utf-8") as f:
            json.dump(interface_data, f, indent=4)
        console.print(f"[{MAIN_COLOR}]Marked all files as 'unsummarized'[/]")
        return
    
    console.print(f"[{MAIN_COLOR}]Starting file summarization with OpenRouter ({model_name})...[/]")
    
    try:
        # Initialize OpenAI client with OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        console.print(f"[{MAIN_COLOR}]Using model: {model_name}[/]")
    except Exception as e:
        console.print(f"[red]Error configuring OpenRouter client: {e}[/red]")
        return
    
    with interface_file.open("r", encoding="utf-8") as f:
        interface_data = json.load(f)
    
    final_summaries = analyze_and_summarize(client, model_name, interface_data)
    update_interface_with_summaries(interface_data, final_summaries)
    
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(interface_data, f, indent=4)
    
    console.print(f"[white]File summarization complete![/]")
    console.print(f"[white]Updated interface.json with summaries[/]")

if __name__ == "__main__":
    typer.run(summarize_files)