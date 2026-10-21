import unittest
import config
from src.progression.save_manager import SaveManager
from src.engine.game_state import GameState
from src.ai.ai_controller import AIController, MedievalAIController, AlienAIController
from src.entities.unit import Unit
from src.entities.building import Building

class TestNewRequirements(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager("test_save_data.json")
        self.game_state = GameState(self.save_manager)

    def test_ai_controller_factory(self):
        medieval_ai = AIController(owner_id=1, faction=config.FACTION_HUMAN, difficulty=5)
        alien_ai = AIController(owner_id=2, faction=config.FACTION_ALIEN, difficulty=5)

        self.assertIsInstance(medieval_ai, MedievalAIController)
        self.assertIsInstance(alien_ai, AlienAIController)

    def test_flexible_iacia_teams(self):
        # Configure arbitrary 1v1v2 setup (3 teams, 4 AIs)
        self.game_state.iacia_config["ai_players"] = [
            {"id": 1, "team": 1, "difficulty": 5, "faction": config.FACTION_HUMAN},
            {"id": 2, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
            {"id": 3, "team": 3, "difficulty": 5, "faction": config.FACTION_HUMAN},
            {"id": 4, "team": 3, "difficulty": 5, "faction": config.FACTION_ALIEN},
        ]
        self.game_state.start_new_game(is_iacia=True)

        self.assertTrue(self.game_state.are_enemies(1, 2))
        self.assertTrue(self.game_state.are_enemies(1, 3))
        self.assertFalse(self.game_state.are_enemies(3, 4)) # Allies

    def test_medieval_map_spawns(self):
        self.game_state.iacia_config["ai_players"] = [
            {"id": 1, "team": 1, "difficulty": 5, "faction": config.FACTION_HUMAN},
            {"id": 2, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
        ]
        self.game_state.start_new_game(is_iacia=True)

        med_base = next(b for b in self.game_state.buildings if b.owner_id == 1)
        alien_base = next(b for b in self.game_state.buildings if b.owner_id == 2)

        # Check nearby resource types
        med_res = [r for r in self.game_state.resources if r.distance_to(med_base) < 400]
        med_types = {r.resource_type for r in med_res}

        alien_res = [r for r in self.game_state.resources if r.distance_to(alien_base) < 400]
        alien_types = {r.resource_type for r in alien_res}

        self.assertIn("gold", med_types)
        self.assertIn("wood", med_types)
        self.assertIn("food", med_types)
        self.assertIn("biomass", alien_types)

if __name__ == "__main__":
    unittest.main()
