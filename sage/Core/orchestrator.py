import json
from pathlib import Path
from rich.console import Console
from typing import Dict, Any, Optional
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
        
        Args:
            ai_response: Parsed JSON response from AI
            
        Returns:
            str: Response to display to user
        """
        try:
            # Handle text response for display
            user_message = ai_response.get("text", "")
            
            # Handle file operations
            for file_path, file_data in ai_response.items():
                if file_path != "text" and file_path != "command" and isinstance(file_data, dict):
                    request = file_data.get("request", {})
                    
                    if "provide" in request:
                        # Read file content and return to combiner
                        file_content = self._read_file(file_path)
                        return f"File content for {file_path}:\n{file_content}"
                    
                    elif "edit" in request:
                        # Edit file
                        result = self._edit_file(file_path, request["edit"])
                        if result:
                            self._update_interface_file(file_path, file_data)
                            return f"✅ {file_path} edited successfully"
                        else:
                            return f"❌ Failed to edit {file_path}"
                    
                    elif "write" in request:
                        # Write new file
                        result = self._write_file(file_path, request["write"])
                        if result:
                            self._update_interface_file(file_path, file_data)
                            return f"✅ {file_path} created successfully"
                        else:
                            return f"❌ Failed to create {file_path}"
                    
                    elif "delete" in request:
                        # Delete file
                        result = self._delete_file(file_path)
                        if result:
                            self._remove_from_interface(file_path)
                            return f"✅ {file_path} deleted successfully"
                        else:
                            return f"❌ Failed to delete {file_path}"
            
            # Handle command execution
            if "command" in ai_response:
                cmd_data = ai_response["command"]
                commands = cmd_data.get("commands", [])
                if commands:
                    results = []
                    for cmd in commands:
                        result = self._execute_command(cmd)
                        results.append(f"Command: {cmd}\nResult: {result}")
                    return "\n".join(results)
            
            # If no special operations, just return the text
            return user_message
            
        except Exception as e:
            return f"❌ Error in orchestrator: {str(e)}"
    
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
    
    def _update_interface_file(self, file_path: str, file_data: Dict):
        """Update interface.json with new file data."""
        try:
            if self.interface_file.exists():
                with open(self.interface_file, 'r', encoding='utf-8') as f:
                    interface_data = json.load(f)
                
                interface_data[file_path] = file_data
                
                with open(self.interface_file, 'w', encoding='utf-8') as f:
                    json.dump(interface_data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error updating interface file: {e}[/red]")
    
    def _remove_from_interface(self, file_path: str):
        """Remove file from interface.json."""
        try:
            if self.interface_file.exists():
                with open(self.interface_file, 'r', encoding='utf-8') as f:
                    interface_data = json.load(f)
                
                if file_path in interface_data:
                    del interface_data[file_path]
                    
                with open(self.interface_file, 'w', encoding='utf-8') as f:
                    json.dump(interface_data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error removing from interface file: {e}[/red]")