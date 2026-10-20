import unittest
from src.entities.unit import Unit
from src.entities.building import Building
from src.entities.resource_node import ResourceNode
import config

class DummyGameState:
    def __init__(self):
        self.units = []
        self.buildings = []
        self.resources_player = {
            0: {"gold": 0, "wood": 0, "food": 0, "biomass": 0},
            1: {"gold": 0, "wood": 0, "food": 0, "biomass": 0}
        }

    def add_resources(self, owner_id, res_type, amount):
        if owner_id in self.resources_player:
            if res_type not in self.resources_player[owner_id]:
                self.resources_player[owner_id][res_type] = 0
            self.resources_player[owner_id][res_type] += amount

class TestEntities(unittest.TestCase):
    def test_unit_creation_and_damage(self):
        unit = Unit(owner_id=0, faction=config.FACTION_HUMAN, unit_type="Infantry", x=100, y=100)
        self.assertEqual(unit.hp, 150)
        unit.take_damage(30)
        self.assertEqual(unit.hp, 120)
        self.assertTrue(unit.alive)
        unit.take_damage(200)
        self.assertEqual(unit.hp, 0)
        self.assertFalse(unit.alive)

    def test_building_production_queue(self):
        building = Building(owner_id=0, faction=config.FACTION_HUMAN, building_type="Barracks", x=200, y=200)
        building.queue_unit("Infantry", train_time=0.5)
        self.assertEqual(len(building.production_queue), 1)

        result = building.update(dt=0.3)
        self.assertIsNone(result)

        result = building.update(dt=0.3)
        self.assertEqual(result, "Infantry")
        self.assertEqual(len(building.production_queue), 0)

    def test_unit_movement(self):
        unit = Unit(owner_id=0, faction=config.FACTION_HUMAN, unit_type="Worker", x=0, y=0)
        gs = DummyGameState()
        unit.move_to(100, 0)
        unit.update(dt=0.5, game_state=gs)
        self.assertGreater(unit.x, 0)

    def test_unit_collision_and_attack_move(self):
        u1 = Unit(0, "Medieval", "Infantry", 100, 100)
        u2 = Unit(0, "Medieval", "Infantry", 102, 100)
        self.assertLess(u1.distance_to(u2), u1.radius + u2.radius)

        u1.attack_move_to(200, 200)
        self.assertTrue(u1.attack_move_mode)
        self.assertEqual(u1.state, "move")

    def test_farm_harvesting(self):
        gs = DummyGameState()
        base = Building(owner_id=0, faction=config.FACTION_HUMAN, building_type="TownHall", x=100, y=100)
        farm = Building(owner_id=0, faction=config.FACTION_HUMAN, building_type="Farm", x=130, y=100)
        worker = Unit(owner_id=0, faction=config.FACTION_HUMAN, unit_type="Worker", x=130, y=100)

        gs.buildings.extend([base, farm])
        gs.units.append(worker)

        worker.harvest_node(farm)
        # Worker should enter inside the farm
        worker.update(0.1, gs)
        self.assertIn(worker, farm.garrisoned_units)
        self.assertFalse(worker.alive)

        # Ticks of farm operation
        for _ in range(50):
            farm.update(0.1, gs)

        self.assertGreater(gs.resources_player[0]["food"], 0)

if __name__ == '__main__':
    unittest.main()
