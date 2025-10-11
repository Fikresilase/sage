import inquirer
import os
from rich.console import Console
from pathlib import Path
import math

console = Console()
MAIN_COLOR = "#8B5CF6"

# Import models from your models.py
from .models import models

def save_model_to_env(model_name):
    """Save the selected model to .env file."""
    env_file = Path(".env")
    
    if not env_file.exists():
        # Create .env file if it doesn't exist
        env_file.write_text(f"MODEL={model_name}\n")
        console.print(f"[green]✓ Created .env file with MODEL={model_name}[/green]")
        return
    
    # Read existing .env content
    env_content = env_file.read_text(encoding="utf-8")
    lines = env_content.splitlines()
    
    # Check if MODEL already exists
    model_found = False
    new_lines = []
    
    for line in lines:
        if line.startswith("MODEL="):
            new_lines.append(f"MODEL={model_name}")
            model_found = True
        else:
            new_lines.append(line)
    
    # If MODEL not found, add it
    if not model_found:
        new_lines.append(f"MODEL={model_name}")
    
    # Write back to .env
    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    console.print(f"[white]✓ Updated .env file with MODEL={model_name}[/white]")

def display_model_page(page, page_size=10):
    """Display a page of models with pagination info and column titles."""
    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_models = models[start_idx:end_idx]
    
    total_pages = math.ceil(len(models) / page_size)
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Display header
    console.print(f"\r[{MAIN_COLOR}]Sage CLI - Model Selection[/]")
    console.print(f"[dim]Page {page + 1} of {total_pages}[/dim]")
    console.print()
    
    # Display column titles
    title_line = f"{'#':>3} {'               Models':<43} | {'Price':<8} | {'Context Window':>12}"
    console.print(f"[bold {MAIN_COLOR}]{title_line}[/bold {MAIN_COLOR}]")
    console.print("[dim]" + "─" * len(title_line) + "[/dim]")
    
    # Create choices with formatted columns
    choices = []
    for i, model in enumerate(page_models, start=1):
        model_num = f"{start_idx + i}."
        model_display = model["model"][:40].ljust(40)
        price_display = model["price"].ljust(8)
        context_display = model["context"].rjust(12)
        
        display_text = f"{model_num:>3} {model_display} | {price_display} | {context_display}"
        choices.append((display_text, model["model"]))
    
    # Add navigation options
    navigation_added = False
    if page > 0:
        choices.append(("← Previous Page", "prev_page"))
        navigation_added = True
    if end_idx < len(models):
        choices.append(("→ Next Page", "next_page"))
        navigation_added = True
    
    # Add manual input and cancel options
    choices.append(("🔍 Choose from more than 500 models from `https://openrouter.ai/models` and type manually", "manual_input"))
    choices.append(("❌ Cancel", "cancel"))
    
    return choices

def manual_model_input():
    """Allow user to manually type model name."""
    console.print("\n[cyan]Enter model name manually:[/cyan]")
    console.print("[dim]Example: google/gemini-2.0-flash-exp:free[/dim]")
    
    try:
        model_name = input("Model: ").strip()
        if model_name:
            save_model_to_env(model_name)
            return model_name
        else:
            console.print("[yellow]No model name entered[/yellow]")
            return None
    except KeyboardInterrupt:
        console.print("\n[yellow]Manual input cancelled[/yellow]")
        return None

def select_model():
    """Main model selection function with pagination."""
    page_size = 10
    current_page = 0
    
    while True:
        # Display current page
        choices = display_model_page(current_page, page_size)
        
        questions = [
            inquirer.List(
                'model',
                message="Select a model:",
                choices=choices,
                carousel=True
            )
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers:
                return None
                
            selected = answers['model']
            
            # Handle navigation
            if selected == "prev_page":
                current_page -= 1
                continue
            elif selected == "next_page":
                current_page += 1
                continue
            elif selected == "manual_input":
                return manual_model_input()
            elif selected == "cancel":
                console.print("[yellow]Model selection cancelled[/yellow]")
                return None
            else:
                # Valid model selected
                save_model_to_env(selected)
                return selected
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Model selection cancelled[/yellow]")
            return None

def main():
    """Main function to run model selection standalone."""
    selected_model = select_model()
    
    if selected_model:
        console.print(f"\n[green]✓ Model selected: {selected_model}[/green]")
        console.print(f"[green]✓ Model saved to .env file[/green]")
    else:
        console.print("[yellow]No model selected[/yellow]")
    
    return selected_model

if __name__ == "__main__":
    main()