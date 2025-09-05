#!/usr/bin/env python3
import requests
import os
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
history = [
    {"role": "system", "content": "You are a helpful AI assistant. Keep responses concise."}
]

# Initialize text-to-speech
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 180)
tts_engine.setProperty('volume', 0.8)

# Initialize speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

def speak(text):
    """Convert text to speech"""
    print(f"AI: {text}\n")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    """Listen for voice input"""
    print("🎤 Listening... (speak now)")
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    
    except sr.WaitTimeoutError:
        print("⏰ No speech detected")
        return None
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_input():
    """Get input from user via voice or text"""
    print("\nChoose input method:")
    print("1. 🎤 Voice (press 1 or say 'voice')")
    print("2. ⌨️  Text (press 2 or say 'text')")
    print("3. 🚪 Exit (press 3 or say 'exit')")
    
    try:
        choice = input("Your choice (1/2/3): ").strip().lower()
        
        if choice in ['1', 'voice', 'v']:
            user_input = listen()
            if user_input:
                return user_input
            else:
                print("Switching to text input...")
                return get_text_input()
        
        elif choice in ['2', 'text', 't', '']:
            return get_text_input()
        
        elif choice in ['3', 'exit', 'quit', 'q']:
            return 'exit'
        
        else:
            print("Invalid choice, using text input...")
            return get_text_input()
            
    except KeyboardInterrupt:
        return 'exit'

def get_text_input():
    """Get text input from user"""
    return input("You (text): ").strip()

def chat_with_ai(user_input):
    """Send message to AI and get response"""
    history.append({"role": "user", "content": user_input})
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "deepseek/deepseek-chat", "messages": history}
    )
    
    ai_response = response.json()['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": ai_response})
    
    return ai_response

def main():
    print("🎤🤖 Voice & Text Chatbot Activated!")
    print("=====================================")
    
    while True:
        user_input = get_input()
        
        if not user_input:
            continue
            
        if user_input == 'exit':
            speak("Goodbye! It was nice talking with you!")
            break
        
        # Process the input
        if user_input in ['clear', 'reset']:
            history.clear()
            history.append({"role": "system", "content": "You are a helpful AI assistant."})
            speak("Conversation cleared!")
            continue
        
        print(f"💭 Processing: {user_input}")
        ai_response = chat_with_ai(user_input)
        speak(ai_response)

if __name__ == "__main__":
    main()