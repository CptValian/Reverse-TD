import unittest
import os
import config
from src.progression.rewards import Rewards
from src.entities.building import Building
from src.entities.unit import Unit
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_new_save_data.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.sm = SaveManager(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_defeat_reward_survival_time(self):
        # Defeat with 0 survival time gives 0
        rewards_0 = Rewards.calculate_rewards(victory=False, num_ais=1, difficulty=1, survival_time=0)
        self.assertEqual(rewards_0[config.POINT_TYPE_COMMAND], 0)

        # Defeat with max survival time (300s+) gives exactly 1/3 of victory reward
        rewards_vic = Rewards.calculate_rewards(victory=True, num_ais=1, difficulty=1)
        rewards_max_loss = Rewards.calculate_rewards(victory=False, num_ais=1, difficulty=1, survival_time=300)

        expected_command = int(rewards_vic[config.POINT_TYPE_COMMAND] / 3.0)
        self.assertEqual(rewards_max_loss[config.POINT_TYPE_COMMAND], expected_command)

    def test_pop_max_and_houses(self):
        gs = GameState(self.sm)
        # Base pop = 10
        self.assertEqual(gs.get_pop_max(0), 10)

        # Add constructed house (+5 pop)
        house = Building(0, config.FACTION_HUMAN, "House", 100, 100, is_constructed=True)
        gs.buildings.append(house)
        self.assertEqual(gs.get_pop_max(0), 15)

    def test_garrison_and_arrows(self):
        gs = GameState(self.sm)
        th = Building(0, config.FACTION_HUMAN, "TownHall", 100, 100)
        peasant = Unit(0, config.FACTION_HUMAN, "Worker", 100, 100)

        self.assertEqual(th.attack_power, 0)
        self.assertTrue(th.garrison_unit(peasant))
        self.assertEqual(len(th.garrisoned_units), 1)

        released = th.ungarrison_all(gs)
        self.assertEqual(len(released), 1)
        self.assertEqual(len(th.garrisoned_units), 0)

    def test_age_up_building_hp(self):
        gs = GameState(self.sm)
        th = Building(0, config.FACTION_HUMAN, "TownHall", 100, 100)
        gs.buildings.append(th)

        initial_hp = th.max_hp
        gs.age_up(0)
        self.assertEqual(gs.player_age, 2)
        self.assertEqual(th.max_hp, int(initial_hp * 1.2))

if __name__ == "__main__":
    unittest.main()
