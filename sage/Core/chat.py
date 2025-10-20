import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
from rich.spinner import Spinner
from rich.live import Live
from rich.status import Status
from rich.table import Table
import time
from .combiner import Combiner
from .env_util import get_api_key, get_model
from .select_models import select_model
import os

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
console = Console()
# Define your main color and related colors
MAIN_COLOR = "#8B5CF6" 
ACCENT_COLOR = "#00c8e2"         #   "#8e1c8e"
USER_COLOR = "#1D5ACA"   
def display_header():
    """
    Displays a modern SAGE ASCII art logo for the CLI tool.
    """
    console.print()
    logo_text = [
        "     ███████╗       █████╗         ██████╗        ███████╗",
        "     ██╔════╝      ██╔══██╗       ██╔════╝        ██╔════╝", 
        "     ███████╗      ███████║       ██║  ███╗       █████╗  ",
        "     ╚════██║      ██╔══██║       ██║   ██║       ██╔══╝  ",
        "     ███████║      ██║  ██║       ╚██████╔╝       ███████╗",
        "     ╚══════╝      ╚═╝  ╚═╝        ╚═════╝        ╚══════╝",
        "              A senior developr in your terminal          "
    ]
    accent_color = "#8B5CF6"  # Purple
    
    # Print the modern logo
    for line in logo_text:
        console.print(f"[{accent_color}]{line}[/]")

    console.print()
    
    # --- Tips for getting started ---
    console.print("Welcome to Sage:", style="white")
    console.print("1. Ask questions, edit files, or run commands.")
    console.print("2. Be specific for the best results.")
    # console.print("3. Create [magenta]SAGE.txt[/magenta] files to customize your interactions with Sage.")
    console.print("3. Type [cyan]model[/cyan] to select a model")
    console.print("4. Type [cyan]voice[/cyan] to use the voice mode")
    console.print("\n")
def display_footer():
    ownership = Text("made by a brokie called ", style="bright_black")
    ownership.append("Fikre", style="magenta")
    ownership.append(" to not pay for cli tools", style="bright_black") # gray text
    width = console.width
    # Pad with spaces on the left
    ownership.pad_left(width - len(ownership.plain))
    console.print(ownership)

def display_chat_ready():
    """Display the chat ready UI after operations like model selection."""
    # os.system('cls' if os.name == 'nt' else 'clear')
    display_header()
    display_footer()
    console.print(f"[{ACCENT_COLOR}]Sage is ready. Type your message below.[/{ACCENT_COLOR}]")

def chat():
    """
    Main chat function that sets up the UI and enters the interactive loop.
    """
    # Get API key first
    api_key = get_api_key()
    if not api_key:
        console.print(f"[bold red] Cannot start chat without API key[/bold red]")
        return
    
    # Initialize combiner (which includes orchestrator)
    combiner = Combiner(api_key)
    
    # Display the static screen that perfectly matches the provided image
    display_chat_ready()

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
                
                        # Handle model selection without sending to AI
            # Handle model selection without sending to AI
            if user_message.lower() == 'model':
                try:
                    selected_model = select_model()
                    if selected_model:
                        console.print(f"[{MAIN_COLOR}]✓ Model changed to: {selected_model}[/{MAIN_COLOR}]")
                    else:
                        console.print("[yellow]Model selection cancelled[/yellow]")
                except KeyboardInterrupt:
                    console.print("\n[yellow]Model selection interrupted by user[/yellow]")
                except Exception as e:
                    console.print(f"[red]✗ Error during model selection: {e}[/red]")
                finally:
                    # Continue to show the messages and get next input
                    continue
                
            # Handle voice mode (you can add similar logic for voice)
            if user_message.lower() == 'voice':
                console.print(f"[{ACCENT_COLOR}] Voice mode feature comming soon... Use your fingers till then[/{ACCENT_COLOR}]")
                # display_chat_ready()
                continue

            # Only send to AI if it's not a command
            # Get AI response with a spinner
            response = _get_ai_response_with_spinner(user_message, combiner)
            
            if response:
                _display_ai_response(response)
            else:
                console.print("[red] No response from AI[/red]")
                
            console.print()
            
        except KeyboardInterrupt:
            console.print(f"\n[{MAIN_COLOR}]👋 Chat session ended by user[/{MAIN_COLOR}]")
            break
        except Exception as e:
            console.print(f"[red]xxx Error in chat: {e}[/red]")
            break

def _get_user_input() -> str:
    """Multiline input. Submit with double Enter, Ctrl+J, or Ctrl+D."""
    kb = KeyBindings()
    
    # Track the last Enter press time for double Enter detection
    last_enter_time = [0]
    ENTER_DOUBLE_THRESHOLD = 0.5  # seconds

    @kb.add('enter')
    def _(event):
        current_time = time.time()
        # If Enter was pressed recently enough, treat as double Enter and submit
        if current_time - last_enter_time[0] < ENTER_DOUBLE_THRESHOLD:
            event.app.exit(result=event.current_buffer.text)
        else:
            # Single Enter - just insert newline
            event.current_buffer.insert_text('\n')
            last_enter_time[0] = current_time

    @kb.add('c-j')
    def _(event):
        event.app.exit(result=event.current_buffer.text)

    @kb.add('c-d')
    def _(event):
        event.app.exit(result=event.current_buffer.text)

    @kb.add('c-c')
    def _(event):
        raise KeyboardInterrupt

    style = Style.from_dict({'prompt': f'bold {USER_COLOR}'})

    session = PromptSession(
        multiline=True,
        key_bindings=kb,
        style=style,
        wrap_lines=True,
        complete_while_typing=False,
    )

    try:
        if not hasattr(_get_user_input, 'shown_hint'):
            console.print("[dim]Type your message (multiline OK).[/dim]")
            console.print("[dim]Press [cyan]Enter twice[/cyan] to send, or [cyan]Ctrl+J[/cyan] / [cyan]Ctrl+D[/cyan] if that fails.[/dim]")
            _get_user_input.shown_hint = True

        result = session.prompt("┃ ")
        return result.strip() if result else ""
    except KeyboardInterrupt:
        raise
    except EOFError:
        return ""
def _get_ai_response_with_spinner(user_message: str, combiner: Combiner) -> str:
    """Get AI response with a loading spinner."""
    # console.print(f"[bold cyan]🔹 Using model: {get_model()}[/bold cyan]")
    # console.print(f"[bold cyan]🔹 Sending request to OpenRouter...[/bold cyan]")

    # now show spinner *only* while waiting
    with Status(
        f"[bold {MAIN_COLOR}] Sage is thinking...[/bold {MAIN_COLOR}]",
        spinner="dots",
        spinner_style=MAIN_COLOR
    ):
        response = combiner.get_ai_response(user_message)

    return response

def _display_ai_response(response: str):
    """Display AI response in a beautiful and clean panel."""
    console.print(
        Panel(
            Text(response, style="white"),
            title=f"[bold {MAIN_COLOR}]🧙 Sage[/bold {MAIN_COLOR}]",
            border_style=MAIN_COLOR,
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )