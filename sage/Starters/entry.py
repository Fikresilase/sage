from pathlib import Path
import typer
import json
import re
from rich.console import Console

console = Console()

def setup_sage(root_path: Path = Path(".")):
    sage_dir = root_path / "Sage"
    interface_file = sage_dir / "interface.json"
    sageignore_file = sage_dir / ".sageignore"
    
    # Check if Sage is already installed
    is_sage_installed = sage_dir.exists() and interface_file.exists() and sageignore_file.exists()
    
    if is_sage_installed:
        choice = typer.prompt(
            "Sage is already installed. Do you want to update your interface? (yes/no)", 
            default="no"
        )
        
        if choice.strip().lower() not in ["y", "yes"]:
            console.print("[cyan]Skipping interface update. Continuing to app...[/cyan]")
            return  # Continue to app instead of exiting
        else:
            console.print("[cyan]Updating Sage interface...[/cyan]")
    else:
        choice = typer.prompt("Do you want to install Sage? (yes/no)", default="no")

        if choice.strip().lower() not in ["y", "yes"]:
            console.print("[yellow]Sage setup cancelled. Continuing to app...[/yellow]")
            return  # Continue to app instead of exiting
        else:
            console.print("[cyan]Setting up Sage...[/cyan]")

    # Ensure .env file exists
    env_file = root_path / ".env"
    env_content = ""
    
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8")
        console.print(f"[cyan]Found[/cyan] {env_file}")
    else:
        env_file.touch()
        console.print(f"[green]Created[/green] {env_file}")

    # Check if SAGE_API_KEY exists in .env
    sage_api_key_pattern = r'^\s*SAGE_API_KEY\s*=\s*[^\s#]+'
    has_sage_api_key = re.search(sage_api_key_pattern, env_content, re.MULTILINE)

    if not has_sage_api_key:
        console.print("[yellow]SAGE_API_KEY not found in .env file[/yellow]")
        sage_api_key = typer.prompt("Please enter your SAGE_API_KEY (input will be visible)")
        
        if sage_api_key.strip():
            # Add SAGE_API_KEY to .env content
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f"SAGE_API_KEY={sage_api_key}\n"
            
            # Write back to .env file
            with env_file.open("w", encoding="utf-8") as f:
                f.write(env_content)
            
            console.print("[green]SAGE_API_KEY added to .env file[/green]")
        else:
            console.print("[yellow]No SAGE_API_KEY provided. You'll need to add it manually to .env[/yellow]")
    else:
        console.print("[green]SAGE_API_KEY found in .env file[/green]")

    # Ensure Sage folder exists
    if not sage_dir.exists():
        sage_dir.mkdir()
        console.print(f"[green]Created[/green] {sage_dir}")
    else:
        console.print(f"[cyan]Found[/cyan] {sage_dir}")

    # Create/update .sageignore file in Sage folder with common ignore patterns
    common_ignores = [
        "# Common build and dependency directories",
        "node_modules/",
        "__pycache__/",
        ".pytest_cache/",
        "target/",
        "build/",
        "dist/",
        "bin/",
        "obj/",
        ".git/",
        ".svn/",
        "",
        "# Dependency files",
        "package-lock.json",
        "yarn.lock",
        "Pipfile.lock",
        "poetry.lock",
        "",
        "# Environment and config files",
        ".env",
        ".venv/",
        "venv/",
        "env/",
        ".idea/",
        ".vscode/",
        "",
        "# OS generated files",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Logs and databases",
        "*.log",
        "*.sqlite",
        "*.db",
        "",
        "# Compiled files",
        "*.pyc",
        "*.class",
        "*.so",
        "*.dll",
        "",
        "# Sage specific - don't scan Sage folder itself",
        "Sage/"
    ]
    
    if not sageignore_file.exists():
        with sageignore_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(common_ignores))
        console.print(f"[green]Created[/green] {sageignore_file}")
    else:
        console.print(f"[cyan]Found[/cyan] {sageignore_file}")

    # Load ignore patterns
    ignore_patterns = []
    if sageignore_file.exists():
        with sageignore_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
        console.print(f"[cyan]Loaded {len(ignore_patterns)} ignore patterns[/cyan]")

    # Collect folder structure of the PARENT directory with ignore support
    def should_ignore(item_name: str, item_path: Path) -> bool:
        # Check if item matches any ignore pattern
        for pattern in ignore_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if item_path.is_dir() and item_name == pattern.rstrip('/'):
                    return True
            else:
                # File pattern or exact match
                if item_name == pattern or item_name.endswith(pattern.lstrip('*')):
                    return True
        return False

    def get_structure(path: Path):
        structure = {}
        items = []
        
        # Collect all items first
        for item in path.iterdir():
            items.append(item)
        
        # Sort items alphabetically by name
        items.sort(key=lambda x: x.name.lower())
        
        for item in items:
            item_name = item.name
            
            # Skip if item matches ignore patterns
            if should_ignore(item_name, item):
                continue
                
            if item.is_dir():
                # Recursively get structure for directories
                structure[item_name] = get_structure(item)
            else:
                structure[item_name] = "file"
        
        return structure

    # Scan the parent directory (root_path) instead of sage_dir
    folder_structure = get_structure(root_path)

    # Create/update interface.json inside Sage folder
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(folder_structure, f, indent=4, sort_keys=True)

    console.print(f"[green]{'Updated' if is_sage_installed else 'Created'}[/green] {interface_file} with alphabetically sorted folder structure")
    console.print(f"[green]Recorded {len(folder_structure)} items from parent directory[/green]")
    
    if is_sage_installed:
        console.print("[bold green]Sage interface updated successfully![/bold green]")
    else:
        console.print("[bold green]Sage setup complete![/bold green]")