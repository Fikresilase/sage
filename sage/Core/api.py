from openai import OpenAI
from rich.console import Console
from .env_util import get_api_key, get_model
console = Console()
def send_to_openrouter(system_prompt: str, user_prompt: str) -> str:
    """
    Send prompt to OpenRouter AI using OpenAI client.
    """
    try:
        # Load API key and model
        api_key = get_api_key()
        if not api_key:
            return "{}"
        model = get_model()
        if not model:
            console.print("[red]x Error: MODEL not found in .env file[/red]")
            return "{}"
        console.print(f"[bold cyan]🔹 Using model: {model}[/bold cyan]")
        # Initialize OpenAI client with OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        # Log prompts
        # console.print("\n[bold yellow]📝 Full System Prompt Sent to AI:[/bold yellow]")
        # console.print(system_prompt)
        # console.print("\n[bold yellow]💬 Full User Prompt Sent to AI:[/bold yellow]")
        # console.print(user_prompt)
        console.print("\n[bold cyan]🔹 Sending request to OpenRouter...[/bold cyan]")
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site.com",  # Update with your site
                "X-Title": "Your App Name",  # Update with your app name
            },
            model=model,
            messages=messages,
            temperature=1,
            top_p=0.8,
            max_tokens=10000,
        )
        ai_response = completion.choices[0].message.content
        # console.print("\n[bold green]✅ Full AI Response Received:[/bold green]")
        # console.print(ai_response)
        return ai_response.strip()
    except Exception as e:
        console.print(f"[red]x Error: {e}[/red]")
        return "{}"