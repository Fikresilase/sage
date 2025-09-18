# import statments
import os
import json
from pathlib import Path
from .utils.get_structure import get_structure
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
    #Ask the User for permission
    answer = input("Do you want to proceed? (y/n): ").strip().lower()
    if answer == 'y': #create a folder named 'sage' in the current directory
        project_path = Path.cwd() / "sage" 
        project_path.mkdir(parents=True, exist_ok=True)
        print(f"'sage' folder created at: {project_path}")
        #create files named as structure, summary, and systemprompt in the 'sage' folder
        files = ["structure.json", "summary.json", "systemprompt.json"]
        for file_name in files:
            file_path = project_path / file_name
            if not file_path.exists():
                file_path.touch()
                # Optionally, write empty JSON object
                file_path.write_text(json.dumps({}, indent=2))
                print(f"Created {file_name}")
                get_structure()
                
            else:
                print(f"{file_name} already exists")
    else: #if the user enters 'n', exit the program
        print("Operation cancelled by the user.")