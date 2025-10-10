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

from .combiner import Combiner  # Changed import
from .env_util import get_api_key

console = Console()

# Define your main color and related colors
MAIN_COLOR = "#8B5CF6" 
ACCENT_COLOR = "#06D6A0"  
USER_COLOR = "#F472B6"   

def chat():
    
    # Get API key first
    api_key = get_api_key()
    if not api_key:
        console.print(f"[bold red]❌ Cannot start chat without API key[/bold red]")
        return
    
    # Initialize combiner (which includes orchestrator)
    combiner = Combiner(api_key)
    
    console.print(
        Panel.fit(
            f"[bold {MAIN_COLOR}]💬 Sage Chat Interface[/bold {MAIN_COLOR}]\nType 'exit', 'quit', or press Ctrl+C to leave",
            border_style=MAIN_COLOR,
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
                console.print(f"[{MAIN_COLOR}]👋 Goodbye![/{MAIN_COLOR}]")
                break

            # Immediately display the user's message in a final, clean box
            _display_user_message_in_box(user_message)
            
            # Get AI response with a spinner
            response = _get_ai_response_with_spinner(user_message, combiner)
            
            if response:
                _display_ai_response(response)
            else:
                console.print("[red]❌ No response from AI[/red]")
                
            console.print()
            
        except KeyboardInterrupt:
            console.print(f"\n[{MAIN_COLOR}]👋 Chat session ended by user[/{MAIN_COLOR}]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error in chat: {e}[/red]")
            break

def _get_user_input() -> str:
    """Clean input prompt that visually matches the response boxes."""
    try:
        user_input = console.input(
            Text("💬 ", style=f"bold {MAIN_COLOR}") + 
            Text("You: ", style=f"bold {ACCENT_COLOR}") + 
            Text("", style="bright_white")
        )
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return ""

def _display_user_message_in_box(message: str):
    """Displays the user's final message in a complete, clean box."""
    console.print(
        Panel(
            Text(message, style="white"),
            title=f"[bold {MAIN_COLOR}]👤 You[/bold {MAIN_COLOR}]",
            border_style=MAIN_COLOR,
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )

def _get_ai_response_with_spinner(user_message: str, combiner: Combiner) -> str:
    """Get AI response with a loading spinner."""
    with Status(
        f"[bold {MAIN_COLOR}]🤖 Sage is thinking...[/bold {MAIN_COLOR}]", 
        spinner="dots",
        spinner_style=MAIN_COLOR
    ) as status:
        response = combiner.get_ai_response(user_message)
    
    return response

def _display_ai_response(response: str):
    """Display AI response in a beautiful and clean panel."""
    console.print(
        Panel(
            Text(response, style="white"),
            title=f"[bold {MAIN_COLOR}]🧠 Sage[/bold {MAIN_COLOR}]",
            border_style=MAIN_COLOR,
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )