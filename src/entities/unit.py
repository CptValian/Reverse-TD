import math
from src.entities.base_entity import BaseEntity
import config

UNIT_TYPES = {
    # Medieval
    "Worker": {"cost": {"food": 50}, "hp": 60, "speed": 100, "attack": 5, "range": 25, "is_worker": True, "radius": 12, "train_time": 10},
    "Scout": {"cost": {"food": 35, "gold": 15}, "hp": 70, "speed": 140, "attack": 6, "range": 25, "is_worker": False, "radius": 11, "train_time": 8, "vision": 400},
    "Infantry": {"cost": {"food": 60, "gold": 40}, "hp": 150, "speed": 90, "attack": 18, "range": 30, "is_worker": False, "radius": 15, "train_time": 14},
    "Archer": {"cost": {"food": 50, "wood": 50}, "hp": 90, "speed": 100, "attack": 14, "range": 180, "is_worker": False, "radius": 13, "train_time": 16},

    # Alien
    "Drone": {"cost": {"biomass": 50}, "hp": 55, "speed": 105, "attack": 6, "range": 25, "is_worker": True, "radius": 12, "train_time": 9},
    "Swarmer": {"cost": {"biomass": 60}, "hp": 100, "speed": 125, "attack": 15, "range": 25, "is_worker": False, "radius": 12, "train_time": 12},
    "Spitter": {"cost": {"biomass": 130}, "hp": 80, "speed": 95, "attack": 16, "range": 170, "is_worker": False, "radius": 14, "train_time": 18}
}

