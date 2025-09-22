from sage.utils.get_API_key import get_API_key
from sage.utils.chat import chat
from sage.utils.get_structure import get_structure
from sage.utils.setupt_project import create_sage_folder, create_necessary_files

def main():
    print("Sage CLI running")

    answer = input("Do you want to proceed? (y/n): ").strip().lower()
    if answer != 'y':
        print("Operation cancelled by the user.")
        return

    # Setup project folder and files
    project_path = create_sage_folder()
    create_necessary_files(project_path)

    # Call setup functions
    get_structure()  
    get_API_key()   
    chat()           
