from pathlib import Path
import typer
import json
import re
import platform
import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt
import inquirer
from sage.Core.select_models import select_model
from .terminals import terminals
from .common_ignors import common_ignores

console = Console()

# Define your main color and related colors
MAIN_COLOR = "#8B5CF6" 
ACCENT_COLOR = "#ffffff"        
USER_COLOR = "#1D5ACA"   

def get_terminal_choice():
    questions = [
        inquirer.List(
            'terminal',
            message="Select your terminal/shell",
            choices=terminals,
            carousel=True
        )
    ]
    
    answers = inquirer.prompt(questions)
    os.system('cls' if os.name == 'nt' else 'clear')
    selected_terminal = answers['terminal']
    
    # Clear the inquirer output and show only the selection
    console.print(f"\r[{MAIN_COLOR}]Sage Cli[/]")
    console.print(f"\r[{MAIN_COLOR}]Selected Terminal:[/] [#00c8e2] {selected_terminal}[/]")
    return selected_terminal

def detect_platform():
    """Detect the operating system platform"""
    system = platform.system().lower()
    
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        # Try to detect specific Linux distribution
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content:
                    return 'ubuntu'
                elif 'debian' in content:
                    return 'debian'
                elif 'fedora' in content:
                    return 'fedora'
                elif 'arch' in content:
                    return 'arch'
                else:
                    return 'linux'
        except (FileNotFoundError, Exception):
            return 'linux'
    else:
        return system

