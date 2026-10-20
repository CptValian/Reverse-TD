import unittest
import math
from src.entities.unit import Unit
from src.entities.building import Building
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager

class TestWallCollision(unittest.TestCase):
    def test_diagonal_wall_collision(self):
        sm = SaveManager()
        gs = GameState(sm)

        # Create a diagonal wall segment at (500, 500) angled at 45 degrees
        angle = math.pi / 4
        wall = Building(owner_id=0, faction="Medieval", building_type="Wall", x=500, y=500, wall_length=100, wall_width=18, wall_angle=angle)
        gs.buildings.append(wall)

        # Place a unit inside/overlapping the wall
        unit = Unit(owner_id=1, faction="Alien", unit_type="Swarmer", x=500, y=500)
        gs.units.append(unit)

        # Resolve collisions
        gs.resolve_unit_collisions()

        # The unit should be pushed outside the wall rectangle boundary
        dist = math.hypot(unit.x - wall.x, unit.y - wall.y)
        self.assertGreater(dist, 8.0)

if __name__ == "__main__":
    unittest.main()
