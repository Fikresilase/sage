from openai import OpenAI
from rich.console import Console
from .env_util import get_api_key, get_model
import json
import os
from pathlib import Path
from typing import Optional

console = Console()

class OpenRouterClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.model = get_model()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenRouter client"""
        if not self.api_key:
            console.print("[red]x Error: API_KEY not found in .env file[/red]")
            return
        
        if not self.model:
            console.print("[red]x Error: MODEL not found in .env file[/red]")
            return
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
    
    def _send_request(self, messages: list) -> Optional[str]:
        """Send request to OpenRouter and return response"""
        if not self.client:
            console.print("[red]x Error: OpenRouter client not initialized[/red]")
            return None
        
        try:
            # Print what's being sent to the AI
            console.print("\n[cyan]=== SENDING TO AI ===[/cyan]")
            for message in messages:
                role = message["role"]
                content = message["content"]
                console.print(f"[yellow]Role: {role}[/yellow]")
                # Truncate very long content for readability
                if len(content) > 1000:
                    console.print(f"[white]Content: {content[:1000]}...[/white]")
                    console.print(f"[white]... (content truncated, total length: {len(content)} characters)[/white]")
                else:
                    console.print(f"[white]Content: {content}[/white]")
                console.print("[cyan]---[/cyan]")
            
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://your-site.com",
                    "X-Title": "Your App Name",
                },
                model=self.model,
                messages=messages,
                temperature=0.7,
                top_p=0.8,
                max_tokens=10000,
            )
            ai_response = completion.choices[0].message.content
            
            # Print what's received from the AI
            console.print("\n[green]=== RECEIVED FROM AI ===[/green]")
            # Truncate very long responses for readability
            if len(ai_response) > 1000:
                console.print(f"[white]Response: {ai_response[:1000]}...[/white]")
                console.print(f"[white]... (response truncated, total length: {len(ai_response)} characters)[/white]")
            else:
                console.print(f"[white]Response: {ai_response}[/white]")
            console.print("[green]======================[/green]\n")
            
            return ai_response.strip()
        except Exception as e:
            console.print(f"[red]x Error during API request: {e}[/red]")
            # Re-raise the exception to stop the process
            raise e

def single_step_ai_processing(interface_data: dict, user_prompt: str, system_prompt: str) -> str:
    """Single-step processing function with interface data"""
    client = OpenRouterClient()
    
    # Combine interface data with user prompt
    full_user_content = f"""Project Interface:
{json.dumps(interface_data, indent=2)}

User Request:
{user_prompt}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_user_content}
    ]
    
    final_response = client._send_request(messages)
    
    if final_response:
        return final_response
    else:
        raise Exception("AI processing failed - no response from API")

# Legacy function for backward compatibility
def send_to_openrouter(system_prompt: str, user_prompt: str) -> str:
    """
    Send prompt to OpenRouter AI using OpenAI client.
    """
    client = OpenRouterClient()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    
    response = client._send_request(messages) or "{}"
    
    return response