import unittest
import os
import pygame
from src.progression.save_manager import SaveManager
from src.engine.game_state import GameState

class TestIntegrationHeadless(unittest.TestCase):
    def setUp(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
        self.test_save = "test_integration_save.json"
        if os.path.exists(self.test_save):
            os.remove(self.test_save)
        self.sm = SaveManager(filepath=self.test_save)

    def tearDown(self):
        if os.path.exists(self.test_save):
            os.remove(self.test_save)

    def test_full_game_simulation_loop(self):
        gs = GameState(self.sm, num_ais=1, ai_difficulty="Très Facile")
        gs.start_new_game()

        self.assertEqual(gs.state, "PLAYING")
        self.assertGreater(len(gs.units), 0)
        self.assertGreater(len(gs.buildings), 0)

        # Simuler 100 ticks de mise à jour du jeu
        for _ in range(100):
            gs.update(0.1)

        # Vérifier qu'aucune exception n'est survenue
        self.assertIn(gs.state, ["PLAYING", "VICTORY", "DEFEAT"])

if __name__ == '__main__':
    unittest.main()
