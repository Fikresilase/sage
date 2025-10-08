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
        
        Args:
            ai_response: Parsed JSON response from AI
            
        Returns:
            str: Response to display to user (AI's text + program results)
        """
        try:
            # Store AI's text response
            ai_text = ai_response.get("text", "")
            program_results = []
            
            # Handle file operations
            for file_path, file_data in ai_response.items():
                if file_path != "text" and file_path != "command" and isinstance(file_data, dict):
                    request = file_data.get("request", {})
                    
                    if "provide" in request:
                        # Read file content and return to combiner
                        file_content = self._read_file(file_path)
                        program_results.append(f"File content for {file_path}:\n{file_content}")
                    
                    elif "edit" in request:
                        # Edit file
                        result = self._edit_file(file_path, request["edit"])
                        if result:
                            self._update_interface_file(file_path, file_data)
                            program_results.append(f"✅ {file_path} edited successfully")
                        else:
                            program_results.append(f"❌ Failed to edit {file_path}")
                    
                    elif "write" in request:
                        # Write new file
                        result = self._write_file(file_path, request["write"])
                        if result:
                            self._update_interface_file(file_path, file_data)
                            program_results.append(f"✅ {file_path} created successfully")
                        else:
                            program_results.append(f"❌ Failed to create {file_path}")
                    
                    elif "delete" in request:
                        # Delete file
                        result = self._delete_file(file_path)
                        if result:
                            self._remove_from_interface(file_path)
                            program_results.append(f"✅ {file_path} deleted successfully")
                        else:
                            program_results.append(f"❌ Failed to delete {file_path}")
            
            # Handle command execution
            if "command" in ai_response:
                cmd_data = ai_response["command"]
                commands = cmd_data.get("commands", [])
                if commands:
                    for cmd in commands:
                        result = self._execute_command(cmd)
                        program_results.append(f"Command: {cmd}\nResult: {result}")
            
            # Update interface for summary/dependents changes from full JSON
            for file_path, file_data in ai_response.items():
                if file_path not in ["text", "command"] and isinstance(file_data, dict):
                    if self._has_interface_changes(file_path, file_data):
                        self._update_interface_file(file_path, file_data)
            
            # Combine AI text with program results
            final_response = ai_text
            if program_results:
                final_response += "\n\n" + "\n".join(program_results)
            
            return final_response
            
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
    
    def _has_interface_changes(self, file_path: str, new_data: Dict) -> bool:
        """Check if summary or dependents actually changed."""
        if not self.interface_file.exists():
            return True
        
        try:
            with open(self.interface_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # Convert flat path to tree and check if file exists in tree
            flat_key = file_path.replace('/', '_')
            if file_path not in current_data:
                # Check if file exists in tree structure
                tree_path = self._find_in_tree(current_data, file_path.split('/'))
                if tree_path is None:
                    return True  # New file
                else:
                    current = tree_path
            else:
                current = current_data[file_path]
            
            return (current.get("summary") != new_data.get("summary") or
                    current.get("dependents") != new_data.get("dependents"))
        except:
            return True
    
    def _find_in_tree(self, tree: Dict, path_parts: list) -> Dict:
        """Find a file in the tree structure."""
        current = tree
        for part in path_parts:
            if part in current:
                current = current[part]
            else:
                return None
        return current
    
    def _flat_to_tree(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert flat file paths to tree structure."""
        tree = {}
        
        for key, value in flat_data.items():
            if key in ["text", "command"]:
                tree[key] = value
                continue
                
            # Split path into parts
            parts = key.split('/')
            current_level = tree
            
            # Navigate/create the tree structure
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # Last part - this is the file
                    current_level[part] = value
                else:
                    # Directory level
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
        
        return tree
    
    def _merge_trees(self, target: Dict, source: Dict):
        """Recursively merge source tree into target tree."""
        for key, value in source.items():
            if key in ["text", "command"]:
                # Skip these special keys for file updates
                continue
                
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                # Recursively merge dictionaries
                self._merge_trees(target[key], value)
            else:
                # Update or add the value
                target[key] = value
    
    def _update_interface_file(self, file_path: str, file_data: Dict):
        """Update interface.json with only summary and dependents changes."""
        try:
            if self.interface_file.exists():
                with open(self.interface_file, 'r', encoding='utf-8') as f:
                    interface_data = json.load(f)
                
                # Convert flat path to tree structure for the update
                tree_update = self._flat_to_tree({file_path: file_data})
                
                # Create update data with only summary and dependents
                update_data = {}
                if "summary" in file_data:
                    update_data["summary"] = file_data["summary"]
                if "dependents" in file_data:
                    update_data["dependents"] = file_data["dependents"]
                update_data["request"] = {}
                
                # Merge the tree update into existing interface data
                self._merge_tree_update(interface_data, tree_update, update_data, file_path.split('/'))
                
                with open(self.interface_file, 'w', encoding='utf-8') as f:
                    json.dump(interface_data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error updating interface file: {e}[/red]")
    
    def _merge_tree_update(self, target: Dict, source: Dict, update_data: Dict, path_parts: list):
        """Merge specific file update into tree structure."""
        current_target = target
        current_source = source
        
        # Navigate to the correct level in both trees
        for part in path_parts:
            if part in current_source:
                current_source = current_source[part]
            
            if part not in current_target:
                current_target[part] = {}
            current_target = current_target[part]
        
        # Apply the update data
        for key, value in update_data.items():
            current_target[key] = value
    
    def _remove_from_interface(self, file_path: str):
        """Remove file from interface.json using tree structure."""
        try:
            if self.interface_file.exists():
                with open(self.interface_file, 'r', encoding='utf-8') as f:
                    interface_data = json.load(f)
                
                # Remove from tree structure
                self._remove_from_tree(interface_data, file_path.split('/'))
                
                with open(self.interface_file, 'w', encoding='utf-8') as f:
                    json.dump(interface_data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error removing from interface file: {e}[/red]")
    
    def _remove_from_tree(self, tree: Dict, path_parts: list):
        """Remove a file from tree structure."""
        if len(path_parts) == 1:
            # Last part - remove the file
            if path_parts[0] in tree:
                del tree[path_parts[0]]
        else:
            # Navigate deeper
            current_part = path_parts[0]
            if current_part in tree:
                self._remove_from_tree(tree[current_part], path_parts[1:])
                
                # Clean up empty directories
                if isinstance(tree[current_part], dict) and not tree[current_part]:
                    del tree[current_part]