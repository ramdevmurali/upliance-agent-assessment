import random
import difflib  # <--- Added Standard Library for Fuzzy Matching
from typing import Dict, Any

class GameReferee:
    """
    Deterministic State Machine for Rock-Paper-Scissors-Plus.
    Acts as the 'Tool' implementation for the AI Agent.
    """

    def __init__(self):
        self.round_num = 1
        self.max_rounds = 3
        self.scores = {"user": 0, "bot": 0}
        self.flags = {
            "user_bomb_used": False,
            "bot_bomb_used": False
        }
        self.game_over = False
        self.final_result = None

    def _get_bot_move(self) -> str:
        """Internal: Generates a fair move for the bot."""
        options = ["rock", "paper", "scissors"]
        if not self.flags["bot_bomb_used"]:
             if random.random() < 0.1: 
                 return "bomb"
        return random.choice(options)

    def play_round(self, user_move: str) -> Dict[str, Any]:
        """
        The Main Tool Contract.
        Validates rules, updates state, and resolves the round.
        """
        if self.game_over:
            return {"error": "Game is already over.", "game_over": True}

        # 1. Normalize Input
        raw_move = user_move.lower().strip()
        valid_moves = ["rock", "paper", "scissors", "bomb"]
        
        # --- FUZZY MATCHING LOGIC ---
        # If the move isn't perfect, try to find a close match (e.g. "sissors" -> "scissors")
        # cutoff=0.6 means "60% similar"
        matches = difflib.get_close_matches(raw_move, valid_moves, n=1, cutoff=0.6)
        
        if raw_move in valid_moves:
            move = raw_move
            was_corrected = False
        elif matches:
            move = matches[0]
            was_corrected = True
        else:
            move = raw_move # Keep original invalid text to show error
            was_corrected = False
        # -----------------------------

        bot_move = self._get_bot_move()
        outcome = ""
        explanation = ""
        
        # 2. Logic & Validation
        
        if move not in valid_moves:
            outcome = "wasted"
            explanation = f"'{user_move}' is invalid! Round wasted."
            bot_move = "n/a"

        elif move == "bomb" and self.flags["user_bomb_used"]:
            outcome = "wasted"
            explanation = "Bomb already used! Round wasted."
            bot_move = "n/a"

        else:
            # Valid Move Execution
            if move == "bomb":
                self.flags["user_bomb_used"] = True
            if bot_move == "bomb":
                self.flags["bot_bomb_used"] = True

            # Add a UX note if we auto-corrected
            correction_note = f"(Auto-corrected '{raw_move}' to '{move}'). " if was_corrected else ""

            if move == bot_move:
                outcome = "draw"
                explanation = f"{correction_note}Both chose {move}. Draw."
            elif move == "bomb":
                outcome = "user"
                explanation = f"{correction_note}BOMB beats everything! You win."
            elif bot_move == "bomb":
                outcome = "bot"
                explanation = f"{correction_note}Bot dropped a BOMB! You lose."
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

        self.round_num += 1
        
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