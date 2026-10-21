import unittest
import math
import config
from src.entities.building import Building
from src.entities.unit import Unit
from src.entities.resource_node import ResourceNode
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager
from src.ai.ai_controller import AIController

class TestAIImprovements(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager(filepath="test_save_ai_tmp.json")
        self.game_state = GameState(self.save_manager)

    def test_building_under_construction_damage_multiplier(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 200, 200, is_constructed=False)
        initial_hp = bld.hp
        # Barracks armor is 0. 10 damage * 2.5 multiplier = 25 damage
        bld.take_damage(10)
        self.assertEqual(bld.hp, initial_hp - 25)

        # Progress construction should not overwrite damage
        bld.build_progress(1.0)
        self.assertEqual(bld.hp, initial_hp - 25 + int(bld.max_hp * 0.90 * (1.0 / bld.total_build_time)))

    def test_under_attack_notification(self):
        ai = AIController(1, config.FACTION_ALIEN, difficulty=18)
        self.game_state.ai_controllers.append(ai)

        bld = Building(1, config.FACTION_ALIEN, "Hive", 100, 100)
        attacker = Unit(0, config.FACTION_HUMAN, "Infantry", 150, 100)
        defender = Unit(1, config.FACTION_ALIEN, "Swarmer", 120, 100)

        self.game_state.buildings.append(bld)
        self.game_state.units.extend([attacker, defender])

        # Base taking damage notifies AI and directs defender to attack
        bld.take_damage(10, attacker=attacker, game_state=self.game_state)
        self.assertEqual(defender.state, "attack")
        self.assertEqual(defender.target_entity, attacker)

    def test_worker_load_balancing_and_anti_stuck(self):
        drone = Unit(1, config.FACTION_ALIEN, "Drone", 100, 100)
        self.game_state.units.append(drone)

        # Simulate stuck drone
        drone.state = "harvest"
        drone.last_pos = (100, 100)
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)

        # After multiple stuck ticks, stuck_timer accumulates
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)

        self.assertGreater(drone.stuck_timer, 0.0)

    def test_iacia_level_18_attack_triggers(self):
        ai = AIController(1, config.FACTION_ALIEN, difficulty=18)
        ai.timer_wave = 15.0  # Force wave timer threshold

        u1 = Unit(1, config.FACTION_ALIEN, "Swarmer", 100, 100)
        u2 = Unit(1, config.FACTION_ALIEN, "Swarmer", 110, 100)
        u3 = Unit(1, config.FACTION_ALIEN, "Swarmer", 120, 100)

        enemy_hive = Building(2, config.FACTION_HUMAN, "TownHall", 800, 800)

        self.game_state.units.extend([u1, u2, u3])
        self.game_state.buildings.append(enemy_hive)
        self.game_state.teams = {1: 1, 2: 2}

        ai.update(0.1, self.game_state)

        # Wave timer forces attack
        self.assertEqual(ai.timer_wave, 0.0)
        self.assertIn(u1.state, ["move", "attack"])

if __name__ == '__main__':
    unittest.main()
