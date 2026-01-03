# AI Game Referee: Rock-Paper-Scissors-Plus

**Candidate:** Ramdev Murali
**Date:** January 3, 2026

---

## 1. Architecture: Brain vs. Body

To solve the challenge of building a reliable referee using a probabilistic LLM, I implemented a strict **"Tool Contract"** architecture that separates intent from logic.

### The Brain: Intent Recognition (Google Gen AI SDK)
The Agent (Gemini) handles the Conversational UX.
*   **Responsibility:** It translates natural language ("Drop a bomb on him!") into structured API calls.
*   **Constraint:** The system prompt explicitly forbids the Agent from calculating results internally. It *must* defer to the tool.

### The Body: Deterministic State Machine (Python)
The `GameReferee` class serves as the Source of Truth.
*   **Responsibility:** It executes the game rules, enforces the "Bomb" constraint, and persists the score.
*   **Mechanism:** Logic is handled via strict Python control flow (`if/else`), ensuring zero hallucinations regarding the score or winner.

---

## 2. State Management Strategy

The assignment required state persistence and strict rule enforcement. I modeled the state explicitly in the backend:

*   **Persistence:** `round_count` and `scores` are stored in the Python instance, persisting across the chat loop.
*   **Constraint Enforcement:** The "Bomb" rule is enforced via a boolean flag (`user_bomb_used`). This is immutable once set, preventing the Agent from "forgetting" that a power-up was consumed.
*   **Input Sanitization:** The logic layer validates moves before execution. If a user inputs "scissor" (singular), the engine catches it and triggers a "Wasted Round" state, preventing the game loop from crashing or proceeding with invalid data.

---

## 3. Operational Guide

### Prerequisites
*   Python 3.10+
*   Google API Key (Gemini Flash tier access)

### Setup & Run
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure API Key:**
    Create a `.env` file: `GOOGLE_API_KEY=AIzaSy...`
3.  **Run the Referee:**
    ```bash
    python3 main.py
    ```

---

## 4. Trade-offs & Future Improvements

### In-Memory State vs. Database
*   **Decision:** State is currently held in Python memory.
*   **Trade-off:** Game progress is lost if the script restarts.
*   **Production View:** In a real-world appliance (like Upliance's hardware), I would persist state in **Redis** keyed by `session_id` to handle device reboots and concurrent users.

### Strict Validation vs. Fuzzy Matching
*   **Decision:** Inputs must match valid moves exactly. Invalid inputs waste a round immediately.
*   **Improvement:** For better UX, I would implement **fuzzy matching** (Levenshtein distance) in the backend to auto-correct minor typos (e.g., `sissors` -> `scissors`) instead of penalizing the user.

### Synchronous Tooling
*   **Decision:** The tool is called synchronously for simplicity.
*   **Improvement:** Converting to `async/await` patterns would allow the agent to handle higher throughput without blocking the event loop.