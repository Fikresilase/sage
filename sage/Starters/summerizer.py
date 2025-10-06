from pathlib import Path
import json
import google.generativeai as genai
import typer
from rich.console import Console
import os

console = Console()

def summarize_files(interface_file: Path = Path("Sage/interface.json")):
    """Summarize files in the interface.json using Gemini AI"""
    
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
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Load interface data
    with interface_file.open("r", encoding="utf-8") as f:
        interface_data = json.load(f)
    
    # Get all file paths recursively
    file_paths = get_all_file_paths(interface_data, Path("."))
    
    if not file_paths:
        console.print("[yellow]No files found to summarize[/yellow]")
        return
    
    console.print(f"[cyan]Found {len(file_paths)} files to process[/cyan]")
    
    # Process files with Gemini
    processed_files = process_files_with_gemini(model, file_paths, interface_data)
    
    # Update interface.json with summaries
    update_interface_with_summaries(interface_data, processed_files)
    
    # Save updated interface.json
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(interface_data, f, indent=4)
    
    console.print("[bold green]File summarization complete![/bold green]")
    console.print(f"[green]Updated {len(processed_files)} files in interface.json[/green]")

def mark_files_unsummarized(data):
    """Recursively mark all files as unsummarized"""
    for key, value in data.items():
        if value == "file":
            data[key] = "unsummarized"
        elif isinstance(value, dict):
            mark_files_unsummarized(value)

def get_all_file_paths(data, current_path: Path):
    """Recursively get all file paths from interface data"""
    file_paths = []
    
    for key, value in data.items():
        if value == "file":
            file_paths.append(current_path / key)
        elif isinstance(value, dict):
            file_paths.extend(get_all_file_paths(value, current_path / key))
    
    return file_paths

def process_files_with_gemini(model, file_paths, interface_data):
    """Process files with Gemini AI and return summaries"""
    processed_files = {}
    file_index = 1
    
    for file_path in file_paths:
        if not file_path.exists():
            console.print(f"[yellow]Warning: File {file_path} not found, skipping...[/yellow]")
            continue
        
        console.print(f"[cyan]Processing: {file_path}[/cyan]")
        
        try:
            # Read file content
            file_content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Prepare system prompt
            system_prompt = f"""
            Analyze the following file and provide a structured summary.
            
            File: {file_path}
            Content:
            {file_content}
            
            Current interface.json structure (for context):
            {json.dumps(interface_data, indent=2)}
            
            Provide your response as a JSON object with the following structure:
            {{
                "summary": "Brief description of what this file does (2-3 sentences)",
                "index": "{file_index}",
                "dependents": "List of index numbers of files that depend on this file (comma-separated, or empty if none)",
                "request": ""
            }}
            
            Be concise and accurate in your analysis.
            """
            
            # Call Gemini API
            response = model.generate_content(system_prompt)
            
            # Parse response
            try:
                # Try to extract JSON from response
                response_text = response.text.strip()
                if "```json" in response_text:
                    # Extract JSON from code block
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    # Extract from any code block
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text
                
                summary_data = json.loads(json_str)
                
                # Validate required fields
                if all(k in summary_data for k in ["summary", "index", "dependents", "request"]):
                    processed_files[str(file_path)] = summary_data
                    console.print(f"[green]✓ Successfully processed {file_path}[/green]")
                else:
                    console.print(f"[yellow]⚠ Incomplete response for {file_path}, using fallback[/yellow]")
                    processed_files[str(file_path)] = {
                        "summary": "Failed to generate summary",
                        "index": str(file_index),
                        "dependents": "",
                        "request": ""
                    }
                    
            except json.JSONDecodeError:
                console.print(f"[yellow]⚠ Failed to parse JSON response for {file_path}, using fallback[/yellow]")
                processed_files[str(file_path)] = {
                    "summary": "Failed to parse AI response",
                    "index": str(file_index),
                    "dependents": "",
                    "request": ""
                }
            
            file_index += 1
            
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {str(e)}[/red]")
            processed_files[str(file_path)] = {
                "summary": f"Error: {str(e)}",
                "index": str(file_index),
                "dependents": "",
                "request": ""
            }
            file_index += 1
    
    return processed_files

def update_interface_with_summaries(data, processed_files, current_path: Path = Path(".")):
    """Recursively update interface data with file summaries"""
    for key, value in data.items():
        if value == "file":
            file_key = str(current_path / key)
            if file_key in processed_files:
                data[key] = processed_files[file_key]
            else:
                data[key] = "unsummarized"
        elif isinstance(value, dict):
            update_interface_with_summaries(value, processed_files, current_path / key)

if __name__ == "__main__":
    typer.run(summarize_files)