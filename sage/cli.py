#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file

api_key = os.getenv("OPENROUTER_API_KEY")
history = []

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ['exit', 'quit', 'q']: break
    
    history.append({"role": "user", "content": user_input})
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "deepseek/deepseek-chat", "messages": history}
    )
    
    ai_response = response.json()['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": ai_response})
    
    print(f"AI: {ai_response}\n")