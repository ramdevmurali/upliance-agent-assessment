# AI Game Referee: Rock-Paper-Scissors-Plus

**Candidate:** Ramdev Murali
**Date:** January 3, 2026

---

## 1. Architecture: Brain vs. Body

To build a reliable referee using a probabilistic LLM, I implemented a strict **"Tool Contract"** architecture that separates intent from logic.

### The Brain: Intent Recognition (Google Gen AI SDK)
The Agent (Gemini) handles the Conversational UX.
*   **Responsibility:** It translates natural language ("Drop a bomb on him!", "I choose rock") into structured API calls.
*   **Constraint:** The system prompt explicitly forbids the Agent from calculating results internally. It must defer to the tool for the source of truth.

### The Body: Deterministic State Machine (Python)
The `GameReferee` class serves as the strict Logic Engine.
*   **Responsibility:** It executes the game rules, enforces the "Bomb" constraint, and persists the score.
*   **Mechanism:** Logic is handled via strict Python control flow (if/else), ensuring zero hallucinations regarding the score or winner.

### Tool Contract (Technical Specification)
The agent interacts with the logic engine via a structured JSON bridge. This ensures strict data types and prevents the LLM from hallucinating game states or scores.

**Interface Schema:**
- **Function:** `play_round(user_move: string)`
- **Returns:**
  ```json
  {
    "round": "int",
    "user_move": "string",
    "bot_move": "string",
    "outcome": "user | bot | draw | wasted",
    "current_scores": {"user": "int", "bot": "int"},
    "game_over": "bool"
  }
---


## 2. State Management Strategy

The assignment required state persistence and strict rule enforcement. I modeled the state explicitly in the backend:

*   **Persistence:** `round_num` and `scores` are stored in the Python instance, persisting across the chat session.
*   **Constraint Enforcement:** The "Bomb" rule is enforced via a boolean flag (`user_bomb_used`). This is immutable once set, preventing the Agent from "forgetting" that a power-up was consumed.
*   **Input Resilience (Fuzzy Matching):** I implemented `difflib` (standard library) to handle minor user typos (e.g., "sissors" -> "scissors"). This ensures a smooth conversational flow without compromising the strict logic engine.

---

## 3. Engineering Rigor: Unit Testing

I have included a dedicated test suite (`test_game_logic.py`) to verify the state machine's correctness independent of the AI.

**Why Testing Matters Here:**
Because the Bot has a random 10% chance to throw a "Bomb," the logic is non-deterministic. I utilized `unittest.mock` to patch the random number generator, ensuring the tests are reliable and repeatable.

*   **Mocking Randomness:** Tests force the bot to play specific moves to verify win/loss conditions.
*   **Fuzzy Logic Verification:** A specific test case verifies that typos are correctly auto-resolved to the nearest valid move.
*   **Edge Case Verification:** Tests ensure that illegal moves (like double-bombing) trigger "Wasted Round" states as per the requirements.

**Run the test suite:**
```bash
python3 test_game_logic.py
```
Expected Output: Ran 4 tests ... OK


---

## 4. Operational Guide

### Prerequisites
*   Python 3.10+
*   Google API Key (Gemini Flash tier access)

### Setup & Run
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ramdevmurali/upliance-agent-assessment.git
    cd upliance-agent-assessment
    ```

2.  **Install Dependencies:**
    ```bash
    # It is recommended to use a virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

4.  **Run the Referee:**
    ```bash
    python3 main.py
    ```

---

## 5. Trade-offs & Future Improvements

### In-Memory State vs. Distributed Cache
*   **Decision:** State is currently held in Python memory.
*   **Trade-off:** Game progress is lost if the script restarts or the session disconnects.
*   **Production View:** For a production appliance, I would persist state in **Redis** keyed by a `session_id`. This allows the AI service to remain stateless and resilient to reboots or network interruptions.

### Intent Matching: Fuzzy Logic vs. Semantic Search
*   **Decision:** I utilized `difflib` for lightweight fuzzy matching of move keywords.
*   **Reasoning:** This is highly efficient for a small set of valid moves. For a more complex product (e.g., a recipe database), I would transition to **Semantic Similarity** using vector embeddings to understand the "meaning" of user requests rather than just spelling.

### High Concurrency
*   **Decision:** The application runs in a synchronous CLI loop.
*   **Improvement:** In a real-world deployment, the tool execution would be converted to **Asynchronous (async/await)** patterns to handle thousands of concurrent kitchen device sessions without blocking the event loop.