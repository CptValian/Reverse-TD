import unittest
import pygame
import config
from src.progression.save_manager import SaveManager
from src.engine.game_state import GameState, Projectile
from src.entities.building import Building, BUILDING_TYPES
from src.entities.unit import Unit, UNIT_TYPES
from src.ai.ai_tech import AI_DIFFICULTY_LEVELS

class TestNewRequirements(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.sm = SaveManager()
        self.gs = GameState(self.sm)

    def test_building_initial_hp_and_wall_hp(self):
        # Wall HP should be 750
        self.assertEqual(BUILDING_TYPES["Wall"]["hp"], 750)

        # Unconstructed building should start at 10% max HP
        b = Building(0, "Medieval", "Barracks", 100, 100, is_constructed=False)
        self.assertEqual(b.hp, int(b.max_hp * 0.10))
        self.assertFalse(b.is_constructed)

        # Progress building
        b.build_progress(b.total_build_time / 2)
        self.assertGreater(b.hp, int(b.max_hp * 0.10))
        self.assertLess(b.hp, b.max_hp)

        b.build_progress(b.total_build_time / 2)
        self.assertTrue(b.is_constructed)
        self.assertEqual(b.hp, b.max_hp)

    def test_drone_sacrifice(self):
        drone = Unit(1, "Alien", "Drone", 100, 100)
        hive_bld = Building(1, "Alien", "SpawningPool", 105, 105, is_constructed=False)
        self.gs.units.append(drone)
        self.gs.buildings.append(hive_bld)

        drone.construct_building(hive_bld)
        # Update drone to reach building
        drone.update(0.1, self.gs)
        self.assertFalse(drone.alive)
        self.assertTrue(hive_bld.auto_building)

        # Hive auto construction
        hive_bld.update(hive_bld.total_build_time + 1, self.gs)
        self.assertTrue(hive_bld.is_constructed)

    def test_bank_and_healing_shrine(self):
        self.gs.resources_player[0] = {"gold": 100, "wood": 100, "food": 100, "biomass": 0}

        bank = Building(0, "Medieval", "Bank", 200, 200, is_constructed=True)
        self.gs.buildings.append(bank)
        bank.update(1.0, self.gs)
        self.assertGreater(self.gs.resources_player[0]["gold"], 100)

        shrine = Building(0, "Medieval", "HealingShrine", 300, 300, is_constructed=True)
        wounded = Unit(0, "Medieval", "Infantry", 320, 320)
        wounded.hp = 50
        self.gs.units.append(wounded)
        self.gs.buildings.append(shrine)

        shrine.update(1.0, self.gs)
        self.assertGreater(wounded.hp, 50)

    def test_watchtower_vs_arrow_tower(self):
        wt = BUILDING_TYPES["Tower"]
        at = BUILDING_TYPES["ArrowTower"]

        # Watchtower has 0 attack and 700 vision
        self.assertEqual(wt["attack_power"], 0)
        self.assertEqual(wt["vision"], 700)

        # Arrow tower has attack power 16 and vision 300
        self.assertEqual(at["attack_power"], 16)
        self.assertEqual(at["vision"], 300)

    def test_projectile_and_queen_kill_transform(self):
        queen = Unit(1, "Alien", "Queen", 100, 100)
        target = Unit(0, "Medieval", "Worker", 200, 200)
        target.hp = 10  # Low HP so Queen projectile kills it

        self.gs.units.extend([queen, target])
        self.gs.spawn_projectile(queen, target, damage=20, proj_type="queen_bolt")

        self.assertEqual(len(self.gs.projectiles), 1)
        proj = self.gs.projectiles[0]

        # Update projectile until impact
        for _ in range(20):
            proj.update(0.1, self.gs)

        self.assertFalse(target.alive)
        # Target killed by queen projectile should spawn a Swarmer
        swarmers = [u for u in self.gs.units if u.unit_type == "Swarmer" and u.owner_id == 1]
        self.assertEqual(len(swarmers), 1)

    def test_ai_level_15_setup(self):
        gs15 = GameState(self.sm, num_ais=1, ai_difficulty=15)
        gs15.start_new_game()

        ai_drones = [u for u in gs15.units if u.owner_id == 1 and u.unit_type == "Drone"]
        self.assertEqual(len(ai_drones), 5)

if __name__ == "__main__":
    unittest.main()
