import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from game_logic import GameReferee

# 1. Load Secrets
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Error: GOOGLE_API_KEY not found in .env file.")

# 2. Initialize the Client
client = genai.Client(api_key=api_key)

# 3. Initialize the Game Engine (State Machine)
game_engine = GameReferee()

# 4. Define the System Instruction
system_prompt = """
You are the Official Referee for a game of Rock-Paper-Scissors-Plus.

RULES TO EXPLAIN (Must be <= 5 lines total):
1. Standard Rules: Rock > Scissors > Paper > Rock.
2. Special Rule: 'Bomb' beats everything but can be used ONLY ONCE per game.
3. Invalid moves or trying to use the Bomb twice results in a WASTED round.
4. The game lasts exactly 3 Rounds.

YOUR BEHAVIOR:
- Start by greeting the user and explaining the rules concisely (under 5 lines).
- When the user makes a move, YOU MUST CALL the 'play_round' tool.
- DO NOT calculate the winner yourself. Trust the tool's output.
- Announce the Round, the Moves, the Winner, and the Current Score based on the tool.
"""

# 5. Create the Chat Session
# 'gemini-flash-latest' points to the best available stable Flash model.
model_name = "gemini-flash-latest"

print("\n" + "="*50)
print(f"🤖 AI REFEREE INITIALIZED ({model_name})")
print("Type 'exit' to stop.")
print("="*50 + "\n")

# Start Chat
chat = client.chats.create(
    model=model_name,
    config=types.GenerateContentConfig(
        tools=[game_engine.play_round], # Pass the Python function directly
        system_instruction=system_prompt,
        temperature=0.7
    )
)

# Trigger the Greeting
try:
    response = chat.send_message("Hello! I am ready to play.")
    print(f"Referee: {response.text}\n")
except Exception as e:
    print(f"⚠️ Connection Error: {e}")
    exit()

# --- 6. The Game Loop (CLI) ---
while True:
    # A. Get User Input
    try:
        user_input = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):
        break

    # B. Handle Exit
    if user_input.lower() in ['exit', 'quit']:
        print("Referee: GG! See you next time.")
        break

    if not user_input:
        continue

    # C. Send to Agent
    try:
        response = chat.send_message(user_input)
        if response.text:
            print(f"Referee: {response.text}")
        else:
            print("Referee: (State updated...)")
            
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # D. Check Game Over
    if game_engine.game_over:
        print("\n" + "="*50)
        print(f"FINAL RESULT: {game_engine.final_result}")
        print("="*50)
        break

    # E. Rate Limit Protection (Keep this to prevent crashing)
    # 10s delay to stay within the "5 requests per minute" free tier.
    print("(Next round loading... ⏳)")
