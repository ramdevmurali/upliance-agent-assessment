import unittest
from unittest.mock import patch
from game_logic import GameReferee

class TestGameReferee(unittest.TestCase):
    
    def setUp(self):
        """Run before every test: Start a fresh game."""
        self.game = GameReferee()

    @patch('game_logic.random.random') # 1. Mock the Bomb probability
    @patch('game_logic.random.choice') # 2. Mock the Move selection
    def test_rock_beats_scissors(self, mock_choice, mock_random):
        """Test that Rock beats Scissors correctly."""
        # Force random() to be 0.5 (Greater than 0.1, so NO Bomb)
        mock_random.return_value = 0.5
        # Force Bot to play Scissors
        mock_choice.return_value = "scissors"
        
        result = self.game.play_round("rock")
        
        self.assertEqual(result["outcome"], "user")
        self.assertEqual(self.game.scores["user"], 1)

    @patch('game_logic.random.random')
    @patch('game_logic.random.choice')
    def test_draw_condition(self, mock_choice, mock_random):
        """Test that same moves result in a draw."""
        # No Bomb
        mock_random.return_value = 0.5
        # Force Bot to play Rock
        mock_choice.return_value = "rock"
        
        result = self.game.play_round("rock")
        
        self.assertEqual(result["outcome"], "draw")
        self.assertEqual(self.game.scores["user"], 0)

    def test_invalid_input_wastes_round(self):
        """Test that typos waste the round but do not crash."""
        result = self.game.play_round("scissor") # Typo (missing 's')
        
        self.assertEqual(result["outcome"], "wasted")
        self.assertEqual(self.game.round_num, 2) # Round still advances

    @patch('game_logic.random.choice')
    def test_bomb_mechanic(self, mock_choice):
        """Test the Bomb logic and One-Time constraint."""
        # For this test, we don't care about random.random because 
        # we (the user) are playing the bomb, so we win regardless.
        mock_choice.return_value = "rock"

        # 1. Use Bomb for the first time (Valid)
        result1 = self.game.play_round("bomb")
        self.assertEqual(result1["outcome"], "user")
        self.assertTrue(self.game.flags["user_bomb_used"])

        # 2. Try to use Bomb again (Invalid)
        result2 = self.game.play_round("bomb")
        self.assertEqual(result2["outcome"], "wasted")
        self.assertEqual(result2["explanation"], "Bomb already used! Round wasted.")

if __name__ == '__main__':
    unittest.main()