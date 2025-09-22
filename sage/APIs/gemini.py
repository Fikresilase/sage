# sage/APIs/gemini.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sage.prompts.system_prompt import SYSTEM_PROMPT_TEXT  # import the string

load_dotenv()

# Configure the API key from environment variable
genai.configure(api_key=os.environ["SAGE_GEMINI_API_KEY"])

# Create the model instance
model = genai.GenerativeModel('gemini-1.5-flash')

# Define the generation configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1.0,
    "top_k": 32,
    "max_output_tokens": 8192,
    "stop_sequences": ["<STOP>"],
}

def get_gemini_response(user_prompt: str) -> str:
    """
    Send a user prompt to Gemini and return the response.
    SYSTEM_PROMPT_TEXT is prepended to give context.
    """
    full_prompt = f"{SYSTEM_PROMPT_TEXT}\nUser: {user_prompt}\nSage:"
    response = model.generate_content(
        full_prompt,
        generation_config=generation_config
    )
    return response.text
