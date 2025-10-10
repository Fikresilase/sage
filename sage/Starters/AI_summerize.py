from pathlib import Path
import json
from rich.console import Console
from .prompts import system_prompt

console = Console()

def analyze_and_summarize(client, model_name, interface_data):
    # Step 1: initial analysis
    summaries = _analyze_structure(client, model_name, interface_data)
    
    # Step 2: check files needing content review
    files_needing_content = _get_files_needing_content(summaries)
    
    if files_needing_content:
        console.print(f"[cyan]Providing content for {len(files_needing_content)} files...[/cyan]")
        summaries = _provide_content_and_reanalyze(client, model_name, summaries, files_needing_content)
    
    return summaries


def _analyze_structure(client, model_name, interface_data):    
    full_prompt = f"{system_prompt}\n\nProject Structure:\n{json.dumps(interface_data, indent=2)}\n\nProvide your analysis as JSON:"
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "Sage CLI",
            },
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert code analyzer. Provide clear, concise summaries of code files."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        response_text = completion.choices[0].message.content.strip()
        json_str = _extract_json(response_text)
        summaries = json.loads(json_str)
        return summaries
    except Exception as e:
        console.print(f"[red]Error in structure analysis: {e}[/red]")
        return {}

def _get_files_needing_content(summaries):
    files = [path for path, data in summaries.items() 
             if isinstance(data, dict) and data.get("request") == "provide"]
    console.print(f"[cyan]Found {len(files)} files needing content review[/cyan]")
    return files

def _provide_content_and_reanalyze(client, model_name, summaries, files_needing_content):
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
    
    content_review_prompt = """
    Review these files that needed additional content and update your summaries.
    Update:
    - summary: Based on actual file content
    - dependents: Update based on imports/references
    - request: Keep empty object {} unless you still need content
    Keep same index numbers. Return COMPLETE updated summaries for ALL files.
    but dont index the command key it not a file but a command exchange interface to run in terminal for later communications.
    """
    
    full_prompt = f"{content_review_prompt}\n\nCurrent Summaries:\n{json.dumps(summaries, indent=2)}\n\nFile Contents:\n{json.dumps(file_contents, indent=2)}\n\nProvide updated COMPLETE summaries as JSON:"
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "Sage CLI",
            },
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert code analyzer. Update file summaries based on actual content."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        response_text = completion.choices[0].message.content.strip()
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