def setup_sage(root_path: Path = Path(".")):
    sage_dir = root_path / "Sage"
    interface_file = sage_dir / "interface.json"
    sageignore_file = sage_dir / ".sageignore"
    
    # Check if Sage is already installed
    is_sage_installed = sage_dir.exists() and interface_file.exists() and sageignore_file.exists()
    
    if is_sage_installed:
        choice = typer.prompt(
            "Sage is already installed. Do you want to update your interface? (y/n)", 
            default="y"
        )
        
        if choice.strip().lower() not in ["y", "yes"]:
            console.print(f"[{MAIN_COLOR}]Skipping interface update. Continuing to app...[/]")
            return  # Continue to app instead of exiting
        else:
            console.print(f"[{MAIN_COLOR}]Updating Sage interface...[/]")
    else:
        choice = typer.prompt("Do you want to install Sage? (y/n)", default="y")

        if choice.strip().lower() not in ["y", "yes"]:
            console.print(f"[{ACCENT_COLOR}]Sage setup cancelled. Continuing to app...[/]")
            return  # Continue to app instead of exiting
        else:
            console.print(f"[{MAIN_COLOR}]Setting up Sage...[/]")

    # Ensure .env file exists
    env_file = root_path / ".env"
    env_content = ""
    
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8")
        console.print(f"[{MAIN_COLOR}]Found[/] {env_file}")
    else:
        env_file.touch()
        console.print(f"[{MAIN_COLOR}]Created[/] {env_file}")

    # Check if SAGE_API_KEY exists in .env
    sage_api_key_pattern = r'^\s*SAGE_API_KEY\s*=\s*[^\s#]+'
    has_sage_api_key = re.search(sage_api_key_pattern, env_content, re.MULTILINE)

    if not has_sage_api_key:
        console.print(f"[{ACCENT_COLOR}]SAGE_API_KEY not found in .env file[/]")
        sage_api_key = typer.prompt("Please enter your SAGE_API_KEY (input will be visible)")
        
        if sage_api_key.strip():
            # Add SAGE_API_KEY to .env content
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f"SAGE_API_KEY={sage_api_key}\n"
            
            # Write back to .env file
            with env_file.open("w", encoding="utf-8") as f:
                f.write(env_content)
            
            console.print(f"[{MAIN_COLOR}]SAGE_API_KEY added to .env file[/]")
        else:
            console.print(f"[{ACCENT_COLOR}]No SAGE_API_KEY provided. You'll need to add it manually to .env[/]")
    else:
        console.print(f"[{MAIN_COLOR}]SAGE_API_KEY found in .env file[/]")
    # Check if MODEL exists in .env and handle model selection
    model_pattern = r'^\s*MODEL\s*=\s*[^\s#]+'
    has_model = re.search(model_pattern, env_content, re.MULTILINE)
    
    if not has_model:
        console.print(f"[{ACCENT_COLOR}]MODEL not found in .env file[/]")
        try:
            selected_model = select_model()
            if selected_model:
                # Add MODEL to .env content
                if env_content and not env_content.endswith('\n'):
                    env_content += '\n'
                env_content += f"MODEL={selected_model}\n"
                
                # Write back to .env file
                with env_file.open("w", encoding="utf-8") as f:
                    f.write(env_content)
                
                console.print(f"[{MAIN_COLOR}]MODEL '{selected_model}' added to .env file[/]")
            else:
                console.print(f"[{ACCENT_COLOR}]No model selected. You'll need to add MODEL manually to .env[/]")
        except KeyboardInterrupt:
            console.print(f"\n[{ACCENT_COLOR}]Model selection interrupted[/]")
        except Exception as e:
            console.print(f"[{ACCENT_COLOR}]Error during model selection: {e}[/]")
    else:
        console.print(f"[{MAIN_COLOR}]MODEL found in .env file[/]")

    # Ensure Sage folder exists
    if not sage_dir.exists():
        sage_dir.mkdir()
        console.print(f"[{MAIN_COLOR}]Created[/] {sage_dir}")
    else:
        console.print(f"[{MAIN_COLOR}]Found[/] {sage_dir}")    
    if not sageignore_file.exists():
        with sageignore_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(common_ignores))
        console.print(f"[{MAIN_COLOR}]Created[/] {sageignore_file}")
    else:
        console.print(f"[{MAIN_COLOR}]Found[/] {sageignore_file}")

    # Load ignore patterns
    ignore_patterns = []
    if sageignore_file.exists():
        with sageignore_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
        console.print(f"[{MAIN_COLOR}]Loaded {len(ignore_patterns)} ignore patterns[/]")

    # Collect flattened file structure with relative paths
    def should_ignore(item_path: Path) -> bool:
        # Check if item matches any ignore pattern
        relative_path = item_path.relative_to(root_path)
        for pattern in ignore_patterns:
            pattern = pattern.rstrip('/')
            # Simple pattern matching - you might want to make this more robust
            if str(relative_path).startswith(pattern) or pattern in str(relative_path):
                return True
        return False

    def get_flattened_structure(path: Path, base_path: Path = None):
        if base_path is None:
            base_path = path
        
        flattened = {}
        
        for item in path.iterdir():
            # Skip if item matches ignore patterns
            if should_ignore(item):
                continue
                
            if item.is_dir():
                # Recursively get files from directories
                flattened.update(get_flattened_structure(item, base_path))
            else:
                # Get relative path from base directory
                relative_path = item.relative_to(base_path)
                flattened[str(relative_path).replace('\\', '/')] = "file"
        
        return flattened

    # Scan the parent directory (root_path) and get flattened structure
    flattened_files = get_flattened_structure(root_path)

    # Detect platform and let user select terminal
    detected_platform = detect_platform()
    selected_terminal = get_terminal_choice()
    
    console.print(f"[{MAIN_COLOR}]Detected platform: {detected_platform}[/]")

    # Create the complete interface structure with flattened file paths
    complete_interface = {
        **flattened_files,  # This unpacks all the flattened file paths
        "command": {
            "summary": "",
            "terminal": selected_terminal,
            "platform": detected_platform,
            "commands": [],
        },
        "text": "place holder for your responce",
        "update":"yes/no"
    }

    # Create/update interface.json inside Sage folder
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(complete_interface, f, indent=4, sort_keys=True)

    console.print(f"[{MAIN_COLOR}]{'Updated' if is_sage_installed else 'Created'}[/] {interface_file} with flattened file structure")
    console.print(f"[{MAIN_COLOR}]Recorded {len(flattened_files)} files[/]")
    
    if is_sage_installed:
        console.print(f"[{MAIN_COLOR}]Sage interface updated successfully![/]")
    else:
        console.print(f"[{MAIN_COLOR}]Sage setup complete![/]")