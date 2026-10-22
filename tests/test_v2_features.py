import unittest
import math
import config
from src.entities.building import Building, BUILDING_TYPES
from src.entities.unit import Unit, UNIT_TYPES
from src.entities.projectile import Projectile
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager
from src.ai.ai_controller import AIController

class TestV2Features(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager(filepath="test_save_v2_tmp.json")
        self.game_state = GameState(self.save_manager)

    def test_queen_kill_transforms_to_swarmer(self):
        queen = Unit(1, config.FACTION_ALIEN, "Queen", 100, 100)
        enemy = Unit(0, config.FACTION_HUMAN, "Worker", 120, 100)
        enemy.hp = 10  # Low HP so Queen attack kills it
        self.game_state.units.extend([queen, enemy])

        queen.attack_target(enemy, self.game_state)
        queen.update(1.1, self.game_state)

        # Update projectiles
        for p in list(self.game_state.projectiles):
            p.update(1.0, self.game_state)

        # Enemy should be dead and a new Swarmer should be created for owner_id 1
        self.assertFalse(enemy.alive)
        swarmers = [u for u in self.game_state.units if u.alive and u.unit_type == "Swarmer" and u.owner_id == 1]
        self.assertEqual(len(swarmers), 1)

    def test_bank_passive_gold_generation(self):
        bank = Building(0, config.FACTION_HUMAN, "Bank", 200, 200)
        self.game_state.buildings.append(bank)
        self.game_state.resources_player[0] = {"gold": 100}

        bank.update(1.0, self.game_state)
        self.assertGreater(self.game_state.resources_player[0]["gold"], 100)

    def test_sanctuary_unit_healing(self):
        sanctuary = Building(0, config.FACTION_HUMAN, "Sanctuary", 200, 200)
        injured_unit = Unit(0, config.FACTION_HUMAN, "Infantry", 220, 200)
        injured_unit.hp = 50  # Injured (max HP 150)
        self.game_state.buildings.append(sanctuary)
        self.game_state.units.append(injured_unit)

        sanctuary.update(1.0, self.game_state)
        self.assertGreater(injured_unit.hp, 50)

    def test_spawn_speed_upgrades(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 200, 200)
        self.save_manager.data["upgrades"]["melee_spawn_speed"] = 1

        bld.queue_unit("Infantry", game_state=self.game_state)
        item = bld.production_queue[0]
        base_time = UNIT_TYPES["Infantry"]["train_time"]
        self.assertAlmostEqual(item["total_time"], base_time * 0.90, places=2)

    def test_starting_resources_and_scout_upgrade(self):
        self.save_manager.data["upgrades"]["high_starting_res"] = 1
        self.save_manager.data["upgrades"]["start_with_scout"] = 1

        self.game_state.start_new_game()
        player_res = self.game_state.resources_player[0]

        # 200 base + 100 high_starting_res = 300
        self.assertEqual(player_res["gold"], 300)
        self.assertEqual(player_res["wood"], 300)

        # Scout unit should be present
        scouts = [u for u in self.game_state.units if u.owner_id == 0 and u.unit_type == "Scout"]
        self.assertEqual(len(scouts), 1)

    def test_watchtower_vs_arrowtower(self):
        wt = Building(0, config.FACTION_HUMAN, "WatchTower", 100, 100)
        at = Building(0, config.FACTION_HUMAN, "ArrowTower", 200, 200)

        self.assertEqual(wt.attack_power, 0)
        self.assertEqual(wt.vision_radius, 750)

        self.assertGreater(at.attack_power, 0)
        self.assertEqual(at.attack_range, 260)

    def test_ai_level_15_starting_drones(self):
        gs = GameState(self.save_manager, num_ais=1, ai_difficulty=15)
        gs.start_new_game()

        ai_drones = [u for u in gs.units if u.owner_id == 1 and u.unit_type == "Drone"]
        self.assertEqual(len(ai_drones), 5)

if __name__ == '__main__':
    unittest.main()
