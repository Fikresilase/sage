import json
from pathlib import Path
from rich.console import Console

from .gemini_client import send_to_gemini
from .orchestrator import Orchestrator
from .prompts import SYSTEM_PROMPT

console = Console()

# SYSTEM_PROMPT = """ my system prompt for the AI"""

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
