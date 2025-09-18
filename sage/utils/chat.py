from sage.APIs.gemini import get_gemini_response

def chat():
    print("💬 Sage Gemini Chat (type 'exit' to quit)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye 👋")
            break

        try:
            response = get_gemini_response(user_input)
            print(f"Sage: {response}\n")
        except Exception as e:
            print(f"⚠️ Error: {e}")
