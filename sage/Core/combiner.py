import json
from pathlib import Path
from rich.console import Console

from .gemini_client import send_to_gemini

console = Console()

# System prompt for the AI
SYSTEM_PROMPT = """
You are Sage, a senior developer in the terminal which has a full context of the project assist with with coding task with your agentic capabilities.

You have access to the project structure through the interface.json file, which contains:
- File paths and their summaries
- File dependencies, what files import or reference that specific file,function or variable from that file(which files are dependent on it) 
- Project commands and platform information

-- always return your answer with a text and the updated json structure of the project, if you change a file or an import statement update the json structure accordingly.

- only interfere with  code when you are asked to write or modify code.if the user asks how can i do something,explain the steps in detail, maybe write code but do not modify any code unless asked to do so.

- to modify a file or add a new file, or delete a file include the text that you want in the request field "edit","delete" or "create" and update the json structure accordingly.





Be helpful, concise, and Always reference the actual project structure.
"""

def get_ai_response(user_prompt: str, api_key: str) -> str:
    """
    Combine user prompt with system prompt and interface data, then send to AI.
    
    Args:
        user_prompt: User's input message
        api_key: API key for Gemini
        
    Returns:
        str: AI response text
    """
    try:
        # Load interface data
        interface_data = _load_interface_data()
        if not interface_data:
            return "❌ Error: Could not load project interface data. Please run setup first."
        
        # Combine everything into the final prompt
        combined_prompt = f"""
{_format_interface_context(interface_data)}

User Question: {user_prompt}

Please provide a helpful response based on the project structure and the user's question.
"""
        
        # Send to Gemini
        response = send_to_gemini(
            api_key=api_key,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=combined_prompt
        )
        
        return response
        
    except Exception as e:
        console.print(f"[red]❌ Error in combiner: {e}[/red]")
        return f"Error: {str(e)}"

def _load_interface_data():
    """Load interface.json data from Sage folder."""
    interface_file = Path("Sage/interface.json")
    if not interface_file.exists():
        console.print("[red]❌ interface.json not found. Please run setup first.[/red]")
        return None
    
    try:
        with open(interface_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Error loading interface.json: {e}[/red]")
        return None

def _format_interface_context(interface_data: dict) -> str:
    """Format interface data for the AI prompt."""
    if not interface_data:
        return "No project structure data available."
    
    # Format the interface data nicely
    context_parts = ["📁 Project Structure Analysis:"]
    
    # Add files information
    file_count = 0
    for key, value in interface_data.items():
        if key != "command" and isinstance(value, dict):
            file_count += 1
            summary = value.get('summary', 'No summary available')
            context_parts.append(f"  - {key}: {summary}")
    
    context_parts.append(f"\nTotal files analyzed: {file_count}")
    
    # Add command information if available
    if "command" in interface_data:
        cmd_data = interface_data["command"]
        context_parts.append(f"\n🚀 Project Commands:")
        context_parts.append(f"  - Platform: {cmd_data.get('platform', 'Unknown')}")
        context_parts.append(f"  - Terminal: {cmd_data.get('terminal', 'Unknown')}")
        if cmd_data.get('commands'):
            context_parts.append("  - Available commands:")
            for cmd in cmd_data['commands']:
                context_parts.append(f"    • {cmd}")
    
    return "\n".join(context_parts)