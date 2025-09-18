import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the API key from an environment variable
genai.configure(api_key=os.environ["SAGE_GEMINI_API_KEY"])

# Create a GenerativeModel instance
model = genai.GenerativeModel('gemini-1.5-flash')

# Define the generation configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1.0,
    "top_k": 32,
    "max_output_tokens": 8192,
    "stop_sequences": ["<STOP>"],
}
def get_gemini_response(prompt):
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    return response.text
