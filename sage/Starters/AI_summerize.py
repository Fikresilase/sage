from pathlib import Path
import json
from rich.console import Console

console = Console()

def analyze_and_summarize(model, interface_data):
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
    You are given a project directory tree. Produce a single, flattened JSON object and output **only** that JSON object (no extra text, no explanation). Follow these rules exactly.

1. Top-level structure
   - The JSON object's keys are the **full file paths** (relative paths including subfolders) for **every file** in the project. Do NOT include directories as keys. Include hidden files (e.g. `.env`, `.gitignore`) if present.
   - and there are two special keys: `"command"`: describes the project's commands and platform. and text which is reserved for future use. return those two keys always exactly as they are given to you.

2. File value schema (applies to every file key)
   Each file key's value MUST be an object with exactly these four keys (no extra keys):
   - `"summary"`: short plain-language description (one sentence) of what the file likely does, inferred from its name and path.
   - `"index"`: unique integer identifier. Indices MUST start at `1` and increase by `1` for each file. Assign indices deterministically by sorting all file paths in lexicographic (UTF-8) order and numbering in that order.
   - `"dependents"`: an array of integers referencing **index** values of other files in this same JSON that likely depend on or import/use this file. Use indices only, not file names. If none are expected, use an empty array `[]`.
   - `"request"`: must be either the empty object `{}` OR the exact string `"provide"`. Use `"provide"` **only** if you cannot infer the file's purpose or dependencies and therefore need the file contents.
   - when you read a file and provide a summery you are not suppose to read the text inside it and return its summery rather you are suppose to see the program inside it understand what it does and return a summery based on that understanding 
     and if you are not able to understand it or if you think its not a real program return what you exactly think about the summery.

   Additional rules for file entries:
   - Do NOT invent dependencies. If uncertain, leave `"dependents": []` and set `"request": "provide"`.
   - Do not include any other fields besides the four required keys.
   - All strings must use double quotes.

3. `"command"` key schema (exact):
   The `"command"` value MUST be an object with these keys:
   - `"summary"`: one-sentence description of the purpose of the commands.
   - `"terminal"`: a short identifier of shell type (`"powershell"`, `"bash"`, `"cmd"`, etc.). If unknown, prefer `"bash"`.
   - `"platform"`: one of `"windows"`, `"linux"`, `"mac"`, or `""` if unknown.
   - `"commands"`: an array. If you can infer one or more safe, likely-to-run commands, list them as strings. If you cannot infer any commands with confidence, set `"commands": []` (empty array). The `commands` key must always exist.

4. Determinism & validation
   - Indices must be consecutive integers starting at 1 and assigned by lexicographic ordering of file paths.
   - Every value in `"dependents"` must be a valid index that appears somewhere in this JSON. Do not reference the `"command"` key by index.
   - The JSON must be valid, parseable, and use only JSON primitives (objects, arrays, numbers, strings, booleans, null).

5. Output rules
   - Return **only** the JSON object text. No prose, no headings, no extra code fences before or after the JSON.
   - Use double quotes for all JSON strings.
   - Include EVERY file present in the tree. Do not omit files.
   - Use `"request": "provide"` sparingly — only when you truly cannot infer purpose/dependencies from name/path.

6. Examples (for clarity only; do not include these in the final output):
{
  ".env": { "summary":"Environment variables.", "index":1, "dependents":[2,3], "request":{} },
  "package.json": { "summary":"Node project metadata.", "index":2, "dependents":[3], "request":{} },
  "src/index.js": { "summary":"App entry point.", "index":3, "dependents":[], "request":{} },
  "command": {
    "summary":"Project shell commands.",
    "terminal":"powershell",
    "platform":"windows",
    "commands":[]
  }
}
    """
    
    full_prompt = f"{system_prompt}\n\nProject Structure:\n{json.dumps(interface_data, indent=2)}\n\nProvide your analysis as JSON:"
    
    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        json_str = _extract_json(response_text)
        summaries = json.loads(json_str)
        # console.print(f"[green]✓ Initial structure analysis complete - found {len(summaries)} files[/green]")
        # console.print("[blue]--- Full AI response (raw) ---[/blue]")
        # console.print(response.text)
        # console.print("[blue]--- end response ---[/blue]")
        return summaries
    except Exception as e:
        console.print(f"[red]Error in structure analysis: {e}[/red]")
        return {}


def _get_files_needing_content(summaries):
    files = [path for path, data in summaries.items() 
             if isinstance(data, dict) and data.get("request") == "provide"]
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
    - request: Keep empty object {} unless you still need content
    Keep same index numbers. Return COMPLETE updated summaries for ALL files.
    but dont index the command key it not a file but a command exchange interface to run in terminal for later communications.
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
