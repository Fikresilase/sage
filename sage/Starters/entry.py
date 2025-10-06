from pathlib import Path
import typer
import json
from rich.console import Console

console = Console()

def setup_sage(root_path: Path = Path(".")):
    choice = typer.prompt("Do you want to install Sage? (yes/no)", default="no")

    if choice.strip().lower() not in ["y", "yes", "y"]:
        console.print("[yellow]Exiting...[/yellow]")
        raise typer.Exit()

    # Ensure .env file exists
    env_file = root_path / ".env"
    if not env_file.exists():
        env_file.touch()
        console.print(f"[green]Created[/green] {env_file}")
    else:
        console.print(f"[cyan]Found[/cyan] {env_file}")

    # Ensure Sage folder exists
    sage_dir = root_path / "Sage"
    if not sage_dir.exists():
        sage_dir.mkdir()
        console.print(f"[green]Created[/green] {sage_dir}")
    else:
        console.print(f"[cyan]Found[/cyan] {sage_dir}")

    # Create .sageignore file in Sage folder with common ignore patterns
    sageignore_file = sage_dir / ".sageignore"
    if not sageignore_file.exists():
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
        for item in path.iterdir():
            item_name = item.name
            
            # Skip if item matches ignore patterns
            if should_ignore(item_name, item):
                continue
                
            if item.is_dir():
                structure[item_name] = get_structure(item)
            else:
                structure[item_name] = "file"
        return structure

    # Scan the parent directory (root_path) instead of sage_dir
    folder_structure = get_structure(root_path)

    # Create interface.json inside Sage folder
    interface_file = sage_dir / "interface.json"
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(folder_structure, f, indent=4)

    console.print(f"[green]Created[/green] {interface_file} with filtered folder structure")
    console.print(f"[green]Recorded {len(folder_structure)} items from parent directory[/green]")
    console.print("[bold green]Sage setup complete![/bold green]")