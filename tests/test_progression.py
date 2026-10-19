import unittest
import os
from src.progression.save_manager import SaveManager
from src.progression.rewards import Rewards
import config

class TestProgression(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_save_data.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.sm = SaveManager(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_buy_upgrade(self):
        self.sm.add_points(command=50, forge=50, architecture=50)
        points = self.sm.get_points()
        self.assertEqual(points["SwarmerBlood"], 50)
        self.assertEqual(points["LandShard"], 50)
        self.assertEqual(points["Pykrite"], 50)

        # Acheter une amélioration de troupe (SwarmerBlood)
        success = self.sm.buy_upgrade("infantry_hp_lvl", "SwarmerBlood", cost_base=10)
        self.assertTrue(success)
        self.assertEqual(self.sm.get_points()["SwarmerBlood"], 40)
        self.assertEqual(self.sm.data["upgrades"]["infantry_hp_lvl"], 1)

        # Débloquer un élément dans l'arbre de compétences (LandShard)
        success_tree = self.sm.buy_upgrade("archer_unlocked", "LandShard", cost=30, is_tree_unlock=True)
        self.assertTrue(success_tree)
        self.assertEqual(self.sm.get_points()["LandShard"], 20)
        self.assertEqual(self.sm.data["upgrades"]["archer_unlocked"], 1)

    def test_rewards_calculation(self):
        rewards_victory = Rewards.calculate_rewards(victory=True, num_ais=1, difficulty="Très Facile")
        self.assertGreater(rewards_victory[config.POINT_TYPE_FORGE], 0)

        rewards_loss = Rewards.calculate_rewards(victory=False, num_ais=1, difficulty="Très Facile")
        self.assertLess(rewards_loss[config.POINT_TYPE_FORGE], rewards_victory[config.POINT_TYPE_FORGE])

if __name__ == '__main__':
    unittest.main()
