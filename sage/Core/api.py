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
    
    def _send_request(self, messages: list) -> Optional[str]:
        """Send request to OpenRouter and return response"""
        if not self.client:
            console.print("[red]x Error: OpenRouter client not initialized[/red]")
            return None
        
        try:
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
            return ai_response.strip()
        except Exception as e:
            console.print(f"[red]x Error during API request: {e}[/red]")
            # Re-raise the exception to stop the process
            raise e

# Load the query transformer prompt
query_transformer_prompt = QUERY_TRANSFORMER_PROMPT

def transform_query(interface_data: dict, user_prompt: str, transformation_prompt: str) -> str:
    """
    Step 1: Transform user prompt based on interface JSON schema
    """
    if not interface_data:
        return user_prompt  # Return original prompt if no interface data
    
    client = OpenRouterClient()
    
    messages = [
        {"role": "system", "content": transformation_prompt},
        {"role": "user", "content": f"Interface: {json.dumps(interface_data, indent=2)}\n\nUser Prompt: {user_prompt}"}
    ]
    
    transformed_prompt = client._send_request(messages)
    
    if transformed_prompt:
        return transformed_prompt
    else:
        # If we get here, it means _send_request returned None but didn't raise an exception
        # This shouldn't happen with the new implementation, but keeping for safety
        raise Exception("Query transformation failed - no response from API")

def process_with_system_prompt(interface_data: dict, transformed_prompt: str, system_prompt: str) -> str:
    """
    Step 2: Send transformed prompt to AI with system prompt AND interface data
    """
    client = OpenRouterClient()
    
    # Combine interface data with transformed prompt for the AI
    full_user_content = f"""Project Interface:
{json.dumps(interface_data, indent=2)}

User Request:
{transformed_prompt}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_user_content}
    ]
    
    final_response = client._send_request(messages)
    
    if final_response:
        return final_response
    else:
        # Similarly, raise exception if second step fails
        raise Exception("AI processing failed - no response from API")

def two_step_ai_processing(interface_data: dict, user_prompt: str, system_prompt: str, transformation_prompt: str = None) -> str:
    """Main two-step processing function"""
    # Use default transformation prompt if not provided
    if transformation_prompt is None:
        transformation_prompt = query_transformer_prompt
    
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
    
    return final_response

# Legacy function for backward compatibility
def send_to_openrouter(system_prompt: str, user_prompt: str) -> str:
    """
    Send prompt to OpenRouter AI using OpenAI client.
    (Single-step version for backward compatibility)
    """
    client = OpenRouterClient()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    
    response = client._send_request(messages) or "{}"
    
    return response