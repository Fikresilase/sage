import json
from pathlib import Path
from rich.console import Console

from .gemini_client import send_to_gemini
from .orchestrator import Orchestrator

console = Console()

# System prompt for the AI (keep your existing one)
SYSTEM_PROMPT = """
- you are Sage a senior developer in the terminal with full context of the project structure and files.
to help with any programing task and any questions the user has about the project.

- the text that you recive is always a user request, this system prompt and the project structure context as JSON.
  the project structure context is organized in the same format and has two keys that are not files:
    - command: which contains the platform, terminal and available commands to run in the terminal.
     organized like this:"command": {
        "commands": [],
        "platform": "this explains what os you are running on",
        "summary": "very short summery of the command you are sending to the user",
        "terminal": "the type of terminal you are running on like bash, zsh, powershell, cmd, etc"
    },
    you should always populate the command array whenever you are using it as an array of strings with the commands you want to run in the terminal.
     so that the program can run them one by one.
    - text: which is where you should put your response to the user.
    - and the other keys are the file with 4 keys:
        - summary: a brief summary of the file purpose and functionality.
        - index: a unique index number for the file.
        - dependents: a list of files that import or reference this file or function or variable from this file.
        - request: if you need to do any thing with the file content you will use the 4 predefined objects
              - provide: if you need the file content to answer the user question or to update the summary or dependents.
                and it looks like this: `"request": {"provide": {}}`
              - edit: if you need to edit any file you will use this object and it looks like this: `"request": {"edit": {start: 10, end: 20, content:["new content line 1", "new content line 2"]}}`
               the start and end are the line number range to replace with the new content. and the content is a list of strings as one string a one line content. 
              - write: if you need to create a new file and write something inside you will use this object and it looks like this: `"request": {"write": ["new file content line 1", "new file content line 2"]}`
                the content is a list of strings as one string a one line content.
              - delete: if you need to delete a file you will use this object and it looks like this: `"request": {"delete": {}}`

            **important Rules**: you work flow will look like this always:
            1. you get user request with the json and you analyze the structure deeply and use the provide request to read the file content and any files that are related to that file and will be important for your dicision.
             and after you understand the files content and you know the answer you will reply only using the text key value section with the answer to the user question and asking the user if they need you to write the code in the files or run a command for them.
             if they explicitly say yes you will use the edit, write or delete request  to do that or the command key to excute a command and update the summary and dependents keys for the files you changed or created accordingly.
             and after you sent that you will get the responce from the program that looks like "program responce:src/components/ui/button.tsx edited success fully" or the error message that happend teling you the respone of you actions.
             and if it is a success you will send the entire json again with the updated summary and dependents for the files you changed or created.
             even if you didnt update or created any file you will send the entire json again with no changes.
             if it is an error you will repeat the process starting from using the text key to explain what the error is and how to fix it and asking the user if they want you to try again or if they want to change something in the user request.  


             3. the way you respond is always using the exact json structure you recived from the user but you dont have to send the entire json only the text key or files that you used the request key for them or summeries or dependents you updated.
             or if you want to excute a command you just can send the command key with the command you want to run and the platform and terminal type.
             4. always return a flat json object with no extra text or explanation.
        **example responses**
        1. using the provide key to read a file content:

         {"src/components/ui/button.tsx": {
            "summary": "A button component for the UI library.",
            "index": 5,
            "dependents": [6, 7],
            "request": {"provide": {}}
         }

         2. answering the user question using the text key:
            {
                "text": "The main entry point of the application is src/main.py. It initializes the app and sets up routing. Do you want me to add a new feature or modify existing functionality?",
            }
        3. editing a file using the edit key:
        {
            "src/main.py": {
                "summary": "The main entry point of the application.",
                "index": 1,
                "dependents": [2, 3],
                "request": {"edit": {"start": 10, "end": 15, "content": ["# New line 1", "# New line 2"]}}
            }
        }
        4. creating a new file using the write key:
        {
            "text": "I have created a new button component for you.",
            "src/components/ui/button.tsx": {
                "summary": "A button component for the UI library.",
                "index": 5,
                "dependents": [6, 7],
                "request": {"write": ["import React from 'react';", "const Button = () => {", "  return <button>Click me</button>;", "};", "export default Button;"]}
            }
        }
        5. deleting a file using the delete key:
        {   text : "I have deleted the button component as you requested.",
            "text": "I have deleted the button component as you requested.",
            "src/components/ui/button.tsx": {
                "summary": "A button component for the UI library.",
                "index": 5,
                "dependents": [6, 7],
                "request": {"delete": {}}
            }
        }
        6. running a command using the command key:
        {   text: "I am running bun to install the dependencies and run the project.",
           command: {
                "summary": "Install dependencies and run the project",
                "command": ["bun install", "bun run dev"],
                "platform": "windows",
                "terminal": "powershell"
           }
        }
       7. final response after a successful edit or write or delete or command:
       {
  "src/components/ui/amthattatatata.jsx": {
    "summary": "This is a React component written in JavaScript, designed to offer fast project rendering and improve website speed upon user installation.",
    "index": 1,
    "dependents": [],
    "request": {}
  },
  "src/components/ui/button.tsx": {
    "summary": "This file defines a reusable UI button component for interactive user actions in a React application.",
    "index": 2,
    "dependents": [4],
    "request": {}
  },
  "src/components/ui/card.tsx": {
    "summary": "This file defines a reusable UI card component for grouping and displaying content in a React application.",
    "index": 3,
    "dependents": [],
    "request": {}
  },
  "src/components/ui/form.tsx": {
    "summary": "This file defines a reusable UI form component for collecting user inputs and managing submissions in a React application.",
    "index": 4,
    "dependents": [],
    "request": {}
  },
  "src/components/ui/input.tsx": {
    "summary": "This file defines a reusable UI input field component for user text entry in a React application.",
    "index": 5,
    "dependents": [4],
    "request": {}
  },
  "src/components/ui/label.tsx": {
    "summary": "This file defines a reusable UI label component for associating text with form elements in a React application.",
    "index": 6,
    "dependents": [4, 5, 7],
    "request": {}
  },
  "src/components/ui/select.tsx": {
    "summary": "This file defines a reusable UI select dropdown component for user selection from a list of options in a React application.",
    "index": 7,
    "dependents": [4],
    "request": {}
  },
  "command": {
    "commands": [],
    "platform": "windows",
    "summary": "",
    "terminal": "cmd.exe"
  },
  "text": "this is a place holder for your response."
}

    """

