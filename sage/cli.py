# import statments
import os
import json
from pathlib import Path

from sage.utils.get_API_key import get_API_key
from sage.utils.chat import chat
from sage.utils.get_structure import get_structure
def get_folder_structure(path: Path) -> dict:
    structure = {}
    for item in path.iterdir():  # iterate files and subfolders
        if item.is_dir():
            # Recursive call for subfolders
            structure[item.name] = get_folder_structure(item)
        else:
            # File → just mark as None
            structure[item.name] = None
    return structure
def main():
    print("Sage CLI running")

    answer = input("Do you want to proceed? (y/n): ").strip().lower()
    if answer != 'y':
        print("Operation cancelled by the user.")
        return

    # Create 'sage' folder
    project_path = Path.cwd() / "sage"
    project_path.mkdir(parents=True, exist_ok=True)
    print(f"'sage' folder created at: {project_path}")

    # Create necessary files
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

    # Now call setup functions once
    get_structure()  # save project structure to structure.json
    get_API_key()    # prompt user for API key and save to .env
    chat()           # start chat interface