class Unit(BaseEntity):
    def __init__(self, owner_id, faction, unit_type, x, y, hp_bonus=0, attack_bonus=0, speed_bonus=0):
        data = UNIT_TYPES.get(unit_type, {"hp": 100, "speed": 100, "attack": 10, "range": 30, "is_worker": False, "radius": 15})
        max_hp = data["hp"] + hp_bonus
        super().__init__(owner_id, faction, x, y, max_hp, radius=data["radius"])

        self.unit_type = unit_type
        self.speed = data["speed"] + speed_bonus
        self.attack_power = data["attack"] + attack_bonus
        self.attack_range = data["range"]
        self.is_worker = data.get("is_worker", False)
        self.vision_radius = data.get("vision", 220)

        # États : "idle", "move", "harvest", "return_resource", "attack", "construct", "repair"
        self.state = "idle"
        self.target_pos = None
        self.target_entity = None
        self.path_waypoints = []
        self.command_queue = []
        self.attack_cooldown = 0
        self.carried_resource = 0
        self.resource_type = None

        # Animations et effets visuels
        self.anim_time = 0.0
        self.is_attacking_anim = 0.0  # Timer d'animation de coup
        self.is_harvesting_anim = 0.0  # Timer d'animation de récolte
        self.attack_move_mode = False
        self.facing_angle = 0.0

    def calculate_path(self, target_x, target_y, game_state):
        if game_state:
            from src.engine.pathfinding import PathfindingGrid
            grid = PathfindingGrid()
            self.path_waypoints = grid.find_path((self.x, self.y), (target_x, target_y), game_state, ignore_entity=self.target_entity)
        else:
            self.path_waypoints = [(target_x, target_y)]

    def move_to(self, target_x, target_y, game_state=None):
        self.target_pos = (target_x, target_y)
        self.target_entity = None
        self.state = "move"
        self.attack_move_mode = False
        self.calculate_path(target_x, target_y, game_state)

    def attack_move_to(self, target_x, target_y, game_state=None):
        self.target_pos = (target_x, target_y)
        self.target_entity = None
        self.state = "move"
        self.attack_move_mode = True
        self.calculate_path(target_x, target_y, game_state)

    def attack_target(self, target, game_state=None):
        self.target_entity = target
        self.state = "attack"
        self.attack_move_mode = False
        if target:
            self.calculate_path(target.x, target.y, game_state)

    def construct_building(self, building, game_state=None):
        if not self.is_worker and self.unit_type != "Swarmer":
            return
        self.target_entity = building
        self.state = "construct"
        self.attack_move_mode = False
        if building:
            self.calculate_path(building.x, building.y, game_state)

    def repair_building(self, building, game_state=None):
        if not self.is_worker:
            return
        self.target_entity = building
        self.state = "repair"
        self.attack_move_mode = False
        if building:
            self.calculate_path(building.x, building.y, game_state)

    def harvest_node(self, node, game_state=None):
        if not self.is_worker:
            return
        self.target_entity = node
        self.state = "harvest"
        self.attack_move_mode = False
        if node:
            self.calculate_path(node.x, node.y, game_state)

    def pop_next_command(self, game_state):
        if self.command_queue:
            cmd = self.command_queue.pop(0)
            c_type = cmd.get("type")
            if c_type == "move":
                self.move_to(cmd["pos"][0], cmd["pos"][1], game_state)
            elif c_type == "attack" and cmd.get("target") and cmd["target"].alive:
                self.attack_target(cmd["target"], game_state)
            elif c_type == "construct" and cmd.get("target") and cmd["target"].alive:
                self.construct_building(cmd["target"], game_state)
            elif c_type == "repair" and cmd.get("target") and cmd["target"].alive:
                self.repair_building(cmd["target"], game_state)
            elif c_type == "harvest" and cmd.get("target") and getattr(cmd["target"], "alive", True):
                self.harvest_node(cmd["target"], game_state)
            elif c_type == "garrison" and cmd.get("target") and cmd["target"].alive:
                if self.distance_to(cmd["target"]) <= self.radius + cmd["target"].radius + 15:
                    cmd["target"].garrison_unit(self)
                else:
                    self.move_to(cmd["target"].x, cmd["target"].y, game_state)
            else:
                self.pop_next_command(game_state)

    def update(self, dt, game_state):
        if not self.alive:
            return

        self.anim_time += dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.is_attacking_anim > 0:
            self.is_attacking_anim -= dt
        if self.is_harvesting_anim > 0:
            self.is_harvesting_anim -= dt

        # Mode Attack-Move : Scanner s'il y a un ennemi à proximité si en déplacement
        if self.attack_move_mode and self.state == "move":
            enemy = self._scan_for_enemy(game_state)
            if enemy:
                self.target_entity = enemy
                self.state = "attack"

        if self.state == "move":
            self._process_movement(dt)

        elif self.state == "attack":
            self._process_attack(dt, game_state)

        elif self.state == "construct":
            self._process_construct(dt, game_state)

        elif self.state == "repair":
            self._process_repair(dt, game_state)

        elif self.state == "harvest":
            self._process_harvest(dt, game_state)

        elif self.state == "return_resource":
            self._process_return_resource(dt, game_state)

    def _scan_for_enemy(self, game_state):
        scan_range = 250
        nearest_enemy = None
        min_d = scan_range
        for e in game_state.units + game_state.buildings:
            if e.alive and e.owner_id != self.owner_id:
                d = self.distance_to(e)
                if d < min_d:
                    min_d = d
                    nearest_enemy = e
        return nearest_enemy

    def _move_towards(self, tx, ty, dt, game_state=None):
        dist = math.hypot(tx - self.x, ty - self.y)
        if dist < 5:
            self.x, self.y = tx, ty
            return True

        dir_x = (tx - self.x) / dist
        dir_y = (ty - self.y) / dist
        self.facing_angle = math.atan2(dir_y, dir_x)

        step_x = dir_x * self.speed * dt
        step_y = dir_y * self.speed * dt

        if game_state:
            next_x = self.x + step_x
            next_y = self.y + step_y

            collides = False
            for b in game_state.buildings:
                if not b.alive or b == self.target_entity:
                    continue
                min_dist = self.radius + b.radius
                if (next_x - b.x)**2 + (next_y - b.y)**2 < min_dist * min_dist:
                    collides = True
                    break

            if collides:
                collides_x = False
                for b in game_state.buildings:
                    if not b.alive or b == self.target_entity:
                        continue
                    if (self.x + step_x - b.x)**2 + (self.y - b.y)**2 < (self.radius + b.radius)**2:
                        collides_x = True; break

                collides_y = False
                for b in game_state.buildings:
                    if not b.alive or b == self.target_entity:
                        continue
                    if (self.x - b.x)**2 + (self.y + step_y - b.y)**2 < (self.radius + b.radius)**2:
                        collides_y = True; break

                if not collides_x:
                    self.x += step_x
                elif not collides_y:
                    self.y += step_y
                else:
                    self.x += step_x
                    self.y += step_y
            else:
                self.x = next_x
                self.y = next_y
        else:
            self.x += step_x
            self.y += step_y

        return False

    def _process_movement(self, dt, game_state=None):
        if not self.target_pos and not self.path_waypoints:
            self.state = "idle"
            self.attack_move_mode = False
            self.pop_next_command(game_state)
            return

        target_wp = self.path_waypoints[0] if self.path_waypoints else self.target_pos
        reached = self._move_towards(target_wp[0], target_wp[1], dt, game_state)

        if reached:
            if self.path_waypoints:
                self.path_waypoints.pop(0)
            if not self.path_waypoints:
                self.target_pos = None
                self.state = "idle"
                self.attack_move_mode = False
                self.pop_next_command(game_state)

    def _process_construct(self, dt, game_state):
        if not self.target_entity or not getattr(self.target_entity, 'alive', True):
            self.target_entity = None
            self.state = "idle"
            self.pop_next_command(game_state)
            return

        bld = self.target_entity
        if getattr(bld, 'is_constructed', True):
            self.target_entity = None
            self.state = "idle"
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(bld)
        dx = bld.x - self.x
        dy = bld.y - self.y
        if dist > 0:
            self.facing_angle = math.atan2(dy, dx)

        if dist > self.radius + bld.radius + 15:
            # Move towards unconstructed building
            self._move_towards(bld.x, bld.y, dt, game_state)
        else:
            # Construct building
            if self.faction == config.FACTION_ALIEN or self.unit_type in ["Drone", "Swarmer"]:
                # Alien insect morphs/sacrifices itself to become the building
                self.alive = False
                bld.build_progress(dt + bld.total_build_time * 0.5, speed_mult=1.0)
            else:
                bld.build_progress(dt, speed_mult=1.0)
                self.is_harvesting_anim = 0.2

    def _process_repair(self, dt, game_state):
        if not self.target_entity or not getattr(self.target_entity, 'alive', True):
            self.target_entity = None
            self.state = "idle"
            self.pop_next_command(game_state)
            return

        bld = self.target_entity
        if bld.hp >= bld.max_hp:
            self.target_entity = None
            self.state = "idle"
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(bld)
        dx = bld.x - self.x
        dy = bld.y - self.y
        if dist > 0:
            self.facing_angle = math.atan2(dy, dx)

        if dist > self.radius + bld.radius + 15:
            dir_x = dx / dist
            dir_y = dy / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # Repair cost is cheap fraction of building cost
            repair_rate = 25.0 * dt  # 25 HP per second
            cost_factor = repair_rate / max(1.0, bld.max_hp)
            rep_cost = {}
            for r_k, r_v in bld.cost.items():
                rep_cost[r_k] = max(0.1 * dt, r_v * cost_factor * 0.2)

            if game_state.deduct_resources(self.owner_id, rep_cost):
                bld.hp = min(bld.max_hp, bld.hp + repair_rate)
                self.is_harvesting_anim = 0.2
            else:
                self.state = "idle"

    def _process_attack(self, dt, game_state):
        if not self.target_entity or not self.target_entity.alive:
            self.target_entity = None
            if self.target_pos and self.attack_move_mode:
                self.state = "move"
            else:
                self.state = "idle"
                self.attack_move_mode = False
                self.pop_next_command(game_state)
            return

        dist = self.distance_to(self.target_entity)
        dx = self.target_entity.x - self.x
        dy = self.target_entity.y - self.y
        if dist > 0:
            self.facing_angle = math.atan2(dy, dx)

        if dist > self.attack_range + self.radius + self.target_entity.radius:
            # Se rapprocher du cible
            dir_x = dx / dist
            dir_y = dy / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # À portée d'attaque
            if self.attack_cooldown <= 0:
                self.target_entity.take_damage(self.attack_power)
                self.attack_cooldown = 1.0  # Temps de recharge
                self.is_attacking_anim = 0.3  # Animation flash/projectile pendant 0.3s

    def _process_harvest(self, dt, game_state):
        if not self.target_entity or not getattr(self.target_entity, 'alive', True):
            self.target_entity = None
            self.state = "idle"
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(self.target_entity)
        dx = self.target_entity.x - self.x
        dy = self.target_entity.y - self.y
        if dist > 0:
            self.facing_angle = math.atan2(dy, dx)

        if dist > self.radius + self.target_entity.radius + 10:
            # Se rapprocher du gisement
            dir_x = dx / dist
            dir_y = dy / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # Récolter
            if hasattr(self.target_entity, 'harvest'):
                harvested = self.target_entity.harvest(config.DEFAULT_HARVEST_RATE * dt)
                self.carried_resource += harvested
                self.resource_type = self.target_entity.resource_type
            elif getattr(self.target_entity, 'building_type', None) == "Farm":
                # Worker enters inside the Farm to work
                if self.target_entity.garrison_unit(self):
                    return
                else:
                    self.state = "idle"
                    return
            self.is_harvesting_anim = 0.2
            if self.carried_resource >= config.DEFAULT_HARVEST_CAPACITY or not getattr(self.target_entity, 'alive', True):
                self.state = "return_resource"

    def _process_return_resource(self, dt, game_state):
        deposit = self._find_nearest_deposit(game_state)
        if not deposit:
            self.state = "idle"
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(deposit)
        if dist > self.radius + deposit.radius + 10:
            dir_x = (deposit.x - self.x) / dist
            dir_y = (deposit.y - self.y) / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # Déposer les ressources
            game_state.add_resources(self.owner_id, self.resource_type, self.carried_resource)
            self.carried_resource = 0
            # Repartir récolter
            if self.target_entity and getattr(self.target_entity, 'alive', True):
                self.state = "harvest"
            else:
                self.state = "idle"

    def _find_nearest_deposit(self, game_state):
        nearest = None
        min_dist = float('inf')
        for b in game_state.buildings:
            if b.alive and b.owner_id == self.owner_id and getattr(b, 'is_constructed', True):
                accepts = False
                b_type = getattr(b, 'building_type', '')
                if b_type in ["TownHall", "Hive"]:
                    accepts = True
                elif b_type == "WoodStockpile" and self.resource_type == "wood":
                    accepts = True
                elif b_type == "GoldStockpile" and self.resource_type == "gold":
                    accepts = True
                elif b_type == "FoodStockpile" and self.resource_type == "food":
                    accepts = True

                if accepts:
                    dist = self.distance_to(b)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = b
        return nearest

    def _find_nearest_base(self, game_state):
        return self._find_nearest_deposit(game_state)
