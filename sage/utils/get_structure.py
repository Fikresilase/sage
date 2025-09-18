import json
from pathlib import Path

def get_structure():
    """
    Creates 'sage' folder if missing, ensures JSON files exist,
    and scans the project folder to save the structure in structure.json.
    """
    project_root = Path.cwd()
    sage_folder = project_root / "sage"
    sage_folder.mkdir(exist_ok=True)

    # Create/ensure JSON files
    files = ["structure.json", "summary.json", "systemprompt.json"]
    for file_name in files:
        file_path = sage_folder / file_name
        file_path.touch(exist_ok=True)
        if file_name == "structure.json":
            # Clear existing structure.json
            file_path.write_text(json.dumps({}, indent=2))

    # Recursive function to get folder structure
    def scan_folder(path: Path) -> dict:
        structure = {}
        for item in path.iterdir():
            if item.name == "sage":  # skip Sage folder
                continue
            if item.is_dir():
                structure[item.name] = scan_folder(item)
            else:
                structure[item.name] = None
        return structure

    # Build tree and save
    tree = scan_folder(project_root)
    structure_file = sage_folder / "structure.json"
    structure_file.write_text(json.dumps(tree, indent=2))
    print(f"Project structure saved to {structure_file}")