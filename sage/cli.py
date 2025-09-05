#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
history = [{"role": "system", "content": "You are a helpful AI assistant."}]

def chat_with_ai(user_input):
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
    print("🤖 AI Chatbot (Text Mode)")
    print("========================")
    print("Type 'exit' to quit, 'clear' to reset conversation")
    print("-" * 40)
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
            
        if user_input.lower() in ['clear', 'reset']:
            history.clear()
            history.append({"role": "system", "content": "You are a helpful AI assistant."})
            print("Conversation cleared!")
            continue
            
        if not user_input:
            continue
            
        ai_response = chat_with_ai(user_input)
        print(f"AI: {ai_response}\n")

if __name__ == "__main__":
    main()