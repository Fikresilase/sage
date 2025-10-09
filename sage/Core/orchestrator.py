import json
from pathlib import Path
from rich.console import Console
from typing import Dict, Any
import subprocess
import os

console = Console()

class Orchestrator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.interface_file = Path("Sage/interface.json")
    
    def process_ai_response(self, ai_response: Dict[str, Any]) -> str:
        """
        Process AI response and handle different actions.
        Returns success/error messages that will be sent back to AI for full JSON update.
        """
        try:
            program_results = []
            actions_taken = False
            
            # Handle file operations
            for file_path, file_data in ai_response.items():
                if file_path != "text" and file_path != "command" and isinstance(file_data, dict):
                    request = file_data.get("request", {})
                    
                    if "provide" in request:
                        # Read file content and return to combiner
                        file_content = self._read_file(file_path)
                        program_results.append(f"File content for {file_path}:\n{file_content}")
                        actions_taken = True
                    
                    elif "edit" in request:
                        # Edit file
                        result = self._edit_file(file_path, request["edit"])
                        if result:
                            program_results.append(f"✅ {file_path} edited successfully")
                        else:
                            program_results.append(f"❌ Failed to edit {file_path}")
                        actions_taken = True
                    
                    elif "write" in request:
                        # Write new file
                        result = self._write_file(file_path, request["write"])
                        if result:
                            program_results.append(f"✅ {file_path} created successfully")
                        else:
                            program_results.append(f"❌ Failed to create {file_path}")
                        actions_taken = True
                    
                    elif "delete" in request:
                        # Delete file
                        result = self._delete_file(file_path)
                        if result:
                            program_results.append(f"✅ {file_path} deleted successfully")
                        else:
                            program_results.append(f"❌ Failed to delete {file_path}")
                        actions_taken = True
                    
                    elif "rename" in request:
                        # Rename file
                        result = self._rename_file(file_path, request["rename"])
                        if result:
                            program_results.append(f"✅ {file_path} renamed to {request['rename']} successfully")
                        else:
                            program_results.append(f"❌ Failed to rename {file_path} to {request['rename']}")
                        actions_taken = True
            
            # Handle command execution
            if "command" in ai_response:
                cmd_data = ai_response["command"]
                commands = cmd_data.get("commands", [])
                if commands:
                    for cmd in commands:
                        result = self._execute_command(cmd)
                        program_results.append(f"Command: {cmd}\nResult: {result}")
                    actions_taken = True
            
            # If no actions were taken, just return AI's text response
            if not actions_taken:
                return ai_response.get("text", "")
            
            # Combine results for AI to process
            return "\n".join(program_results)
            
        except Exception as e:
            return f"❌ Error in orchestrator: {str(e)}"
    
    def update_interface_json(self, new_interface_data: Dict[str, Any]):
        """Update the entire interface.json with new data from AI"""
        try:
            # Ensure request objects are empty in the final stored version
            cleaned_data = {}
            for key, value in new_interface_data.items():
                if key in ["text", "command"]:
                    cleaned_data[key] = value
                elif isinstance(value, dict):
                    # Copy the file data but ensure request is empty
                    cleaned_value = value.copy()
                    cleaned_value["request"] = {}
                    cleaned_data[key] = cleaned_value
            
            with open(self.interface_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2)
            
            console.print("[green]✅ Interface JSON updated successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Error updating interface JSON: {e}[/red]")
            return False
    
    def _read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            path = Path(file_path)
            if path.exists():
                return path.read_text(encoding='utf-8')
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _edit_file(self, file_path: str, edit_data: Dict) -> bool:
        """Edit file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            content = path.read_text(encoding='utf-8').splitlines()
            start = edit_data.get("start", 1) - 1  # Convert to 0-based
            end = edit_data.get("end", len(content))
            new_content = edit_data.get("content", [])
            
            # Replace the specified lines
            updated_content = content[:start] + new_content + content[end:]
            
            path.write_text("\n".join(updated_content), encoding='utf-8')
            return True
        except Exception as e:
            console.print(f"[red]Error editing file: {e}[/red]")
            return False
    
    def _write_file(self, file_path: str, content: list) -> bool:
        """Write new file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(content), encoding='utf-8')
            return True
        except Exception as e:
            console.print(f"[red]Error writing file: {e}[/red]")
            return False
    
    def _delete_file(self, file_path: str) -> bool:
        """Delete file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            console.print(f"[red]Error deleting file: {e}[/red]")
            return False
    
    def _rename_file(self, old_path: str, new_name: str) -> bool:
        """Rename/move file to new location."""
        try:
            old_path_obj = Path(old_path)
            
            if not old_path_obj.exists():
                console.print(f"[red]Error: File to rename not found: {old_path}[/red]")
                return False
            
            # Handle different new_name formats:
            # - "userform" -> rename in same directory with same extension
            # - "src/components/ui/userform.tsx" -> full path move
            new_path_obj = Path(new_name)
            
            # If new_name is just a filename without path, use same directory
            if new_path_obj.parent == Path('.'):
                new_path_obj = old_path_obj.parent / new_name
            
            # Ensure the target directory exists
            new_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform the rename/move
            old_path_obj.rename(new_path_obj)
            
            console.print(f"[green]✅ Renamed {old_path} to {new_path_obj}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error renaming file {old_path} to {new_name}: {e}[/red]")
            return False
    
    def _execute_command(self, command: str) -> str:
        """Execute shell command."""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Command execution failed: {str(e)}"