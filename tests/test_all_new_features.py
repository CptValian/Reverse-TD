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

        # Both wall sections have their own HP (750 each now)
        self.assertEqual(w1.hp, 750)
        self.assertEqual(w2.hp, 750)

        w1.take_damage(50)
        self.assertEqual(w1.hp, 700)
        self.assertEqual(w2.hp, 750)

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
        # AI Level 1 (can build defenses & top intelligence)
        ai_l1 = AIController(1, config.FACTION_ALIEN, difficulty=1)
        self.assertEqual(ai_l1.config["can_build_defenses"], True)

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
        for proj in list(self.game_state.projectiles):
            proj.update(1.0, self.game_state)
        self.assertLess(enemy.hp, enemy.max_hp)

    def test_worker_repair(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 100, 100)
        bld.hp = 200
        worker = Unit(0, config.FACTION_HUMAN, "Worker", 100, 100)
        self.game_state.resources_player[0] = {"wood": 100, "gold": 100}

        worker.repair_building(bld)
        worker.update(2.0, self.game_state)

        self.assertGreater(bld.hp, 200)

    def test_building_construction_hp_progression(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 100, 100, is_constructed=False)
        self.assertEqual(bld.hp, int(bld.max_hp * 0.10))

        # Advance construction
        bld.build_progress(bld.total_build_time * 0.5)
        self.assertGreater(bld.hp, int(bld.max_hp * 0.10))

        bld.build_progress(bld.total_build_time * 0.6)
        self.assertEqual(bld.hp, bld.max_hp)
        self.assertTrue(bld.is_constructed)

    def test_moulin_food_stockpile(self):
        moulin = Building(0, config.FACTION_HUMAN, "FoodStockpile", 200, 200)
        self.assertEqual(moulin.building_type, "FoodStockpile")

        worker = Unit(0, config.FACTION_HUMAN, "Worker", 200, 200)
        worker.carried_resource = 10
        worker.resource_type = "food"

        deposit = worker._find_nearest_deposit(self.game_state)
        self.game_state.buildings.append(moulin)
        deposit = worker._find_nearest_deposit(self.game_state)
        self.assertEqual(deposit, moulin)

    def test_command_queueing_and_alien_swarmer_morph(self):
        drone = Unit(1, config.FACTION_ALIEN, "Drone", 300, 300)
        pool = Building(1, config.FACTION_ALIEN, "SpawningPool", 300, 300, is_constructed=False)

        drone.command_queue.append({"type": "construct", "target": pool})
        drone.pop_next_command(self.game_state)

        drone.update(0.1, self.game_state)
        # Drone morphs (dies) and sets building under construction
        self.assertFalse(drone.alive)
        self.assertTrue(getattr(pool, 'is_being_built', False))

    def test_pathfinding_grid(self):
        from src.engine.pathfinding import PathfindingGrid
        grid = PathfindingGrid()
        path = grid.find_path((100, 100), (500, 500), self.game_state)
        self.assertTrue(len(path) >= 1)

    def test_projectile_and_options_fog_setting(self):
        from src.entities.projectile import Projectile
        proj = Projectile(100, 100, None, 10)
        self.assertEqual(proj.selected, False)
        self.assertEqual(proj.is_point_inside(100, 100), False)

        # Test fog of war setting toggle
        self.save_manager.set_setting("disable_fog_of_war", True)
        self.assertFalse(self.game_state.is_fog_of_war_enabled())
        self.save_manager.set_setting("disable_fog_of_war", False)

    def test_ai_autobuilding_structures(self):
        ai_bld = Building(1, config.FACTION_ALIEN, "SpawningPool", 400, 400, is_constructed=False)
        self.assertFalse(ai_bld.is_constructed)
        ai_bld.update(ai_bld.total_build_time + 1.0, self.game_state)
        self.assertTrue(ai_bld.is_constructed)

if __name__ == '__main__':
    unittest.main()
