import google.generativeai as genai
from rich.console import Console
from rich.status import Status

console = Console()

def send_to_gemini(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """
    Send prompt to Gemini AI and return response.
    
    Args:
        api_key: Gemini API key
        system_prompt: System instructions for the AI
        user_prompt: User's input prompt
        
    Returns:
        str: AI response text
    """
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Combine system prompt and user prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Generate content
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text.strip()
        else:
            console.print("[yellow]⚠️ No text in Gemini response[/yellow]")
            return "No response generated."
            
    except Exception as e:
        console.print(f"[red]❌ Gemini API error: {e}[/red]")
        return f"Error communicating with AI: {str(e)}"