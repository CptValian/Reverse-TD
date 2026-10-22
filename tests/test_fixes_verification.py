import unittest
import config
from src.entities.unit import Unit
from src.entities.building import Building
from src.entities.resource_node import ResourceNode
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager

class TestNewFixes(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager(filepath="test_save_fixes_tmp.json")
        self.game_state = GameState(self.save_manager)

    def test_teammates_cannot_attack_or_damage_each_other(self):
        self.game_state.teams = {1: 1, 2: 1, 3: 2}  # Players 1 & 2 are Team 1; Player 3 is Team 2

        u1 = Unit(1, config.FACTION_HUMAN, "Infantry", 100, 100)
        u2_ally = Unit(2, config.FACTION_HUMAN, "Infantry", 110, 100)
        u3_enemy = Unit(3, config.FACTION_ALIEN, "Swarmer", 200, 100)

        self.game_state.units.extend([u1, u2_ally, u3_enemy])

        # Verify are_enemies logic
        self.assertFalse(self.game_state.are_enemies(1, 2))
        self.assertTrue(self.game_state.are_enemies(1, 3))

        # Scanner should ignore friendly teammate
        enemy = u1._scan_for_enemy(self.game_state)
        self.assertEqual(enemy, u3_enemy)

        # Teammate damage attempt should be negated
        initial_hp = u2_ally.hp
        u2_ally.take_damage(20, attacker=u1, game_state=self.game_state)
        self.assertEqual(u2_ally.hp, initial_hp)

        # Enemy damage attempt should succeed
        u2_ally.take_damage(20, attacker=u3_enemy, game_state=self.game_state)
        self.assertEqual(u2_ally.hp, initial_hp - 20)

    def test_worker_construction_and_harvesting_no_spinning(self):
        worker = Unit(1, config.FACTION_HUMAN, "Worker", 100, 100)
        bld = Building(1, config.FACTION_HUMAN, "Barracks", 120, 100, is_constructed=False)
        self.game_state.units.append(worker)
        self.game_state.buildings.append(bld)

        worker.construct_building(bld, self.game_state)
        worker.update(0.1, self.game_state)

        # Worker gets in construction range and clears movement path to prevent oscillation loops
        self.assertEqual(worker.state, "construct")
        self.assertEqual(len(worker.path_waypoints), 0)
        self.assertIsNone(worker.target_pos)

if __name__ == '__main__':
    unittest.main()
