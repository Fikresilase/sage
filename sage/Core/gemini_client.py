import google.generativeai as genai
from rich.console import Console
from rich.status import Status

console = Console()

def send_to_gemini(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """
    Send prompt to Gemini AI and return response.
    Includes full console logging of all prompts and AI output.
    """
    try:
        console.print("[bold cyan]🔹 Configuring Gemini API...[/bold cyan]")
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 10000,
        }
        console.print("[bold cyan]🔹 Generation configuration:[/bold cyan]")
        console.print(generation_config)
        
        console.print("[bold cyan]🔹 Initializing Gemini model...[/bold cyan]")
        model = genai.GenerativeModel(
            'gemini-2.5-pro',
            generation_config=generation_config,
            system_instruction=system_prompt
        )
        
        # Log system prompt fully
        console.print("\n[bold yellow]📝 Full System Prompt Sent to AI:[/bold yellow]")
        console.print(system_prompt)
        
        # Log user prompt fully
        console.print("\n[bold yellow]💬 Full User Prompt Sent to AI:[/bold yellow]")
        console.print(user_prompt)
        
        console.print("\n[bold cyan]🔹 Sending request to Gemini...[/bold cyan]")
        response = model.generate_content(user_prompt)
        
        if response.text:
            console.print("\n[bold green]✅ Full AI Response Received:[/bold green]")
            console.print(response.text)
            return response.text.strip()
        else:
            console.print("[yellow]⚠️ No text in Gemini response[/yellow]")
            return "{}"
            
    except Exception as e:
        console.print(f"[red]❌ Gemini API error: {e}[/red]")
        return "{}"
