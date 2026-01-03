import random
import difflib
from typing import Dict, Any

class GameReferee:
    """
    Deterministic State Machine for Rock-Paper-Scissors-Plus.
    This class handles all state persistence and rule enforcement, 
    acting as the 'Body' for the AI Agent.
    """

    def __init__(self):
        # Game State Initialization
        self.round_num = 1
        self.max_rounds = 3
        self.scores = {"user": 0, "bot": 0}
        
        # Logic Constraints (Flags)
        self.flags = {
            "user_bomb_used": False,
            "bot_bomb_used": False
        }
        
        self.game_over = False
        self.final_result = None

    def validate_move(self, user_input: str):
        """
        Normalizes input and applies fuzzy matching via difflib.
        Returns: (move, is_valid, was_corrected)
        """
        raw = user_input.lower().strip()
        valid_moves = ["rock", "paper", "scissors", "bomb"]
        
        # Check for near matches (e.g., 'sissors' -> 'scissors')
        matches = difflib.get_close_matches(raw, valid_moves, n=1, cutoff=0.6)
        
        if raw in valid_moves:
            return raw, True, False
        elif matches:
            return matches[0], True, True
        return raw, False, False

    def _get_bot_move(self) -> str:
        """
        Internal: Decides the bot's move. 
        Respects the 'Once per game' bomb constraint.
        """
        options = ["rock", "paper", "scissors"]
        
        # 10% chance for Bot to use its Bomb if still available
        if not self.flags["bot_bomb_used"]:
             if random.random() < 0.1: 
                 return "bomb"
        
        return random.choice(options)

    def play_round(self, user_move: str) -> Dict[str, Any]:
        """
        Main Tool Entry Point.
        Orchestrates move validation, round resolution, and state updates.
        """
        if self.game_over:
            return {"error": "Game is already over.", "game_over": True}

        # 1. Parsing & Validation
        move, is_valid, was_corrected = self.validate_move(user_move)
        bot_move = self._get_bot_move()
        
        outcome = ""
        explanation = ""
        correction_note = f"(Auto-corrected '{user_move.strip()}' to '{move}'). " if was_corrected else ""

        # 2. Rule Enforcement
        
        # Case A: Invalid Input (Rule: Wastes the round)
        if not is_valid:
            outcome = "wasted"
            explanation = f"'{user_move}' is not a valid move. Round wasted!"
            bot_move = "n/a"

        # Case B: Illegal Bomb Usage (Rule: Once per player)
        elif move == "bomb" and self.flags["user_bomb_used"]:
            outcome = "wasted"
            explanation = "Bomb already used! Round wasted."
            bot_move = "n/a"

        # Case C: Valid Logic Resolution
        else:
            if move == "bomb": self.flags["user_bomb_used"] = True
            if bot_move == "bomb": self.flags["bot_bomb_used"] = True

            if move == bot_move:
                outcome = "draw"
                explanation = f"{correction_note}Both chose {move}. It's a draw."
            elif move == "bomb":
                outcome = "user"
                explanation = f"{correction_note}BOMB beats everything! You win."
            elif bot_move == "bomb":
                outcome = "bot"
                explanation = f"{correction_note}Bot used a BOMB! You lose."
            elif (move == "rock" and bot_move == "scissors") or \
                 (move == "paper" and bot_move == "rock") or \
                 (move == "scissors" and bot_move == "paper"):
                outcome = "user"
                explanation = f"{correction_note}{move.title()} beats {bot_move}. You win!"
            else:
                outcome = "bot"
                explanation = f"{correction_note}{bot_move.title()} beats {move}. Bot wins!"

        # 3. State Mutation
        if outcome == "user":
            self.scores["user"] += 1
        elif outcome == "bot":
            self.scores["bot"] += 1
        
        response = {
            "round": self.round_num,
            "user_move": move,
            "bot_move": bot_move,
            "outcome": outcome,
            "explanation": explanation,
            "current_scores": self.scores.copy(),
        }

        # 4. Progress Round & Check End Game
        self.round_num += 1
        if self.round_num > self.max_rounds:
            self.game_over = True
            if self.scores["user"] > self.scores["bot"]:
                self.final_result = "User Wins the Game!"
            elif self.scores["bot"] > self.scores["user"]:
                self.final_result = "Bot Wins the Game!"
            else:
                self.final_result = "It's a Draw!"
            
            response["final_result"] = self.final_result
            response["game_over"] = True
        else:
            response["game_over"] = False

        return response