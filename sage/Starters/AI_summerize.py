from pathlib import Path
import json
from rich.console import Console

console = Console()

def analyze_and_summarize(model, interface_data):
    """
    Perform a two-step AI summarization:
    1. Initial structure analysis based on interface_data.
    2. Content review for files that requested 'provide'.
    Returns final summaries for all files.
    """
    # Step 1: initial analysis
    summaries = _analyze_structure(model, interface_data)
    
    # Step 2: check files needing content review
    files_needing_content = _get_files_needing_content(summaries)
    
    if files_needing_content:
        console.print(f"[cyan]Providing content for {len(files_needing_content)} files...[/cyan]")
        summaries = _provide_content_and_reanalyze(model, summaries, files_needing_content)
    
    return summaries


def _analyze_structure(model, interface_data):
    system_prompt = """
    Analyze this project structure and provide summaries for EVERY file in the structure.

    For EACH file (including nested files), provide:
    - summary: Brief description of what you think this file does based on its name and location
    - index: Assign a unique number to each file (start from 1)
    - dependents: Guess which other files might depend on this one (provide index numbers not the file names as comma-separated array elements)
    - request: Only fill this if you're very uncertain about the file's purpose. Use "provide" if you need to see the file content.

    Return your response as a FLATTENED JSON object where keys are FULL FILE PATHS 
    and values are objects with the above structure.

    IMPORTANT: Include EVERY file. Only use "request": "provide" when genuinely uncertain.
    """
    
    full_prompt = f"{system_prompt}\n\nProject Structure:\n{json.dumps(interface_data, indent=2)}\n\nProvide your analysis as JSON:"
    
    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        json_str = _extract_json(response_text)
        summaries = json.loads(json_str)
        console.print(f"[green]✓ Initial structure analysis complete - found {len(summaries)} files[/green]")
        return summaries
    except Exception as e:
        console.print(f"[red]Error in structure analysis: {e}[/red]")
        return {}


def _get_files_needing_content(summaries):
    files = [path for path, data in summaries.items() if data.get("request") == "provide"]
    console.print(f"[cyan]Found {len(files)} files needing content review[/cyan]")
    return files


def _provide_content_and_reanalyze(model, summaries, files_needing_content):
    file_contents = {}
    for file_path in files_needing_content:
        path_obj = Path(file_path)
        if path_obj.exists():
            try:
                content = path_obj.read_text(encoding="utf-8", errors="ignore")
                file_contents[file_path] = content
                console.print(f"[green]✓ Read content for {file_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not read {file_path}: {e}[/yellow]")
                file_contents[file_path] = ""
        else:
            console.print(f"[yellow]⚠ File not found: {file_path}[/yellow]")
            file_contents[file_path] = ""
    
    system_prompt = """
    Review these files that needed additional content and update your summaries.
    Update:
    - summary: Based on actual file content
    - dependents: Update based on imports/references
    - request: Keep empty string "" unless you still need content
    Keep same index numbers. Return COMPLETE updated summaries for ALL files.
    """
    
    full_prompt = f"{system_prompt}\n\nCurrent Summaries:\n{json.dumps(summaries, indent=2)}\n\nFile Contents:\n{json.dumps(file_contents, indent=2)}\n\nProvide updated COMPLETE summaries as JSON:"
    
    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        updated_summaries = json.loads(_extract_json(response_text))
        console.print("[green]✓ Content review complete[/green]")
        return updated_summaries
    except Exception as e:
        console.print(f"[red]Error in content review: {e}[/red]")
        return summaries


def _extract_json(text):
    """Extract JSON from AI response, ignoring markdown fences."""
    if "```json" in text:
        return text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text
