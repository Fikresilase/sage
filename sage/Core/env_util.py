from pathlib import Path
import typer
from rich.console import Console

console = Console()

def get_api_key():
    """Get API key from .env file."""
    # Check if .env exists and get API key
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[red]x Error: .env file not found[/red]")
        return None
    
    # Load SAGE_API_KEY from .env
    env_content = env_file.read_text(encoding="utf-8")
    api_key = None
    for line in env_content.splitlines():
        if line.startswith("SAGE_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break
    
    if not api_key:
        console.print("[red]x Error: SAGE_API_KEY not found in .env file[/red]")
        return None

    return api_key

def get_model():
    """Get MODEL from .env file."""
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[red]x Error: .env file not found[/red]")
        return None
    
    # Load MODEL from .env
    env_content = env_file.read_text(encoding="utf-8")
    model = None
    for line in env_content.splitlines():
        if line.startswith("MODEL="):
            model = line.split("=", 1)[1].strip()
            break
    
    if not model:
        console.print("[red]x Error: MODEL not found in .env file[/red]")
        return None

    return model