from pathlib import Path
import json

def create_sage_folder() -> Path:
    """
    Create 'sage' folder in the current directory if it doesn't exist.
    Returns the Path object of the folder.
    """
    project_path = Path.cwd() / "sage"
    project_path.mkdir(parents=True, exist_ok=True)
    print(f"'sage' folder created at: {project_path}")
    return project_path

def create_necessary_files(project_path: Path):
    """
    Create necessary JSON files inside the 'sage' folder.
    """
    files = ["structure.json", "summary.json", "systemprompt.json"]
    for file_name in files:
        file_path = project_path / file_name
        if not file_path.exists():
            file_path.touch()
            if file_name.endswith(".json"):
                file_path.write_text(json.dumps({}, indent=2))
            print(f"Created {file_name}")
        else:
            print(f"{file_name} already exists")