class Combiner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.orchestrator = Orchestrator(api_key)
        self.conversation_history = []
    
    def get_ai_response(self, user_prompt: str) -> str:
        try:
            # Load interface data
            interface_data = self._load_interface_data()
            if not interface_data:
                console.print("[red]❌ Error: Could not load project interface data. Please run setup first.[/red]")
                return "❌ Error: Could not load project interface data. Please run setup first."
            
            # Add conversation history to context
            history_context = self._format_conversation_history()
            
            # Combine everything into the final prompt
            combined_prompt = f"""
Project Interface JSON:
{json.dumps(interface_data)}

{history_context}

User Question: {user_prompt}

Please provide a helpful response based on the project structure and the user's question.
"""
            
            # Send to Gemini
            ai_response_text = send_to_gemini(
                api_key=self.api_key,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=combined_prompt
            )
            
            # Parse AI response
            ai_response = self._parse_ai_response(ai_response_text)
            
            # Process through orchestrator
            orchestrator_response = self.orchestrator.process_ai_response(ai_response)
            
            # Add to conversation history
            self.conversation_history.append({
                "user": user_prompt,
                "ai": ai_response,
                "orchestrator": orchestrator_response
            })
            
            # Follow-up handling
            if self._needs_follow_up(orchestrator_response, ai_response):
                return self._handle_follow_up(orchestrator_response, ai_response)
            
            return orchestrator_response
            
        except Exception as e:
            console.print(f"[red]❌ Error in combiner: {e}[/red]")
            return f"Error: {str(e)}"
    
    def _parse_ai_response(self, response_text: str) -> dict[str, any]:
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            console.print("[yellow]⚠️ AI response is not valid JSON, treating as text[/yellow]")
            return {"text": response_text}
    
    def _needs_follow_up(self, orchestrator_response: str, ai_response: dict) -> bool:
        for key, value in ai_response.items():
            if key != "text" and key != "command" and isinstance(value, dict):
                if "provide" in value.get("request", {}):
                    return True
        return "Command:" in orchestrator_response or "File content for" in orchestrator_response
    
    def _handle_follow_up(self, orchestrator_response: str, previous_ai_response: dict) -> str:
        try:
            interface_data = self._load_interface_data()
            history_context = self._format_conversation_history()
            recent_user_intent = self.conversation_history[-1]["user"] if self.conversation_history else "User request to modify the project."

            full_follow_up_prompt = f"""
Project Interface JSON:
{json.dumps(interface_data)}

{history_context}

Recent User Intent: {recent_user_intent}

Previous AI request resulted in this program response:
{orchestrator_response}

Now continue the workflow: Analyze the provided content in context of the user intent. If the user explicitly requested a modification (e.g., change color to green), output the appropriate JSON for 'edit', 'write', etc. Do not ask for more confirmation—act directly. Provide a 'text' key with a brief user-friendly update if needed.

Follow the exact system prompt rules for JSON responses.
"""
            
            follow_up_response = send_to_gemini(
                api_key=self.api_key,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=full_follow_up_prompt
            )
            
            follow_up_ai_response = self._parse_ai_response(follow_up_response)
            final_response = self.orchestrator.process_ai_response(follow_up_ai_response)
            
            self.conversation_history[-1]["follow_up"] = {
                "ai": follow_up_ai_response,
                "orchestrator": final_response
            }
            
            return final_response
            
        except Exception as e:
            console.print(f"[red]❌ Error in follow-up: {e}[/red]")
            return orchestrator_response
    
    def _load_interface_data(self):
        interface_file = Path("Sage/interface.json")
        if not interface_file.exists():
            console.print("[red]❌ interface.json not found. Please run setup first.[/red]")
            return None
        try:
            with open(interface_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]❌ Error loading interface.json: {e}[/red]")
            return None
    
    def _format_conversation_history(self) -> str:
        if not self.conversation_history:
            return ""
        
        history_parts = ["\n📝 Conversation History:"]
        for i, entry in enumerate(self.conversation_history[-3:], 1):
            history_parts.append(f"Exchange {i}:")
            history_parts.append(f"  User: {entry['user']}")
            if 'follow_up' in entry:
                history_parts.append(f"  AI Final Response: {entry['follow_up']['orchestrator']}")
            else:
                history_parts.append(f"  AI Response: {entry['orchestrator']}")
        
        return "\n".join(history_parts)

# Backward compatibility
def get_ai_response(user_prompt: str, api_key: str) -> str:
    combiner = Combiner(api_key)
    return combiner.get_ai_response(user_prompt)
