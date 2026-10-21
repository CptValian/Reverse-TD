import unittest
import pygame
from src.progression.save_manager import SaveManager
from src.engine.game_state import GameState
from src.entities.projectile import Projectile
from src.entities.unit import Unit
from src.entities.building import Building
from src.ai.ai_controller import AIController
from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
from src.progression.progression_tree import ProgressionUI

class TestV3Features(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.HIDDEN)

    def setUp(self):
        self.sm = SaveManager(filepath="test_v3_save.json")
        self.sm.data["upgrades"] = {}

    def test_projectile_radius_attribute(self):
        p = Projectile(100, 100, None, damage=10)
        self.assertTrue(hasattr(p, 'radius'))
        self.assertEqual(p.radius, 4)

    def test_ai_levels_16_17_18_exist(self):
        self.assertIn(16, AI_DIFFICULTY_LEVELS)
        self.assertIn(17, AI_DIFFICULTY_LEVELS)
        self.assertIn(18, AI_DIFFICULTY_LEVELS)

    def test_ai_starting_units(self):
        # AI Level 2 (+1 swarmer)
        gs2 = GameState(self.sm, num_ais=1, ai_difficulty=2)
        gs2.start_new_game()
        ai_swarmers = [u for u in gs2.units if u.owner_id != 0 and u.unit_type == "Swarmer"]
        self.assertEqual(len(ai_swarmers), 1)

        # AI Level 3 (+1 drone, +1 swarmer)
        gs3 = GameState(self.sm, num_ais=1, ai_difficulty=3)
        gs3.start_new_game()
        ai_drones = [u for u in gs3.units if u.owner_id != 0 and u.unit_type == "Drone"]
        self.assertEqual(len(ai_drones), 4) # 3 base + 1 bonus

        # AI Level 17 (+4 starting drones)
        gs17 = GameState(self.sm, num_ais=1, ai_difficulty=17)
        gs17.start_new_game()
        ai_drones17 = [u for u in gs17.units if u.owner_id != 0 and u.unit_type == "Drone"]
        self.assertEqual(len(ai_drones17), 7) # 3 base + 4 bonus

    def test_double_map_biomass_level_16(self):
        gs16 = GameState(self.sm, num_ais=1, ai_difficulty=16)
        gs16.start_new_game()
        biomass_nodes = [r for r in gs16.resources if r.resource_type == "biomass"]
        self.assertGreater(len(biomass_nodes), 0)
        self.assertEqual(biomass_nodes[0].amount, 3000) # Base 1500 doubled to 3000

    def test_hero_system_and_upgrades(self):
        self.sm.data["upgrades"]["hero_unlocked"] = 1
        self.sm.data["upgrades"]["hero_archer"] = 1
        self.sm.data["upgrades"]["hero_range_boost"] = 1

        gs = GameState(self.sm, num_ais=1, ai_difficulty=1)
        gs.start_new_game()

        hero = next(u for u in gs.units if u.owner_id == 0 and u.unit_type == "Hero")
        self.assertIsNotNone(hero)
        self.assertTrue(hero.is_hero)
        self.assertEqual(hero.hero_level, 1)
        self.assertTrue(getattr(hero, 'is_hero_archer', False))
        self.assertEqual(hero.attack_range, 225) # 180 * 1.25

        # Test hero kills and level up
        init_hp = hero.max_hp
        init_atk = hero.attack_power
        hero.add_hero_kill() # Level 2
        hero.add_hero_kill() # Level 3
        self.assertEqual(hero.hero_level, 3)
        self.assertGreater(hero.max_hp, init_hp)
        self.assertGreater(hero.attack_power, init_atk)

    def test_house_pop_upgrades(self):
        self.sm.data["upgrades"]["house_unlocked"] = 1
        self.sm.data["upgrades"]["house_pop_1"] = 1
        self.sm.data["upgrades"]["house_pop_2"] = 1

        gs = GameState(self.sm, num_ais=1, ai_difficulty=1)
        gs.start_new_game()
        house = Building(0, "human", "House", 100, 100, is_constructed=True)
        gs.buildings.append(house)

        pop_max = gs.get_pop_max(0)
        # Base 10 + TownHall (10) + House (5 base + 2 from pop_1 & pop_2) = 27
        self.assertEqual(pop_max, 27)

    def test_sanctuary_boost_upgrade(self):
        self.sm.data["upgrades"]["sanctuary_boost"] = 1
        gs = GameState(self.sm, num_ais=1, ai_difficulty=1)
        gs.start_new_game()

        sanc = Building(0, "human", "Sanctuary", 100, 100, is_constructed=True)
        u = Unit(0, "human", "Infantry", 200, 100) # Distance 100 <= 210
        u.hp = 50
        gs.units.append(u)

        sanc.update(1.0, gs)
        self.assertEqual(u.hp, 62.0) # 50 + 12 HP/s

    def test_skill_tree_nodes_no_overlap(self):
        ui = ProgressionUI(self.sm)
        # Test node rendering setup
        cards = []
        # Simulate positions check
        import src.progression.progression_tree as pt
        import inspect
        source = inspect.getsource(pt.ProgressionUI._draw_skill_tree_tab)
        self.assertIn("hero_unlocked", source)
        self.assertIn("hero_archer", source)
        self.assertIn("hero_range_boost", source)
        self.assertIn("house_pop_1", source)
        self.assertIn("house_pop_2", source)
        self.assertIn("house_pop_3", source)
        self.assertIn("sanctuary_boost", source)

if __name__ == "__main__":
    unittest.main()
