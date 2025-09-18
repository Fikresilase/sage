from pathlib import Path

def get_API_key():
    """
    Ask the user for their Gemini API key and store it in the project's .env file as SAGE_GEMINI_API_KEY.
    If the key already exists, skip asking.
    """
    env_file = Path(".env")
    env_lines = []

    # Read existing .env if it exists
    if env_file.exists():
        env_lines = env_file.read_text().splitlines()
        # Check if key already exists
        for line in env_lines:
            if line.startswith("SAGE_GEMINI_API_KEY="):
                print("Gemini API key already exists in .env ✅")
                return

    # Ask user for API key
    api_key = input("Enter your Gemini API key: ").strip()
    if not api_key:
        print("No API key entered. Skipping.")
        return

    # Append the key to .env
    env_lines.append(f"SAGE_GEMINI_API_KEY={api_key}")
    env_file.write_text("\n".join(env_lines) + "\n")
    print("Gemini API key saved to .env as SAGE_GEMINI_API_KEY ✅")
