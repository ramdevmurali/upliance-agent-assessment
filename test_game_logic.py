import unittest
from unittest.mock import patch
from game_logic import GameReferee

class TestGameReferee(unittest.TestCase):
    
    def setUp(self):
        """Initializes a fresh engine for every test."""
        self.game = GameReferee()

    @patch('game_logic.random.choice')
    @patch('game_logic.random.random')
    def test_rock_beats_scissors(self, mock_random, mock_choice):
        """Tests standard win condition."""
        mock_random.return_value = 0.5  # Prevent bot bomb
        mock_choice.return_value = "scissors"
        
        result = self.game.play_round("rock")
        self.assertEqual(result["outcome"], "user")
        self.assertEqual(self.game.scores["user"], 1)

    @patch('game_logic.random.choice')
    @patch('game_logic.random.random')
    def test_draw_condition(self, mock_random, mock_choice):
        """Tests draw logic."""
        mock_random.return_value = 0.5
        mock_choice.return_value = "rock"
        
        result = self.game.play_round("rock")
        self.assertEqual(result["outcome"], "draw")

    def test_fuzzy_matching_logic(self):
        """Tests that typos are handled by difflib."""
        result = self.game.play_round("sissors") # Intentional typo
        self.assertEqual(result["user_move"], "scissors")
        self.assertIn("Auto-corrected", result["explanation"])

    @patch('game_logic.random.choice')
    @patch('game_logic.random.random')
    def test_bomb_mechanic(self, mock_random, mock_choice):
        """Tests bomb logic and one-time constraint deterministically."""
        mock_random.return_value = 0.5  # No bot bomb
        mock_choice.return_value = "rock"

        # First use: Success
        result1 = self.game.play_round("bomb")
        self.assertEqual(result1["outcome"], "user")
        self.assertTrue(self.game.flags["user_bomb_used"])

        # Second use: Wasted Round
        result2 = self.game.play_round("bomb")
        self.assertEqual(result2["outcome"], "wasted")
        self.assertEqual(self.game.round_num, 3) # Round still advanced

if __name__ == '__main__':
    unittest.main()