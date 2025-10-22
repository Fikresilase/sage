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
    
    def process_ai_response(self, ai_response: Dict[str, Any]) -> dict:
        try:
            program_results = []
            actions_taken = False
            
            for file_path, file_data in ai_response.items():
                if file_path not in ["text", "command", "update"] and isinstance(file_data, dict):
                    request = file_data.get("request", {})
                    
                    if "provide" in request:
                        file_content = self._read_file(file_path)
                        program_results.append(f"File content for {file_path}:\n{file_content}")
                        actions_taken = True
                    
                    elif "edit" in request:
                        result = self._edit_file(file_path, request["edit"])
                        program_results.append(f" {file_path} edited successfully" if result else f"❌ Failed to edit {file_path}")
                        actions_taken = True
                    
                    # ... other operations ...
            
            if "command" in ai_response:
                command_data = ai_response["command"]
                
                # Handle both string and object formats
                if isinstance(command_data, str):
                    # Simple string command
                    commands = [command_data]
                elif isinstance(command_data, dict) and "commands" in command_data:
                    # Complex command object
                    commands = command_data["commands"]
                    platform = command_data.get("platform", "")
                    terminal = command_data.get("terminal", "")
                    
                    if platform or terminal:
                        console.print(f"[dim]Platform: {platform}, Terminal: {terminal}[/dim]")
                else:
                    # Fallback - treat as single command
                    commands = [str(command_data)]
                
                # Execute all commands and capture ALL terminal output
                for cmd in commands:
                    console.print(f"[yellow] Executing: {cmd}[/yellow]")
                    console.print("[dim]─" * 50 + "[/dim]")
                    
                    # Capture ALL terminal output for AI
                    terminal_output = self._execute_command_and_capture_output(cmd)
                    program_results.append(f"Command: {cmd}\n{terminal_output}")
                    
                    console.print("[dim]─" * 50 + "[/dim]")
                
                actions_taken = True
            
            return {
                "has_actions": actions_taken,
                "results": "\n".join(program_results) if actions_taken else ai_response.get("text", "")
            }
            
        except Exception as e:
            return {
                "has_actions": True,
                "results": f" Error in orchestrator: {str(e)}"
            }
    
    def update_interface_json(self, new_interface_data: Dict[str, Any]):
        try:
            cleaned_data = {}
            for key, value in new_interface_data.items():
                if key in ["text", "command"]:
                    cleaned_data[key] = value
                elif isinstance(value, dict):
                    cleaned_value = value.copy()
                    cleaned_value["request"] = {}
                    cleaned_data[key] = cleaned_value
            
            with open(self.interface_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2)
            
            console.print("[green] Interface JSON updated successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]x Error updating interface JSON: {e}[/red]")
            return False
    
    def _read_file(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if path.exists():
                return path.read_text(encoding='utf-8')
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _edit_file(self, file_path: str, edit_data: Dict) -> bool:
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            content = path.read_text(encoding='utf-8').splitlines()
            start = edit_data.get("start", 1) - 1
            end = edit_data.get("end", len(content))
            new_content = edit_data.get("content", [])
            updated_content = content[:start] + new_content + content[end:]
            path.write_text("\n".join(updated_content), encoding='utf-8')
            return True
        except Exception as e:
            console.print(f"[red]Error editing file: {e}[/red]")
            return False
    
    def _write_file(self, file_path: str, content: list) -> bool:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(content), encoding='utf-8')
            return True
        except Exception as e:
            console.print(f"[red]Error writing file: {e}[/red]")
            return False
    
    def _delete_file(self, file_path: str) -> bool:
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
        try:
            old_path_obj = Path(old_path)
            if not old_path_obj.exists():
                console.print(f"[red]Error: File to rename not found: {old_path}[/red]")
                return False
            new_path_obj = Path(new_name)
            if new_path_obj.parent == Path('.'):
                new_path_obj = old_path_obj.parent / new_name
            new_path_obj.parent.mkdir(parents=True, exist_ok=True)
            old_path_obj.rename(new_path_obj)
            console.print(f"[green] Renamed {old_path} to {new_path_obj}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error renaming file {old_path} to {new_name}: {e}[/red]")
            return False

    def _execute_command(self, command: str) -> str:
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

    def _execute_command_with_display(self, command: str) -> str:
        """Execute command with real-time terminal display"""
        try:
            # Direct passthrough to terminal - user sees everything
            result = subprocess.run(
                command, 
                shell=True,
                # No capture - output goes directly to terminal
            )
            
            if result.returncode == 0:
                return "Command completed successfully"
            else:
                return f"Error: Command failed with exit code {result.returncode}"
                
        except Exception as e:
            return f"Command execution failed: {str(e)}"

    def _execute_command_and_capture_output(self, command: str) -> str:
        """Execute command and capture ALL terminal output for AI"""
        try:
            # Execute command and capture ALL output (both stdout and stderr)
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=os.getcwd()
            )
            
            # Combine both stdout and stderr to get EVERYTHING
            full_output = ""
            if result.stdout:
                full_output += result.stdout
            if result.stderr:
                full_output += f"\n{result.stderr}"
            
            # Also display to user in real terminal
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
            
            return full_output.strip() if full_output else "(No output)"
                
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg