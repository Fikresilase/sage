from pathlib import Path

def get_API_key():
    """
    Ask the user for their Gemini API key and store it in the project's .env file as SAGE_GEMINI_API_KEY
    """
    api_key = input("Enter your Gemini API key: ").strip()
    if not api_key:
        print("No API key entered. Skipping.")
        return

    env_file = Path(".env")
    env_lines = []

    # Read existing .env if it exists
    if env_file.exists():
        env_lines = env_file.read_text().splitlines()

    # Check if key already exists
    key_exists = False
    for i, line in enumerate(env_lines):
        if line.startswith("SAGE_GEMINI_API_KEY="):
            env_lines[i] = f"SAGE_GEMINI_API_KEY={api_key}"
            key_exists = True
            break

    if not key_exists:
        env_lines.append(f"SAGE_GEMINI_API_KEY={api_key}")

    # Write back to .env
    env_file.write_text("\n".join(env_lines) + "\n")
    print("Gemini API key saved to .env as SAGE_GEMINI_API_KEY ✅")
