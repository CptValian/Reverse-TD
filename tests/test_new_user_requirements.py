import unittest
import math
import config
from src.entities.building import Building, BUILDING_TYPES
from src.entities.unit import Unit, UNIT_TYPES
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager
from src.ai.ai_controller import BaseAIController

class TestNewUserRequirements(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager(filepath="test_save_user_reqs.json")
        self.game_state = GameState(self.save_manager)

    def test_human_playing_alien(self):
        self.game_state.start_new_game(player_faction=config.FACTION_ALIEN)
        self.assertEqual(self.game_state.player_faction, config.FACTION_ALIEN)

        # Check player 0 base is Hive and worker is Drone
        p0_bases = [b for b in self.game_state.buildings if b.owner_id == 0]
        p0_units = [u for u in self.game_state.units if u.owner_id == 0]

        self.assertTrue(any(b.building_type == "Hive" for b in p0_bases))
        self.assertTrue(any(u.unit_type == "Drone" for u in p0_units))

        # Check AI opponent is Medieval
        ai_bases = [b for b in self.game_state.buildings if b.owner_id != 0]
        self.assertTrue(any(b.building_type == "TownHall" for b in ai_bases))

    def test_monk_healing_beam(self):
        monk = Unit(0, config.FACTION_HUMAN, "Monk", 100, 100)
        injured_soldier = Unit(0, config.FACTION_HUMAN, "Infantry", 120, 100)
        injured_soldier.hp = 50  # Injured (max 150)
        self.game_state.units.extend([monk, injured_soldier])

        monk.update(1.0, self.game_state)
        # Monk should heal injured soldier (+2 HP/s)
        self.assertAlmostEqual(injured_soldier.hp, 52.0, places=1)

    def test_tower_damage_and_projectile(self):
        at = BUILDING_TYPES["ArrowTower"]
        sc = BUILDING_TYPES["SpineCrawler"]
        self.assertEqual(at["attack_power"], 20)
        self.assertEqual(sc["attack_power"], 24)

    def test_starting_cache_3_and_near_base_boost(self):
        self.save_manager.data["upgrades"]["starting_res_1"] = 1
        self.save_manager.data["upgrades"]["high_starting_res"] = 1
        self.save_manager.data["upgrades"]["starting_cache_3"] = 1
        self.save_manager.data["upgrades"]["near_base_res_boost"] = 1

        self.game_state.start_new_game(player_faction=config.FACTION_HUMAN)
        res_p0 = self.game_state.resources_player[0]

        # 200 base + 100 + 100 + 100 = 500
        self.assertEqual(res_p0["gold"], 500)

        # Check near base resources boosted by x1.5
        p0_base = next(b for b in self.game_state.buildings if b.owner_id == 0)
        near_res = [r for r in self.game_state.resources if math.hypot(r.x - p0_base.x, r.y - p0_base.y) <= 450]
        self.assertTrue(len(near_res) > 0)
        for r in near_res:
            self.assertTrue(r.amount >= 375)  # Standard ~250 * 1.5 = 375

    def test_ai_risk_factor_evaluation(self):
        ai_ctrl = BaseAIController(owner_id=1, faction=config.FACTION_ALIEN)
        # Place heavy enemy army near candidate position
        enemy_army = [Unit(0, config.FACTION_HUMAN, "Infantry", 500, 500) for _ in range(10)]
        self.game_state.units.extend(enemy_army)

        pos = ai_ctrl._find_valid_building_position(self.game_state, "SpawningPool", 500, 500, search_radius=100)
        # Candidate position (500, 500) surrounded by heavy enemy army without friendly defense should be rejected
        if pos:
            dist = math.hypot(pos[0] - 500, pos[1] - 500)
            self.assertGreater(dist, 400)

if __name__ == '__main__':
    unittest.main()
