import unittest
from src.engine.map_generator import MapGenerator
import config

class TestMapGenerator(unittest.TestCase):
    def test_map_generation(self):
        generator = MapGenerator(width=2000, height=2000)
        map_data = generator.generate_map(num_players=2)

        self.assertEqual(map_data["width"], 2000)
        self.assertEqual(map_data["height"], 2000)
        self.assertEqual(len(map_data["spawns"]), 2)
        self.assertGreater(len(map_data["resources"]), 5)

if __name__ == '__main__':
    unittest.main()
