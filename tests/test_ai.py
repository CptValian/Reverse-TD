import unittest
from src.ai.ai_controller import AIController
from src.entities.unit import Unit
from src.entities.building import Building
from src.entities.resource_node import ResourceNode
import config

class MockGameState:
    def __init__(self):
        self.units = []
        self.buildings = []
        self.resources = []
        self.resources_player = {
            0: {"gold": 500, "biomass": 500},
            1: {"gold": 500, "biomass": 500}
        }

    def deduct_resources(self, owner_id, res_type, amount=None):
        if isinstance(res_type, dict):
            for r, c in res_type.items():
                if self.resources_player[owner_id].get(r, 0) < c:
                    return False
            for r, c in res_type.items():
                self.resources_player[owner_id][r] -= c
            return True
        else:
            if self.resources_player[owner_id].get(res_type, 0) >= amount:
                self.resources_player[owner_id][res_type] -= amount
                return True
            return False

    def can_place_building(self, building_type, x, y, owner_id=None):
        return True

class TestAI(unittest.TestCase):
    def test_ai_controller_behavior(self):
        gs = MockGameState()
        # Ajouter une base et des ouvriers pour l'IA (owner_id = 1)
        base = Building(owner_id=1, faction=config.FACTION_ALIEN, building_type="Hive", x=1000, y=1000)
        drone = Unit(owner_id=1, faction=config.FACTION_ALIEN, unit_type="Drone", x=1000, y=1000)
        res_node = ResourceNode("biomass", x=1100, y=1000)

        gs.buildings.append(base)
        gs.units.append(drone)
        gs.resources.append(res_node)

        ai = AIController(owner_id=1, difficulty="Très Facile")
        ai.update(dt=0.1, game_state=gs)

        # L'ouvrier au repos doit passer en état récolte
        self.assertEqual(drone.state, "harvest")

if __name__ == '__main__':
    unittest.main()
