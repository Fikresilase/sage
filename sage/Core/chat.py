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
        console.print("[red]❌ Cannot start chat without API key[/red]")
        return
    
    console.print(Panel.fit(
        "[bold green]💬 Sage Chat Interface[/bold green]\nType 'exit', 'quit', or press Ctrl+C to leave",
        border_style="green",
        padding=(1, 2)
    ))
    
    while True:
        try:
            # Get user input
            user_message = _get_user_input()
            
            if not user_message:
                console.print("[yellow]No message entered. Exiting chat...[/yellow]")
                break
                
            if user_message.lower() in ['exit', 'quit', 'bye']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            
            # Show processing animation and get AI response
            response = _get_ai_response_with_spinner(user_message, api_key)
            
            if response:
                _display_ai_response(response)
            else:
                console.print("[red]❌ No response from AI[/red]")
                
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Chat session ended by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error in chat: {e}[/red]")
            break

def _get_user_input() -> str:
    """
    Display beautiful glowing textbox and get user input.
    
    Returns:
        str: User's input text
    """
    chat_panel = Panel(
        Align.center(
            Text("💬 Type your message below and press ENTER to send", 
                 style="bold cyan", justify="center")
        ),
        title="✨ Sage Chat",
        title_align="center",
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2),
        style="bright_blue on black",
        subtitle="Type 'exit' to leave • Press ENTER to submit"
    )
    
    console.print()
    console.print(chat_panel)
    console.print()
    
    try:
        user_input = console.input(
            Text("📝 ", style="bold green") + 
            Text("You: ", style="bold cyan") + 
            Text("", style="bright_white")
        )
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return ""

def _get_ai_response_with_spinner(user_message: str, api_key: str) -> str:
    """
    Get AI response with a beautiful loading spinner.
    
    Args:
        user_message: User's input message
        api_key: API key for Gemini
        
    Returns:
        str: AI response text
    """
    with Status(
        "[bold cyan]🤖 Sage is thinking...[/bold cyan]", 
        spinner="dots",
        spinner_style="green"
    ) as status:
        response = get_ai_response(user_message, api_key)
    
    return response

def _display_ai_response(response: str):
    """
    Display AI response in a beautiful panel.
    
    Args:
        response: AI response text to display
    """
    console.print(
        Panel(
            f"[bold white]{response}[/bold white]",
            title="🧠 Sage Response",
            border_style="green",
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )