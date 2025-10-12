import json
from pathlib import Path
from rich.console import Console
from .api import send_to_openrouter
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
            # Load interface data (flat structure)
            interface_data = self._load_interface_data()
            if not interface_data:
                console.print("[red]x Error: Could not load project interface data. Please run setup first.[/red]")
                return "x Error: Could not load project interface data. Please run setup first."

            # Add conversation history to context
            history_context = self._format_conversation_history()

            # If we have pending actions from previous step, include the results
            action_results = ""
            if self.pending_actions and self.conversation_history:
                last_entry = self.conversation_history[-1]
                if "action_results" in last_entry:
                    action_results = f"\nPrevious Action Results:\n{last_entry['action_results']}"

            # Combine everything into the final prompt
            combined_prompt = f"""
    Project Interface JSON:
    {json.dumps(interface_data, indent=2)}

    {history_context}
    {action_results}

    User Question: {user_prompt}

    Please provide a helpful response based on the project structure and the user's question.
    """

            ai_response_text = send_to_openrouter(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=combined_prompt
            )

            # Parse AI response
            ai_response = self._parse_ai_response(ai_response_text)

            # Process through orchestrator - this returns action results
            orchestrator_response = self.orchestrator.process_ai_response(ai_response)

            # Check if actions were taken (orchestrator returns action results)
            if self._contains_action_results(orchestrator_response):
                # Store the initial AI response and orchestrator results
                self.conversation_history.append({
                    "user": user_prompt,
                    "ai": ai_response,
                    "action_results": orchestrator_response,
                    "pending": True
                })

                #  KEY CHANGE: Always send orchestrator results back to AI
                follow_up_response = self._get_ai_followup(orchestrator_response, interface_data)

                #  KEY CHANGE: Update interface if AI explicitly says "yes" in "update" field - NO OTHER CONDITIONS
                if follow_up_response.get("update", "").lower() == "yes":
                    self.orchestrator.update_interface_json(follow_up_response)
                    console.print("[green]✓ Interface JSON updated per AI request[/green]")
                else:
                    console.print("[yellow] Interface JSON not updated - AI did not request update[/yellow]")

                # Store the follow-up response
                self.conversation_history.append({
                    "user": "[System: Orchestrator Results]",
                    "ai": follow_up_response,
                    "pending": False
                })

                # Return only the follow-up AI's text to user
                return follow_up_response.get("text", "").strip()

            else:
                # No actions taken, normal flow - but check if AI wants to update interface anyway
                #  NEW: Check if AI wants to update interface even without actions
                if ai_response.get("update", "").lower() == "yes":
                    self.orchestrator.update_interface_json(ai_response)
                    console.print("[green]✓ Interface JSON updated per AI request (no actions taken)[/green]")

                # Store the response
                self.conversation_history.append({
                    "user": user_prompt,
                    "ai": ai_response,
                    "orchestrator": orchestrator_response,
                    "pending": False
                })
                self.pending_actions = False

                # Return only AI's text
                return ai_response.get("text", "").strip()

        except Exception as e:
            console.print(f"[red]x Error in combiner: {e}[/red]")
            return f"Error: {str(e)}"

    def _get_ai_followup(self, orchestrator_results: str, interface_data: dict) -> dict:
        """Immediately send orchestrator results back to AI for processing"""

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

        ai_response_text = send_to_openrouter(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=followup_prompt
        )

        # Parse and return the AI's follow-up response
        return self._parse_ai_response(ai_response_text)

    def _contains_action_results(self, response: str) -> bool:
        """Check if response contains action results (success/error messages)"""
        if not isinstance(response, str):
            return False

        action_indicators = ["✅", "x", "edited successfully", "created successfully",
                           "deleted successfully", "Command:", "File content for",
                           "renamed successfully", "Error:", "Failed to"]
        return any(indicator in response for indicator in action_indicators)

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
            console.print("[yellow] AI response is not valid JSON, treating as text[/yellow]")
            return {"text": response_text, "update": "no"}  # Default to no update

    def _load_interface_data(self):
        interface_file = Path("Sage/interface.json")
        if not interface_file.exists():
            console.print("[red]x interface.json not found. Please run setup first.[/red]")
            return None
        try:
            with open(interface_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]x Error loading interface.json: {e}[/red]")
            return None

    def _format_conversation_history(self) -> str:
        if not self.conversation_history:
            return ""

        history_parts = ["\n Conversation History:"]
        for i, entry in enumerate(self.conversation_history[-3:], 1):
            history_parts.append(f"Exchange {i+len(self.conversation_history)-3}:")
            history_parts.append(f"  User: {entry['user']}")

            if entry.get("pending", False):
                history_parts.append(f"  Status: Action completed, waiting for AI update")
            else:
                ai_text = entry['ai'].get('text', 'No text response')
                history_parts.append(f"  AI Response: {ai_text}")

        return "\n".join(history_parts)

# Backward compatibility function
def get_ai_response(user_prompt: str, api_key: str) -> str:
    """
    Creates a Combiner instance and gets an AI response.
    This is kept for backward compatibility.
    """
    combiner = Combiner(api_key)
    return combiner.get_ai_response(user_prompt)