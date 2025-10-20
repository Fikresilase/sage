from openai import OpenAI
from rich.console import Console
from .env_util import get_api_key, get_model
from .prompts import QUERY_TRANSFORMER_PROMPT
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
        console.print(f"[bold cyan]🔹 OpenRouter client initialized with model: {self.model}[/bold cyan]")
    
    def _send_request(self, messages: list) -> Optional[str]:
        """Send request to OpenRouter and return response"""
        if not self.client:
            console.print("[red]x Error: OpenRouter client not initialized[/red]")
            return None
        
        try:
            console.print("\n[bold cyan]🔹 Sending request to OpenRouter...[/bold cyan]")
            console.print(f"[dim]Using model: {self.model}[/dim]")
            
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://your-site.com",
                    "X-Title": "Your App Name",
                },
                model=self.model,
                messages=messages,
                temperature=0.7,  # Lowered for more consistent results
                top_p=0.8,
                max_tokens=10000,
            )
            ai_response = completion.choices[0].message.content
            console.print("[bold green]✓ API request successful[/bold green]")
            console.print(f"[dim]Response length: {len(ai_response)} characters[/dim]")
            return ai_response.strip()
        except Exception as e:
            console.print(f"[red]x Error during API request: {e}[/red]")
            return None

# Load the query transformer prompt
query_transformer_prompt = QUERY_TRANSFORMER_PROMPT

def transform_query(interface_data: dict, user_prompt: str, transformation_prompt: str) -> str:
    """
    Step 1: Transform user prompt based on interface JSON schema
    """
    console.print("\n" + "="*50)
    console.print("[bold blue]STEP 1: QUERY TRANSFORMATION[/bold blue]")
    console.print("="*50)
    
    if not interface_data:
        console.print("[red]x No interface data provided for transformation[/red]")
        return user_prompt  # Return original prompt if no interface data
    
    client = OpenRouterClient()
    console.print(f"[dim]Transformation prompt : {transformation_prompt}[/dim]")
    console.print(f"[dim]Original user prompt: {user_prompt}[/dim]")
    console.print(f"[dim]Interface data keys: {list(interface_data.keys())}[/dim]")
    
    messages = [
        {"role": "system", "content": transformation_prompt},
        {"role": "user", "content": f"Interface: {json.dumps(interface_data, indent=2)}\n\nUser Prompt: {user_prompt}"}
    ]
    
    console.print("\n[bold yellow]🔄 Transforming user query...[/bold yellow]")
    transformed_prompt = client._send_request(messages)
    
    if transformed_prompt:
        console.print("\n[bold green]✓ Query transformation successful[/bold green]")
        console.print(f"[green]Transformed prompt preview:[/green] {transformed_prompt[:200]}...")
        return transformed_prompt
    else:
        console.print("[red]x Query transformation failed, using original prompt[/red]")
        return user_prompt

def process_with_system_prompt(interface_data: dict, transformed_prompt: str, system_prompt: str) -> str:
    """
    Step 2: Send transformed prompt to AI with system prompt AND interface data
    """
    console.print("\n" + "="*50)
    console.print("[bold blue]STEP 2: FINAL PROCESSING[/bold blue]")
    console.print("="*50)
    
    client = OpenRouterClient()
    
    console.print(f"[dim]System prompt length: {len(system_prompt)} characters[/dim]")
    console.print(f"[dim]Transformed prompt length: {len(transformed_prompt)} characters[/dim]")
    console.print(f"[dim]Interface data included: Yes[/dim]")
    
    # Combine interface data with transformed prompt for the AI
    full_user_content = f"""Project Interface:
{json.dumps(interface_data, indent=2)}

User Request:
{transformed_prompt}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_user_content}
    ]
    
    console.print("\n[bold yellow] Processing with system prompt...[/bold yellow]")
    final_response = client._send_request(messages)
    
    if final_response:
        console.print("\n[bold green]✓ Final processing successful[/bold green]")
        console.print(f"[green]Final response preview:[/green] {final_response[:200]}...")
        return final_response
    else:
        console.print("[red]x Final processing failed[/red]")
        return "{}"

def two_step_ai_processing(interface_data: dict, user_prompt: str, system_prompt: str, transformation_prompt: str = None) -> str:
    """Main two-step processing function"""
    console.print("\n" + "="*60)
    console.print("[bold magenta] STARTING TWO-STEP AI PROCESSING[/bold magenta]")
    console.print("="*60)

    # Use default transformation prompt if not provided
    if transformation_prompt is None:
        transformation_prompt = query_transformer_prompt
        console.print("[dim]Using default transformation prompt[/dim]")
    
    # Step 1: Transform the query
    transformed_query = transform_query(
        interface_data=interface_data,
        user_prompt=user_prompt,
        transformation_prompt=transformation_prompt
    )
    
    # Step 2: Process with system prompt AND interface data
    final_response = process_with_system_prompt(
        interface_data=interface_data,
        transformed_prompt=transformed_query,
        system_prompt=system_prompt
    )
    
    console.print("\n" + "="*60)
    console.print("[bold magenta] TWO-STEP PROCESSING COMPLETED[/bold magenta]")
    console.print("="*60)
    
    return final_response

# Legacy function for backward compatibility
def send_to_openrouter(system_prompt: str, user_prompt: str) -> str:
    """
    Send prompt to OpenRouter AI using OpenAI client.
    (Single-step version for backward compatibility)
    """
    console.print("\n[bold yellow]🔹 Using legacy single-step processing[/bold yellow]")
    
    client = OpenRouterClient()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    
    console.print(f"[dim]System prompt: {system_prompt[:100]}...[/dim]")
    console.print(f"[dim]User prompt: {user_prompt[:100]}...[/dim]")
    
    response = client._send_request(messages) or "{}"
    console.print(f"[dim]Response: {response[:200]}...[/dim]")
    
    return response