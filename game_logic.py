import random
from typing import Dict, Any

class GameReferee:
    """
    Deterministic State Machine for Rock-Paper-Scissors-Plus.
    Acts as the 'Tool' implementation for the AI Agent.
    """

    def __init__(self):
        # Game State
        self.round_num = 1
        self.max_rounds = 3
        
        # State Persistence: Tracking scores and one-time abilities
        self.scores = {"user": 0, "bot": 0}
        self.flags = {
            "user_bomb_used": False,
            "bot_bomb_used": False
        }
        
        self.game_over = False
        self.final_result = None

    def _get_bot_move(self) -> str:
        """
        Internal: Generates a fair move for the bot.
        """
        options = ["rock", "paper", "scissors"]
        
        # Strategy: 10% chance to use Bomb if still available
        if not self.flags["bot_bomb_used"]:
             if random.random() < 0.1: 
                 return "bomb"
        
        return random.choice(options)

    def play_round(self, user_move: str) -> Dict[str, Any]:
        """
        The Main Tool Contract.
        Validates rules, updates state, and resolves the round.
        """
        # Guard clause to prevent extra turns
        if self.game_over:
            return {"error": "Game is already over.", "game_over": True}

        # Normalize input to prevent case/whitespace issues
        move = user_move.lower().strip()
        bot_move = self._get_bot_move()
        
        valid_moves = ["rock", "paper", "scissors", "bomb"]
        outcome = ""
        explanation = ""
        
        # --- Logic & Validation ---
        
        # Rule: Invalid input wastes the round (no score, but round counts)
        if move not in valid_moves:
            outcome = "wasted"
            explanation = f"'{user_move}' is invalid! Round wasted."
            bot_move = "n/a"

        # Rule: Bomb can be used only once per player
        elif move == "bomb" and self.flags["user_bomb_used"]:
            outcome = "wasted"
            explanation = "Bomb already used! Round wasted."
            bot_move = "n/a"

        # Valid Move Execution
        else:
            # Mark one-time flags
            if move == "bomb":
                self.flags["user_bomb_used"] = True
            if bot_move == "bomb":
                self.flags["bot_bomb_used"] = True

            # Resolution Logic
            if move == bot_move:
                outcome = "draw"
                explanation = f"Both chose {move}. Draw."
            elif move == "bomb":
                outcome = "user"
                explanation = "BOMB beats everything! You win."
            elif bot_move == "bomb":
                outcome = "bot"
                explanation = "Bot dropped a BOMB! You lose."
            elif (move == "rock" and bot_move == "scissors") or \
                 (move == "paper" and bot_move == "rock") or \
                 (move == "scissors" and bot_move == "paper"):
                outcome = "user"
                explanation = f"{move.title()} beats {bot_move}. You win!"
            else:
                outcome = "bot"
                explanation = f"{bot_move.title()} beats {move}. Bot wins!"

        # --- State Mutation ---
        
        if outcome == "user":
            self.scores["user"] += 1
        elif outcome == "bot":
            self.scores["bot"] += 1
        
        # Snapshot state for the Agent response
        response = {
            "round": self.round_num,
            "user_move": move,
            "bot_move": bot_move,
            "outcome": outcome,
            "explanation": explanation,
            "current_scores": self.scores.copy(),
        }

        # Advance Round
        self.round_num += 1
        
        # Check End Condition (Strict 3 rounds)
        if self.round_num > self.max_rounds:
            self.game_over = True
            
            if self.scores["user"] > self.scores["bot"]:
                self.final_result = "User Wins!"
            elif self.scores["bot"] > self.scores["user"]:
                self.final_result = "Bot Wins!"
            else:
                self.final_result = "It's a Draw!"
            
            response["final_result"] = self.final_result
            response["game_over"] = True
        else:
            response["game_over"] = False

        return response