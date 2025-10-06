from pathlib import Path
import json
import google.generativeai as genai
import typer
from rich.console import Console
import os

console = Console()

def summarize_files(interface_file: Path = Path("Sage/interface.json")):
    """Summarize files in the interface.json using Gemini AI with optimized logic"""
    
    # Check if .env exists and get API key
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[red]Error: .env file not found[/red]")
        return
    
    # Load SAGE_API_KEY from .env
    env_content = env_file.read_text(encoding="utf-8")
    api_key = None
    for line in env_content.splitlines():
        if line.startswith("SAGE_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break
    
    if not api_key:
        console.print("[red]Error: SAGE_API_KEY not found in .env file[/red]")
        return
    
    # Check if interface.json exists
    if not interface_file.exists():
        console.print(f"[red]Error: {interface_file} not found[/red]")
        return
    
    # Ask user if they want to summarize
    choice = typer.prompt("Do you want to summarize your files? (yes/no)", default="no")
    
    if choice.strip().lower() not in ["y", "yes"]:
        console.print("[yellow]Skipping file summarization...[/yellow]")
        
        # Mark all files as "unsummarized"
        with interface_file.open("r", encoding="utf-8") as f:
            interface_data = json.load(f)
        
        mark_files_unsummarized(interface_data)
        
        with interface_file.open("w", encoding="utf-8") as f:
            json.dump(interface_data, f, indent=4)
        
        console.print("[green]Marked all files as 'unsummarized'[/green]")
        return
    
    console.print("[cyan]Starting file summarization with Gemini AI...[/cyan]")
    
    try:
        # Configure Gemini with gemini-2.5-flash
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        console.print("[green]Using model: gemini-2.5-flash[/green]")
            
    except Exception as e:
        console.print(f"[red]Error configuring Gemini: {e}[/red]")
        return
    
    # Load interface data
    with interface_file.open("r", encoding="utf-8") as f:
        interface_data = json.load(f)
    
    console.print("[cyan]Analyzing project structure with Gemini AI...[/cyan]")
    
    # First pass: Provide only interface.json to AI for initial analysis
    initial_summaries = analyze_structure_with_gemini(model, interface_data)
    
    # Check if any files need content review
    files_needing_content = get_files_needing_content(initial_summaries)
    
    # Second pass: Provide content for files that need it
    if files_needing_content:
        console.print(f"[cyan]Providing content for {len(files_needing_content)} files that need review...[/cyan]")
        final_summaries = provide_content_and_reanalyze(model, initial_summaries, files_needing_content)
    else:
        final_summaries = initial_summaries
    
    # Update interface.json with summaries
    update_interface_with_summaries(interface_data, final_summaries)
    
    # Save updated interface.json
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(interface_data, f, indent=4)
    
    console.print("[bold green]File summarization complete![/bold green]")
    console.print(f"[green]Updated interface.json with summaries[/green]")

def analyze_structure_with_gemini(model, interface_data):
    """Analyze the project structure using only interface.json"""
    
    system_prompt = """
    Analyze this project structure and provide summaries for EVERY file in the structure.
    
    For EACH file (including nested files), provide:
    - summary: Brief description of what you think this file does based on its name and location
    - index: Assign a unique number to each file (start from 1)
    - dependents: Guess which other files might depend on this one (provide index numbers not the file names as comma-separated array elements)
    - request: Only fill this if you're very uncertain about the file's purpose. Use "provide" if you need to see the file content.
    
    Return your response as a FLATTENED JSON object where keys are FULL FILE PATHS (including nested paths like "src/App.tsx") 
    and values are objects with the above structure.
    
    IMPORTANT: You MUST include EVERY file in the structure. Do not skip any files.
    Be smart about guessing dependencies based on file names and folder structure.
    Only use "request": "provide" when you genuinely cannot guess the file's purpose.
    """
    
    full_prompt = f"""
    {system_prompt}
    
    Project Structure:
    {json.dumps(interface_data, indent=2)}
    
    Provide your analysis as a FLATTENED JSON where keys are full file paths:
    """
    
    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        summaries = json.loads(json_str)
        console.print(f"[green]✓ Initial structure analysis complete - found {len(summaries)} files[/green]")
        return summaries
        
    except Exception as e:
        console.print(f"[red]Error in structure analysis: {e}[/red]")
        console.print(f"[yellow]Response was: {response_text}[/yellow]")
        return {}

def get_files_needing_content(summaries):
    """Get list of files that need content review"""
    files_needing_content = []
    for file_path, summary_data in summaries.items():
        if summary_data.get("request") == "provide":
            files_needing_content.append(file_path)
    
    console.print(f"[cyan]Found {len(files_needing_content)} files needing content review[/cyan]")
    return files_needing_content

def provide_content_and_reanalyze(model, summaries, files_needing_content):
    """Provide file content for files that need it and get updated summaries"""
    
    # Read content for files that need review
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
    
    # Create prompt for content review
    system_prompt = """
    Review these files that needed additional content and update your summaries.
    For each file, update:
    - summary: Based on the actual file content
    - dependents: Update based on imports, requires, or references found in the content
    - request: Always include this key. never leave it unincluded Leave it as empty string "" unless you're very uncertain about the file's purpose and need to see the content, then use "provide"
    
    Keep the same index numbers as before.
    Return the COMPLETE updated summaries for ALL files (not just the ones reviewed).
    """
    
    full_prompt = f"""
    {system_prompt}
    
    Current Summaries (all files):
    {json.dumps(summaries, indent=2)}
    
    File Contents (only for files needing review):
    {json.dumps(file_contents, indent=2)}
    
    Provide updated COMPLETE summaries as JSON:
    """
    
    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        updated_summaries = json.loads(json_str)
        console.print("[green]✓ Content review complete[/green]")
        return updated_summaries
        
    except Exception as e:
        console.print(f"[red]Error in content review: {e}[/red]")
        return summaries

def mark_files_unsummarized(data):
    """Recursively mark all files as unsummarized"""
    for key, value in data.items():
        if value == "file":
            data[key] = "unsummarized"
        elif isinstance(value, dict):
            mark_files_unsummarized(value)

def update_interface_with_summaries(data, summaries, current_path: Path = Path(".")):
    """Recursively update interface data with file summaries"""
    for key, value in data.items():
        if value == "file":
            # Create the full file path as it would appear in the flattened summaries
            file_key = str(current_path / key).replace("\\", "/")
            
            if file_key in summaries:
                # Ensure request is empty if it was filled
                summary_data = summaries[file_key].copy()
                if summary_data.get("request") == "provide":
                    summary_data["request"] = ""
                data[key] = summary_data
            else:
                # If not found in summaries, check without current path (for root files)
                if key in summaries:
                    summary_data = summaries[key].copy()
                    if summary_data.get("request") == "provide":
                        summary_data["request"] = ""
                    data[key] = summary_data
                else:
                    data[key] = "unsummarized"
        elif isinstance(value, dict):
            update_interface_with_summaries(value, summaries, current_path / key)

if __name__ == "__main__":
    typer.run(summarize_files)