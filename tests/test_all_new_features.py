import unittest
import math
from src.entities.building import Building, BUILDING_TYPES
from src.entities.unit import Unit, UNIT_TYPES
from src.entities.resource_node import ResourceNode
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager
from src.ai.ai_controller import AIController
import config

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager(filepath="test_save_tmp.json")
        self.game_state = GameState(self.save_manager)

    def test_continuous_wall_sections_and_hp(self):
        w1 = Building(0, config.FACTION_HUMAN, "Wall", 100, 100, wall_length=40, wall_width=20, wall_angle=0.0)
        w2 = Building(0, config.FACTION_HUMAN, "Wall", 138, 100, wall_length=40, wall_width=20, wall_angle=0.0)

        # Both wall sections have their own HP
        self.assertEqual(w1.hp, 250)
        self.assertEqual(w2.hp, 250)

        w1.take_damage(50)
        self.assertEqual(w1.hp, 200)
        self.assertEqual(w2.hp, 250)

        # GameState allows placing adjacent wall sections
        self.game_state.buildings.append(w1)
        self.assertTrue(self.game_state.can_place_building("Wall", 138, 100))

    def test_worker_assisted_construction(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 500, 500, is_constructed=False)
        self.assertFalse(bld.is_constructed)

        # Updating building alone without worker progress does not advance construction
        bld.update(1.0, self.game_state)
        self.assertEqual(bld.build_timer, bld.total_build_time)

        # Worker constructs building
        worker = Unit(0, config.FACTION_HUMAN, "Worker", 500, 500)
        worker.construct_building(bld)
        worker.update(5.0, self.game_state)

        self.assertLess(bld.build_timer, bld.total_build_time)

    def test_ai_tech_gating_and_level_features(self):
        # AI Level 1 (cannot build defenses or spitters)
        ai_l1 = AIController(1, config.FACTION_ALIEN, difficulty=1)
        self.assertEqual(ai_l1.config["can_build_defenses"], False)

        # AI Level 4 (can build Spine Crawler)
        ai_l4 = AIController(1, config.FACTION_ALIEN, difficulty=4)
        self.assertEqual(ai_l4.config["can_build_defenses"], True)

        # AI Level 10 (can build Biomass Generator)
        ai_l10 = AIController(1, config.FACTION_ALIEN, difficulty=10)
        self.assertTrue(ai_l10.config.get("can_build_biomass_gen"))

    def test_scout_unit_stats(self):
        scout = Unit(0, config.FACTION_HUMAN, "Scout", 100, 100)
        self.assertEqual(scout.speed, 140)
        self.assertEqual(scout.vision_radius, 400)

    def test_forum_passive_arrow(self):
        forum = Building(0, config.FACTION_HUMAN, "TownHall", 200, 200)

        # Without garrisoned peasants and without upgrade, attack power is 0
        self.save_manager.data["upgrades"]["forum_passive_arrow"] = 0
        self.assertEqual(len(forum.garrisoned_units), 0)

        # Enable upgrade
        self.save_manager.data["upgrades"]["forum_passive_arrow"] = 1
        # In update(), effective_attack calculates (0 + 1) * 12 = 12
        enemy = Unit(1, config.FACTION_ALIEN, "Swarmer", 220, 200)
        self.game_state.units.append(enemy)
        self.game_state.buildings.append(forum)

        forum.update(1.1, self.game_state)
        self.assertLess(enemy.hp, enemy.max_hp)

    def test_worker_repair(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 100, 100)
        bld.hp = 200
        worker = Unit(0, config.FACTION_HUMAN, "Worker", 100, 100)
        self.game_state.resources_player[0] = {"wood": 100, "gold": 100}

        worker.repair_building(bld)
        worker.update(2.0, self.game_state)

        self.assertGreater(bld.hp, 200)

if __name__ == '__main__':
    unittest.main()
