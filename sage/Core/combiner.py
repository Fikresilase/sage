import json
from pathlib import Path
from rich.console import Console
from .api import send_to_openrouter, two_step_ai_processing, query_transformer_prompt
from .orchestrator import Orchestrator
from .prompts import SYSTEM_PROMPT

console = Console()

class Combiner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.orchestrator = Orchestrator(api_key)
        self.conversation_history = []
        self.pending_actions = False

    def get_ai_response(self, user_prompt: str) -> str:
        try:
            interface_data = self._load_interface_data()
            if not interface_data:
                return "x Error: Could not load project interface data. Please run setup first."

            # Use two-step processing with interface data - NO CONSOLE.PRINT HERE
            ai_response_text = two_step_ai_processing(
                interface_data=interface_data,
                user_prompt=user_prompt,
                system_prompt=SYSTEM_PROMPT,
                transformation_prompt=query_transformer_prompt
            )

            ai_response = self._parse_ai_response(ai_response_text)
            
            # Check if response contains actions that need orchestrator processing
            if self._is_action_response(ai_response):
                # NO STEP 3 HEADER PRINT HERE - let the outer spinner handle it
                orchestrator_response = self.orchestrator.process_ai_response(ai_response)
                
                # Always get results from dict (orchestrator now always returns dict)
                results_text = orchestrator_response.get("results", "")
                has_actions = orchestrator_response.get("has_actions", False)

                if has_actions:
                    self.conversation_history.append({
                        "user": user_prompt,
                        "ai": ai_response,
                        "action_results": results_text,
                        "pending": True
                    })

                    # Get follow-up response for action results
                    follow_up_response = self._get_ai_followup(results_text, interface_data)

                    if follow_up_response.get("update", "").lower() == "yes":
                        self.orchestrator.update_interface_json(follow_up_response)
                        console.print("[green]✓ Interface JSON updated[/green]")

                    self.conversation_history.append({
                        "user": "[System: Orchestrator Results]",
                        "ai": follow_up_response,
                        "pending": False
                    })

                    return follow_up_response.get("text", "").strip()
                else:
                    # Handle case where orchestrator processed but no actions were taken
                    self.conversation_history.append({
                        "user": user_prompt,
                        "ai": ai_response,
                        "orchestrator": results_text,
                        "pending": False
                    })
                    self.pending_actions = False
                    return results_text if results_text else ai_response.get("text", "").strip()

            else:
                # Simple text response - no actions needed
                if ai_response.get("update", "").lower() == "yes":
                    self.orchestrator.update_interface_json(ai_response)
                    console.print("[green]✓ Interface JSON updated (no actions)[/green]")

                self.conversation_history.append({
                    "user": user_prompt,
                    "ai": ai_response,
                    "pending": False
                })
                self.pending_actions = False

                return ai_response.get("text", "").strip()

        except Exception as e:
            console.print(f"[red]x Error in combiner: {e}[/red]")
            return f"Error: {str(e)}"

    def _is_action_response(self, response: dict) -> bool:
        """Check if AI response contains actions that need orchestrator processing"""
        if not isinstance(response, dict):
            return False
        
        # Check for file operations (keys that aren't standard response fields)
        standard_fields = ["text", "update", "command"]
        action_keys = [key for key in response.keys() if key not in standard_fields]
        
        if action_keys:
            return True
        
        # Check for command operations
        if "command" in response:
            return True
            
        return False

    def _get_ai_followup(self, orchestrator_results: str, interface_data: dict) -> dict:
        """Get follow-up response for action results"""
        followup_prompt = f"""
Project Interface JSON:
{json.dumps(interface_data, indent=2)}

**ORCHESTRATOR EXECUTION RESULTS:**
{orchestrator_results}

Please process these orchestrator results and provide a user-friendly response.
You should:
1. Summarize what was accomplished (or what failed) in a natural way
2. Suggest next steps if appropriate

**Include an "update" field in your response with either "yes" or "no"**
- Say "yes" if you want to update the project interface JSON with any structural changes
- Say "no" if no interface update is needed

Respond in the standard JSON format with:
- "text": user-friendly message
- "update": "yes" or "no"
- Any additional file operations if needed
"""

        # Use direct API call for follow-up (no transformation needed)
        ai_response_text = send_to_openrouter(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=followup_prompt
        )

        return self._parse_ai_response(ai_response_text)

    def _parse_ai_response(self, response_text: str) -> dict[str, any]:
        """Parse AI response text into a dictionary"""
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            console.print("[yellow]⚠️  AI response is not valid JSON, treating as text[/yellow]")
            return {"text": response_text, "update": "no"}

    def _load_interface_data(self):
        """Load the project interface data"""
        interface_file = Path("Sage/interface.json")
        if not interface_file.exists():
            console.print("[red]x interface.json not found. Please run setup first.[/red]")
            return None
        try:
            with open(interface_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Removed the success message to reduce noise
                return data
        except Exception as e:
            console.print(f"[red]x Error loading interface.json: {e}[/red]")
            return None