#!/usr/bin/env python3
import requests
import os
import pyttsx3
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
history = [
    {"role": "system", "content": "You are a helpful AI assistant. Keep responses concise."}
]

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Optional: Configure voice settings
tts_engine.setProperty('rate', 180)  # Speed of speech
tts_engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)

def speak(text):
    """Convert text to speech"""
    print(f"AI: {text}\n")
    tts_engine.say(text)
    tts_engine.runAndWait()

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ['exit', 'quit', 'q']: 
        speak("Goodbye!")
        break
    
    history.append({"role": "user", "content": user_input})
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "deepseek/deepseek-chat", "messages": history}
    )
    
    ai_response = response.json()['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": ai_response})
    
    # Speak the response instead of just printing
    speak(ai_response)