import unittest
import math
import config
from src.entities.building import Building
from src.entities.unit import Unit
from src.entities.resource_node import ResourceNode
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager
from src.ai.ai_controller import AIController

class TestAIImprovements(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager(filepath="test_save_ai_tmp.json")
        self.game_state = GameState(self.save_manager)

    def test_building_under_construction_damage_multiplier(self):
        bld = Building(0, config.FACTION_HUMAN, "Barracks", 200, 200, is_constructed=False)
        initial_hp = bld.hp
        # Barracks armor is 0. 10 damage * 2.5 multiplier = 25 damage
        bld.take_damage(10)
        self.assertEqual(bld.hp, initial_hp - 25)

        # Progress construction should not overwrite damage
        bld.build_progress(1.0)
        self.assertEqual(bld.hp, initial_hp - 25 + int(bld.max_hp * 0.90 * (1.0 / bld.total_build_time)))

    def test_under_attack_notification(self):
        ai = AIController(1, config.FACTION_ALIEN, difficulty=18)
        self.game_state.ai_controllers.append(ai)

        bld = Building(1, config.FACTION_ALIEN, "Hive", 100, 100)
        attacker = Unit(0, config.FACTION_HUMAN, "Infantry", 150, 100)
        defender = Unit(1, config.FACTION_ALIEN, "Swarmer", 120, 100)

        self.game_state.buildings.append(bld)
        self.game_state.units.extend([attacker, defender])

        # Base taking damage notifies AI and directs defender to attack
        bld.take_damage(10, attacker=attacker, game_state=self.game_state)
        self.assertEqual(defender.state, "attack")
        self.assertEqual(defender.target_entity, attacker)

    def test_worker_load_balancing_and_anti_stuck(self):
        drone = Unit(1, config.FACTION_ALIEN, "Drone", 100, 100)
        self.game_state.units.append(drone)

        # Simulate stuck drone
        drone.state = "harvest"
        drone.last_pos = (100, 100)
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)

        # After multiple stuck ticks, stuck_timer accumulates
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)
        drone.stuck_check_timer = 0.8
        drone.update(0.1, self.game_state)

        self.assertGreater(drone.stuck_timer, 0.0)

    def test_iacia_level_18_attack_triggers(self):
        ai = AIController(1, config.FACTION_ALIEN, difficulty=18)

        units = [Unit(1, config.FACTION_ALIEN, "Swarmer", 100 + i * 10, 100) for i in range(12)]

        enemy_hive = Building(2, config.FACTION_HUMAN, "TownHall", 800, 800)

        self.game_state.units.extend(units)
        self.game_state.buildings.append(enemy_hive)
        self.game_state.teams = {1: 1, 2: 2}

        ai.update(0.1, self.game_state)

        # Strategic army threshold triggers attack
        self.assertIn(units[0].state, ["move", "attack"])

    def test_ai_building_placement_clearance(self):
        ai = AIController(1, config.FACTION_HUMAN, difficulty=5)
        # Place existing building and resource node
        existing_bld = Building(1, config.FACTION_HUMAN, "TownHall", 500, 500)
        res_node = ResourceNode("gold", 600, 500)
        self.game_state.buildings.append(existing_bld)
        self.game_state.resources.append(res_node)

        pos = ai._find_valid_building_position(self.game_state, "Barracks", 500, 500, min_building_gap=50, min_resource_gap=75)
        self.assertIsNotNone(pos)
        bx, by = pos

        # Verify clearance from existing building
        dist_bld = math.hypot(bx - existing_bld.x, by - existing_bld.y)
        self.assertGreaterEqual(dist_bld, existing_bld.radius + 35 + 50)

        # Verify clearance from resource node
        dist_res = math.hypot(bx - res_node.x, by - res_node.y)
        self.assertGreaterEqual(dist_res, res_node.radius + 35 + 75)

    def test_unblocked_spawn_pos_when_training_units(self):
        bld = Building(1, config.FACTION_HUMAN, "Barracks", 400, 400)
        self.game_state.buildings.append(bld)

        # Block default spawn area below building with another building
        blocking_bld = Building(1, config.FACTION_HUMAN, "House", 400, 400 + bld.radius + 20)
        self.game_state.buildings.append(blocking_bld)

        sx, sy = self.game_state._find_unblocked_spawn_pos(bld, unit_radius=15)
        # Ensure spawn pos does not collide with blocking_bld
        dist_to_blocking = math.hypot(sx - blocking_bld.x, sy - blocking_bld.y)
        self.assertGreaterEqual(dist_to_blocking, blocking_bld.radius + 15 + 5)

    def test_static_worker_during_harvesting_and_building(self):
        worker = Unit(1, config.FACTION_HUMAN, "Worker", 200, 200)
        res_node = ResourceNode("gold", 220, 200)
        self.game_state.units.append(worker)
        self.game_state.resources.append(res_node)

        worker.harvest_node(res_node, self.game_state)
        # Move worker close enough to lock interaction
        worker.x, worker.y = 220 - (worker.radius + res_node.radius + 5), 200
        worker.update(0.1, self.game_state)

        # Worker should now be action locked
        self.assertTrue(worker.is_action_locked)

        initial_pos = (worker.x, worker.y)
        initial_angle = worker.facing_angle

        # Additional ticks should keep position and facing angle static
        worker.update(0.5, self.game_state)
        self.assertEqual((worker.x, worker.y), initial_pos)
        self.assertEqual(worker.facing_angle, initial_angle)
        self.assertEqual(worker.stuck_timer, 0.0)

    def test_ai_reflection_cycle_interval(self):
        ai = AIController(1, config.FACTION_ALIEN, difficulty=5)
        self.assertEqual(ai.reflection_interval, 0.5)

        # Set reflection timer below threshold
        ai.reflection_timer = 0.1
        drone = Unit(1, config.FACTION_ALIEN, "Drone", 300, 300)
        self.game_state.units.append(drone)
        res = ResourceNode("biomass", 400, 300)
        self.game_state.resources.append(res)

        # Update with dt=0.1 -> reflection_timer becomes 0.2 < 0.5 so heavy decision logic doesn't run
        ai.update(0.1, self.game_state)
        self.assertEqual(drone.state, "idle")

        # Update with dt=0.4 -> reflection_timer becomes 0.6 >= 0.5, decision logic executes
        ai.update(0.4, self.game_state)
        self.assertEqual(drone.state, "harvest")

if __name__ == '__main__':
    unittest.main()
