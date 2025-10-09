from pathlib import Path
import typer
import json
import re
import platform
import os
import subprocess
from rich.console import Console

console = Console()

def detect_terminal():
    """Detect the shell/terminal being used, ignoring IDEs"""
    # Get the shell from environment variables
    shell = os.environ.get('SHELL', '')
    
    if shell:
        # Extract shell name from path
        shell_name = os.path.basename(shell).lower()
        if shell_name in ['bash', 'zsh', 'fish', 'sh', 'dash', 'ksh', 'tcsh', 'csh']:
            return shell_name
    
    # Check COMSPEC on Windows for cmd.exe
    if platform.system() == 'Windows':
        comspec = os.environ.get('COMSPEC', '').lower()
        if 'cmd.exe' in comspec:
            return 'cmd.exe'
        
        # Check for PowerShell
        if 'powershell' in comspec or 'pwsh' in comspec:
            return 'powershell'
        
        # Check common PowerShell environment variables
        if 'PSModulePath' in os.environ:
            return 'powershell'
        
        # Try to detect PowerShell by checking parent process (simplified)
        try:
            result = subprocess.run(
                ['cmd', '/c', 'echo %COMSPEC%'],
                capture_output=True, text=True, timeout=2
            )
            if 'powershell' in result.stdout.lower() or 'pwsh' in result.stdout.lower():
                return 'powershell'
            elif 'cmd.exe' in result.stdout.lower():
                return 'cmd.exe'
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
    
    # Fallback: check common shell environment variables
    if 'BASH_VERSION' in os.environ:
        return 'bash'
    elif 'ZSH_VERSION' in os.environ:
        return 'zsh'
    elif 'FISH_VERSION' in os.environ:
        return 'fish'
    
    # Final fallback based on platform
    if platform.system() == 'Windows':
        return 'cmd.exe'  # Default Windows fallback
    else:
        return 'bash'  # Default Unix fallback

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

    # Detect platform and terminal
    detected_platform = detect_platform()
    detected_terminal = detect_terminal()
    
    console.print(f"[cyan]Detected platform: {detected_platform}[/cyan]")
    console.print(f"[cyan]Detected terminal/shell: {detected_terminal}[/cyan]")

    # Create the complete interface structure with flattened file paths
    complete_interface = {
        **flattened_files,  # This unpacks all the flattened file paths
        "command": {
            "summary": "",
            "terminal": detected_terminal,
            "platform": detected_platform,
            "commands": []
        },
        "text": "place holder for your responce"
    }

    # Create/update interface.json inside Sage folder
    with interface_file.open("w", encoding="utf-8") as f:
        json.dump(complete_interface, f, indent=4, sort_keys=True)

    console.print(f"[green]{'Updated' if is_sage_installed else 'Created'}[/green] {interface_file} with flattened file structure")
    console.print(f"[green]Recorded {len(flattened_files)} files[/green]")
    
    if is_sage_installed:
        console.print("[bold green]Sage interface updated successfully![/bold green]")
    else:
        console.print("[bold green]Sage setup complete![/bold green]")