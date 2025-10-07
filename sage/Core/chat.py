import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
from rich.spinner import Spinner
from rich.live import Live
from rich.status import Status
import time

from .combiner import get_ai_response
from .env_util import get_api_key

console = Console()

def chat():
    """
    Chat interface that takes user input, shows processing animation,
    gets AI response, and displays it in a loop.
    """
    # Get API key first
    api_key = get_api_key()
    if not api_key:
        console.print("[bold red]❌ Cannot start chat without API key[/bold red]")
        return
    
    console.print(
        Panel.fit(
            "[bold green]💬 Sage Chat Interface[/bold green]\nType 'exit', 'quit', or press Ctrl+C to leave",
            border_style="green",
            padding=(1, 2)
        )
    )
    console.print()
    
    while True:
        try:
            # Get user input using a clean, single-line prompt
            user_message = _get_user_input()
            
            if not user_message:
                console.print("[yellow]No message entered. Exiting chat...[/yellow]")
                break
                
            if user_message.lower() in ['exit', 'quit', 'bye']:
                console.print("[green]👋 Goodbye![/green]")
                break

            # Immediately display the user's message in a final, clean box
            _display_user_message_in_box(user_message)
            
            # Get AI response with a spinner
            response = _get_ai_response_with_spinner(user_message, api_key)
            
            if response:
                _display_ai_response(response)
            else:
                console.print("[red]❌ No response from AI[/red]")
                
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[green]👋 Chat session ended by user[/green]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error in chat: {e}[/red]")
            break

def _get_user_input() -> str:
    """
    Clean input prompt that visually matches the response boxes.
    
    Returns:
        str: User's input text
    """
    # Simple, clean prompt that matches the aesthetic
    try:
        user_input = console.input(
            Text("💬 ", style="bold green") + 
            Text("You: ", style="bold cyan") + 
            Text("", style="bright_white")
        )
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return ""

def _display_user_message_in_box(message: str):
    """
    Displays the user's final message in a complete, clean box.
    """
    console.print(
        Panel(
            Text(message, style="white"),
            title="[bold green]👤 You[/bold green]",
            border_style="green",
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )

def _get_ai_response_with_spinner(user_message: str, api_key: str) -> str:
    """
    Get AI response with a loading spinner.
    
    Args:
        user_message: User's input message
        api_key: API key for Gemini
        
    Returns:
        str: AI response text
    """
    # Show processing with an animated spinner
    with Status(
        "[bold green]🤖 Sage is thinking...[/bold green]", 
        spinner="dots",
        spinner_style="green"
    ) as status:
        response = get_ai_response(user_message, api_key)
    
    return response

def _display_ai_response(response: str):
    """
    Display AI response in a beautiful and clean panel.
    
    Args:
        response: AI response text to display
    """
    console.print(
        Panel(
            Text(response, style="white"),
            title="[bold green]🧠 Sage[/bold green]",
            border_style="green",
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )