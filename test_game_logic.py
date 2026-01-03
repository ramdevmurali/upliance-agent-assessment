import unittest
from unittest.mock import patch
from game_logic import GameReferee

class TestGameReferee(unittest.TestCase):
    
    def setUp(self):
        """Run before every test: Start a fresh game."""
        self.game = GameReferee()

    @patch('game_logic.random.random')
    @patch('game_logic.random.choice')
    def test_rock_beats_scissors(self, mock_choice, mock_random):
        """Test that Rock beats Scissors correctly."""
        mock_random.return_value = 0.5
        mock_choice.return_value = "scissors"
        
        result = self.game.play_round("rock")
        
        self.assertEqual(result["outcome"], "user")
        self.assertEqual(self.game.scores["user"], 1)

    @patch('game_logic.random.random')
    @patch('game_logic.random.choice')
    def test_draw_condition(self, mock_choice, mock_random):
        """Test that same moves result in a draw."""
        mock_random.return_value = 0.5
        mock_choice.return_value = "rock"
        
        result = self.game.play_round("rock")
        
        self.assertEqual(result["outcome"], "draw")

    def test_fuzzy_matching_correction(self):
        """Test that 'sissors' is auto-corrected to 'scissors'."""
        # We don't need to mock random here, we just care about the input correction
        # But we mock choice to ensure the bot plays valid move
        with patch('game_logic.random.choice', return_value="paper"):
            with patch('game_logic.random.random', return_value=0.5):
                # INTENTIONAL TYPO BELOW: "sissors"
                result = self.game.play_round("sissors") 
                
                # Verify it was fixed
                self.assertEqual(result["user_move"], "scissors")
                self.assertIn("Auto-corrected", result["explanation"])

    @patch('game_logic.random.choice')
    def test_bomb_mechanic(self, mock_choice):
        """Test the Bomb logic."""
        mock_choice.return_value = "rock"
        result1 = self.game.play_round("bomb")
        self.assertEqual(result1["outcome"], "user")

if __name__ == '__main__':
    unittest.main()