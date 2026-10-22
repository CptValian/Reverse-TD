import math
from src.entities.base_entity import BaseEntity
import config

UNIT_TYPES = {
    # Medieval
    "Worker": {"cost": {"food": 50}, "hp": 60, "speed": 100, "attack": 5, "range": 25, "is_worker": True, "radius": 12, "train_time": 10},
    "Scout": {"cost": {"food": 35, "gold": 15}, "hp": 70, "speed": 140, "attack": 6, "range": 25, "is_worker": False, "radius": 11, "train_time": 8, "vision": 400},
    "Infantry": {"cost": {"food": 60, "gold": 40}, "hp": 150, "speed": 90, "attack": 18, "range": 30, "is_worker": False, "radius": 15, "train_time": 14},
    "Archer": {"cost": {"food": 50, "wood": 50}, "hp": 90, "speed": 100, "attack": 14, "range": 180, "is_worker": False, "radius": 13, "train_time": 16},
    "Hero": {"cost": {"food": 0}, "hp": 200, "speed": 110, "attack": 25, "range": 30, "is_worker": False, "radius": 16, "train_time": 0},
    "Monk": {"cost": {"gold": 150, "food": 50}, "hp": 80, "speed": 90, "attack": 0, "range": 200, "is_worker": False, "radius": 13, "train_time": 15},

    # Alien
    "Drone": {"cost": {"biomass": 50}, "hp": 55, "speed": 105, "attack": 6, "range": 25, "is_worker": True, "radius": 12, "train_time": 9},
    "Swarmer": {"cost": {"biomass": 60}, "hp": 100, "speed": 125, "attack": 15, "range": 25, "is_worker": False, "radius": 12, "train_time": 12},
    "Spitter": {"cost": {"biomass": 130}, "hp": 80, "speed": 95, "attack": 16, "range": 170, "is_worker": False, "radius": 14, "train_time": 18},
    "Queen": {"cost": {"biomass": 250}, "hp": 220, "speed": 90, "attack": 22, "range": 160, "is_worker": False, "radius": 16, "train_time": 22}
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
        self.is_action_locked = False

        # Animations et effets visuels
        self.anim_time = 0.0
        self.is_attacking_anim = 0.0  # Timer d'animation de coup
        self.is_harvesting_anim = 0.0  # Timer d'animation de récolte
        self.attack_move_mode = False
        self.facing_angle = 0.0

        # Hero attributes
        self.is_hero = (unit_type == "Hero")
        self.hero_level = 1
        self.hero_kills = 0

        # Anti-stuck and crowding timers
        self.stuck_timer = 0.0
        self.stuck_check_timer = 0.0
        self.last_pos = (float(x), float(y))

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
        self.is_action_locked = False
        self.calculate_path(target_x, target_y, game_state)

    def attack_move_to(self, target_x, target_y, game_state=None):
        self.target_pos = (target_x, target_y)
        self.target_entity = None
        self.state = "move"
        self.attack_move_mode = True
        self.is_action_locked = False
        self.calculate_path(target_x, target_y, game_state)

    def attack_target(self, target, game_state=None):
        self.target_entity = target
        self.state = "attack"
        self.attack_move_mode = False
        self.is_action_locked = False
        if target:
            self.calculate_path(target.x, target.y, game_state)

    def construct_building(self, building, game_state=None):
        if not self.is_worker:
            return
        self.target_entity = building
        self.state = "construct"
        self.attack_move_mode = False
        self.is_action_locked = False
        if building:
            self.calculate_path(building.x, building.y, game_state)

    def repair_building(self, building, game_state=None):
        if not self.is_worker:
            return
        self.target_entity = building
        self.state = "repair"
        self.attack_move_mode = False
        self.is_action_locked = False
        if building:
            self.calculate_path(building.x, building.y, game_state)

    def harvest_node(self, node, game_state=None):
        if not self.is_worker:
            return
        self.target_entity = node
        self.state = "harvest"
        self.attack_move_mode = False
        self.is_action_locked = False
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

        # Anti-stuck check for active movement (exempt locked static workers)
        if self.state in ["move", "harvest", "return_resource", "construct", "repair"] and not getattr(self, 'is_action_locked', False):
            effective_dt = min(dt, 0.2)
            self.stuck_check_timer += effective_dt
            if self.stuck_check_timer >= 0.8:
                dist_moved = math.hypot(self.x - self.last_pos[0], self.y - self.last_pos[1])
                if dist_moved < 3.0:
                    self.stuck_timer += self.stuck_check_timer
                else:
                    self.stuck_timer = max(0.0, self.stuck_timer - 0.5)

                self.last_pos = (self.x, self.y)
                self.stuck_check_timer = 0.0

            if self.stuck_timer >= 1.5:
                # Apply lateral nudge vector to break unit congestion
                nudge_angle = self.facing_angle + math.pi / 2.0
                if (id(self) % 2) == 0:
                    nudge_angle -= math.pi
                self.x += math.cos(nudge_angle) * 4.0
                self.y += math.sin(nudge_angle) * 4.0

            if self.stuck_timer >= 3.0:
                self.stuck_timer = 0.0
                if self.is_worker and self.state in ["harvest", "return_resource", "construct"]:
                    self.state = "idle"
                    self.target_pos = None
                    self.path_waypoints.clear()
                elif self.state in ["move", "attack"]:
                    if self.target_pos:
                        self.calculate_path(self.target_pos[0], self.target_pos[1], game_state)
        elif getattr(self, 'is_action_locked', False):
            self.stuck_timer = 0.0
            self.stuck_check_timer = 0.0

        if self.unit_type == "Monk" and game_state:
            injured_allies = [
                u for u in game_state.units
                if u.alive and u is not self and u.hp < u.max_hp
                and not game_state.are_enemies(self.owner_id, u.owner_id)
                and self.distance_to(u) <= self.attack_range
            ]
            if injured_allies:
                heal_target = min(injured_allies, key=lambda u: u.hp / float(u.max_hp))
                heal_target.hp = min(heal_target.max_hp, heal_target.hp + 2.0 * dt)
                self.target_entity = heal_target
                self.is_attacking_anim = 0.2
                dx_h = heal_target.x - self.x
                dy_h = heal_target.y - self.y
                if dx_h != 0 or dy_h != 0:
                    self.facing_angle = math.atan2(dy_h, dx_h)

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
            if e.alive and game_state and game_state.are_enemies(self.owner_id, e.owner_id):
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
            self.is_action_locked = False
            self.pop_next_command(game_state)
            return

        bld = self.target_entity
        if getattr(bld, 'is_constructed', True):
            self.target_entity = None
            self.state = "idle"
            self.is_action_locked = False
            if self.is_worker and not self.command_queue and game_state:
                nearby_unconstructed = [
                    b for b in game_state.buildings
                    if b.alive and not b.is_constructed and b.owner_id == self.owner_id and self.distance_to(b) <= 450
                ]
                if nearby_unconstructed:
                    next_bld = min(nearby_unconstructed, key=lambda b: self.distance_to(b))
                    self.construct_building(next_bld, game_state)
                    return

            self.pop_next_command(game_state)
            return

        dist = self.distance_to(bld)
        dx = bld.x - self.x
        dy = bld.y - self.y

        if not self.is_action_locked:
            if dist > self.radius + bld.radius + 22:
                self._move_towards(bld.x, bld.y, dt, game_state)
            else:
                self.is_action_locked = True
                if dist > 0:
                    self.facing_angle = math.atan2(dy, dx)
                self.path_waypoints.clear()
                self.target_pos = None

        if self.is_action_locked:
            if dist > self.radius + bld.radius + 38:
                self.is_action_locked = False
            else:
                if self.unit_type == "Drone":
                    self.alive = False
                    bld.is_being_built = True
                elif self.is_worker:
                    bld.build_progress(dt, speed_mult=1.0)
                    self.is_harvesting_anim = 0.2

    def _process_repair(self, dt, game_state):
        if not self.target_entity or not getattr(self.target_entity, 'alive', True):
            self.target_entity = None
            self.state = "idle"
            self.is_action_locked = False
            self.pop_next_command(game_state)
            return

        bld = self.target_entity
        if bld.hp >= bld.max_hp:
            self.target_entity = None
            self.state = "idle"
            self.is_action_locked = False
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(bld)
        dx = bld.x - self.x
        dy = bld.y - self.y

        if not self.is_action_locked:
            if dist > self.radius + bld.radius + 22:
                self._move_towards(bld.x, bld.y, dt, game_state)
            else:
                self.is_action_locked = True
                if dist > 0:
                    self.facing_angle = math.atan2(dy, dx)
                self.path_waypoints.clear()
                self.target_pos = None

        if self.is_action_locked:
            if dist > self.radius + bld.radius + 38:
                self.is_action_locked = False
            else:
                repair_rate = 25.0 * dt
                cost_factor = repair_rate / max(1.0, bld.max_hp)
                rep_cost = {}
                for r_k, r_v in bld.cost.items():
                    rep_cost[r_k] = max(0.1 * dt, r_v * cost_factor * 0.2)

                if game_state.deduct_resources(self.owner_id, rep_cost):
                    bld.hp = min(bld.max_hp, bld.hp + repair_rate)
                    self.is_harvesting_anim = 0.2
                else:
                    self.state = "idle"
                    self.is_action_locked = False

    def take_damage(self, amount, attacker=None, game_state=None):
        if attacker and game_state and not game_state.are_enemies(self.owner_id, attacker.owner_id):
            return  # Immune to friendly/allied damage
        super().take_damage(amount, attacker=attacker, game_state=game_state)
        # If unit is attacked and currently idle, defend itself against the attacker
        if self.alive and self.state == "idle" and attacker and getattr(attacker, 'alive', True):
            if game_state and game_state.are_enemies(self.owner_id, attacker.owner_id):
                if not self.is_worker or getattr(attacker, 'is_worker', False):
                    self.attack_target(attacker, game_state)

    def _process_attack(self, dt, game_state):
        if not self.target_entity or not self.target_entity.alive or (game_state and not game_state.are_enemies(self.owner_id, self.target_entity.owner_id)):
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
                def make_on_hit_cb(attacker, target_e):
                    def on_hit_cb(target, prev_hp, gs):
                        if not target.alive:
                            if attacker.unit_type == "Queen":
                                swarmer = Unit(attacker.owner_id, attacker.faction, "Swarmer", target.x, target.y)
                                gs.units.append(swarmer)
                            if attacker.is_hero:
                                attacker.add_hero_kill()
                    return on_hit_cb

                on_hit = make_on_hit_cb(self, self.target_entity)

                if self.attack_range > 50 or self.unit_type in ["Archer", "Spitter", "Queen"] or (self.is_hero and getattr(self, 'is_hero_archer', False)):
                    from src.entities.projectile import Projectile
                    p_type = "arrow"
                    if self.unit_type == "Spitter":
                        p_type = "spitter_spore"
                    elif self.unit_type == "Queen":
                        p_type = "queen_spore"

                    proj = Projectile(self.x, self.y, self.target_entity, self.attack_power, speed=500, owner_id=self.owner_id, projectile_type=p_type, on_hit_callback=on_hit, attacker_entity=self)
                    if hasattr(game_state, 'projectiles'):
                        game_state.projectiles.append(proj)
                    else:
                        # Fallback if projectiles list not initialized
                        self.target_entity.take_damage(self.attack_power, attacker=self, game_state=game_state)
                        if not self.target_entity.alive and self.is_hero:
                            self.add_hero_kill()
                else:
                    self.target_entity.take_damage(self.attack_power, attacker=self, game_state=game_state)
                    if not self.target_entity.alive and self.is_hero:
                        self.add_hero_kill()

                self.attack_cooldown = 1.0  # Temps de recharge
                self.is_attacking_anim = 0.3  # Animation flash/projectile pendant 0.3s

    def add_hero_kill(self):
        if not self.is_hero:
            return
        self.hero_kills += 1
        # Level up every kill (or 1 kill = 1 level up)
        new_level = 1 + self.hero_kills
        if new_level > self.hero_level:
            levels_gained = new_level - self.hero_level
            self.hero_level = new_level
            # Each level above 1 grants: +5% HP, +3% ATK speed, +3% ATK damage
            hp_ratio = self.hp / max(1.0, self.max_hp)
            self.max_hp = max(self.max_hp + 1, int(round(self.max_hp * (1.0 + 0.05 * levels_gained))))
            self.hp = int(self.max_hp * hp_ratio)
            self.attack_power = max(self.attack_power + 1, int(round(self.attack_power * (1.0 + 0.03 * levels_gained))))

    def _process_harvest(self, dt, game_state):
        if not self.target_entity or not getattr(self.target_entity, 'alive', True):
            self.target_entity = None
            self.state = "idle"
            self.is_action_locked = False
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(self.target_entity)
        dx = self.target_entity.x - self.x
        dy = self.target_entity.y - self.y

        min_range = self.radius + self.target_entity.radius + 18
        max_range = self.radius + self.target_entity.radius + 55

        if not self.is_action_locked:
            if dist > max_range:
                self._move_towards(self.target_entity.x, self.target_entity.y, dt, game_state)
            elif dist <= min_range:
                self.is_action_locked = True
                if dist > 0:
                    self.facing_angle = math.atan2(dy, dx)
                self.path_waypoints.clear()
                self.target_pos = None
            else:
                # Between min_range and max_range: lock if blocked by crowding or other workers
                is_blocked = (getattr(self, 'stuck_timer', 0.0) > 0.15)
                if not is_blocked and game_state:
                    for other in game_state.units:
                        if other is not self and getattr(other, 'is_action_locked', False) and getattr(other, 'target_entity', None) == self.target_entity:
                            if self.distance_to(other) <= self.radius + other.radius + 16:
                                is_blocked = True
                                break

                if is_blocked:
                    self.is_action_locked = True
                    if dist > 0:
                        self.facing_angle = math.atan2(dy, dx)
                    self.path_waypoints.clear()
                    self.target_pos = None
                else:
                    self._move_towards(self.target_entity.x, self.target_entity.y, dt, game_state)

        if self.is_action_locked:
            if dist > max_range + 20:
                self.is_action_locked = False
            else:
                if hasattr(self.target_entity, 'harvest'):
                    harvested = self.target_entity.harvest(config.DEFAULT_HARVEST_RATE * dt)
                    self.carried_resource += harvested
                    self.resource_type = self.target_entity.resource_type
                elif getattr(self.target_entity, 'building_type', None) == "Farm":
                    if self.target_entity.garrison_unit(self):
                        self.is_action_locked = False
                        return
                    else:
                        self.state = "idle"
                        self.is_action_locked = False
                        return
                self.is_harvesting_anim = 0.2
                if self.carried_resource >= config.DEFAULT_HARVEST_CAPACITY or not getattr(self.target_entity, 'alive', True):
                    self.is_action_locked = False
                    self.state = "return_resource"

    def _process_return_resource(self, dt, game_state):
        deposit = self._find_nearest_deposit(game_state)
        if not deposit:
            self.state = "idle"
            self.is_action_locked = False
            self.pop_next_command(game_state)
            return

        dist = self.distance_to(deposit)
        dx = deposit.x - self.x
        dy = deposit.y - self.y

        if dist > self.radius + deposit.radius + 18:
            self._move_towards(deposit.x, deposit.y, dt, game_state)
        else:
            if dist > 0:
                self.facing_angle = math.atan2(dy, dx)
            self.path_waypoints.clear()
            self.target_pos = None

            game_state.add_resources(self.owner_id, self.resource_type, self.carried_resource)
            self.carried_resource = 0
            self.is_action_locked = False
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
                elif b_type == "BiomassStockpile" and self.resource_type == "biomass":
                    accepts = True

                if accepts:
                    dist = self.distance_to(b)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = b
        return nearest

    def _find_nearest_base(self, game_state):
        return self._find_nearest_deposit(game_state)
