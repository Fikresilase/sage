# import statments
import os
from pathlib import Path
def main():
    print("Sage CLI running")
    #Ask the User for permission
    answer = input("Do you want to proceed? (y/n): ").strip().lower()
    if answer == 'y':
        project_path = Path.cwd() / "sage" 
        project_path.mkdir(parents=True, exist_ok=True)
        print(f"'sage' folder created at: {project_path}")
    else:
        print("Operation cancelled by the user.")