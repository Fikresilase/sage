#!/usr/bin/env python3
import requests
import json
import os
import requests
import sys
from dotenv import load_dotenv  
load_dotenv()  # Load environment variables from .env file
class DeepSeekChatbot:
    def __init__(self):
        self.api_key = self.get_api_key()
        self.conversation_history = []
        self.model = "deepseek/deepseek-chat"  # You can change this to other models
        
    def get_api_key(self):
        """Get API key from environment variable or prompt user"""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("🔑 OpenRouter API Key not found in environment variables.")
            api_key = input("Please enter your OpenRouter API key: ").strip()
            # Optional: Save to environment for future use
            os.environ["OPENROUTER_API_KEY"] = api_key
        return api_key
    
    def send_message(self, message):
        """Send message to DeepSeek via OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-username/cli-chatbot",
            "X-Title": "CLI Chatbot"
        }
        
        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result['choices'][0]['message']['content']
            
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            return f"❌ API Error: {str(e)}"
        except KeyError:
            return "❌ Unexpected response format from API"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("🤖 DeepSeek CLI Chatbot activated!")
        print("💬 Type your messages to chat with DeepSeek AI")
        print("🔄 Type '/clear' to clear conversation history")
        print("🚪 Type '/exit', '/quit', or '/q' to end the session")
        print("🔧 Type '/model' to see current model")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['/exit', '/quit', '/q']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                elif user_input.lower() == '/clear':
                    self.conversation_history = []
                    print("🗑️ Conversation history cleared!")
                    continue
                
                elif user_input.lower() == '/model':
                    print(f"🤖 Current model: {self.model}")
                    continue
                
                # Send message to API
                print("🤖 Thinking...", end="\r")
                response = self.send_message(user_input)
                
                # Clear the "Thinking..." message and print response
                print(" " * 50, end="\r")  # Clear line
                print(f"AI: {response}")
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print("\n👋 Session ended by user. Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break

def main():
    # Check if API key is available or can be obtained
    try:
        chatbot = DeepSeekChatbot()
        chatbot.start_chat()
    except Exception as e:
        print(f"❌ Failed to start chatbot: {e}")

if __name__ == '__main__':
    main()