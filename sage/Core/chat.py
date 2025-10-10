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
from .env_util import get_api_key

console = Console()

# Define your main color and related colors
MAIN_COLOR = "#8B5CF6" 
ACCENT_COLOR = "#06D6A0"  
USER_COLOR = "#F472B6"   

def display_header():
    """
    Displays the SAGE ASCII art logo and the getting started tips.
    """
    console.print()

    # A recreation of the pixel-art logo with a dithered shadow effect
    logo_text = [
        "██████╗░░█████╗░░██████╗░███████╗",
        "██╔══██╗██╔══██╗██╔════╝░██╔════╝",
        "╚█████╔╝███████║██║░░██╗░█████╗░░",
        "██╔══██╗██╔══██║██║░░╚██╗██╔══╝░░",
        "██████╔╝██║░░██║╚██████╔╝███████╗",
        "╚═════╝░╚═╝░░╚═╝░╚═════╝░╚══════╝",
    ]

    # A gradient of colors from blue to purple to pink, applied per column
    colors = [
        *["#3b82f6"]*7,  # Blue
        *["#6366f1"]*7,  # Indigo
        *["#8b5cf6"]*7,  # Purple
        *["#d946ef"]*7,  # Fuchsia
        *["#ec4899"]*7,  # Pink
    ]

    shadow_color = "grey23"
    
    # Create a "canvas" to place the shadow and text
    canvas_width = len(logo_text[0]) + 2
    canvas_height = len(logo_text) + 1
    canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]

    # Draw the dithered shadow first (using '░' character)
    for r, row in enumerate(logo_text):
        for c, char in enumerate(row):
            if char != ' ':
                # Place shadow characters offset from the main text
                if canvas[r + 1][c + 2] == ' ':
                    canvas[r + 1][c + 2] = f"[{shadow_color}]░[/]"

    # Draw the main logo text on top of the shadow
    for r, row in enumerate(logo_text):
        for c, char in enumerate(row):
            if char != ' ':
                # Use the color from the gradient list for the text
                canvas[r][c] = f"[{colors[c]}]{char}[/]"
    
    # Print the completed logo canvas
    for row in canvas:
        console.print("".join(row))

    console.print()
    
    # --- Tips for getting started ---
    console.print("Tips for getting started:", style="white")
    console.print("1. Ask questions, edit files, or run commands.")
    console.print("2. Be specific for the best results.")
    console.print("3. Create [magenta]SAGE.md[/magenta] files to customize your interactions with Sage.")
    console.print("4. [cyan]/help[/cyan] for more information.")
    console.print("\n")


def display_footer():
    ownership = Text("made with ❤️ by Fikre   ", style="bright_black")  # gray text
    width = console.width

    # Pad with spaces on the left
    ownership.pad_left(width - len(ownership.plain))
    console.print(ownership)

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
    display_header()
    display_footer()

    console.print("[bold green]Sage is ready. Type your message below.[/bold green]")
    
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
    """Clean input prompt that visually matches the response boxes."""
    try:
        # Clear the prompt line and get user input
        user_input = console.input(Text("> ", style="bold white"))
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return ""

def _get_ai_response_with_spinner(user_message: str, combiner: Combiner) -> str:
    """Get AI response with a loading spinner."""
    with Status(
        f"[bold {MAIN_COLOR}]🤔 Sage is thinking...[/bold {MAIN_COLOR}]", 
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
            title=f"[bold {MAIN_COLOR}]🧙 Sage[/bold {MAIN_COLOR}]",
            border_style=MAIN_COLOR,
            title_align="left",
            padding=(1, 2),
            box=box.ROUNDED
        )
    )