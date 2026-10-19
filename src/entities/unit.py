import math
from src.entities.base_entity import BaseEntity
import config

UNIT_TYPES = {
    # Medieval
    "Worker": {"cost": {"food": 50}, "hp": 60, "speed": 100, "attack": 5, "range": 25, "is_worker": True, "radius": 12, "train_time": 10},
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

        # États : "idle", "move", "harvest", "return_resource", "attack"
        self.state = "idle"
        self.target_pos = None
        self.target_entity = None
        self.attack_cooldown = 0
        self.carried_resource = 0
        self.resource_type = None

        # Animations et effets visuels
        self.anim_time = 0.0
        self.is_attacking_anim = 0.0  # Timer d'animation de coup
        self.is_harvesting_anim = 0.0  # Timer d'animation de récolte
        self.attack_move_mode = False
        self.facing_angle = 0.0

    def move_to(self, target_x, target_y):
        self.target_pos = (target_x, target_y)
        self.target_entity = None
        self.state = "move"
        self.attack_move_mode = False

    def attack_move_to(self, target_x, target_y):
        self.target_pos = (target_x, target_y)
        self.target_entity = None
        self.state = "move"
        self.attack_move_mode = True

    def attack_target(self, target):
        self.target_entity = target
        self.state = "attack"
        self.attack_move_mode = False

    def harvest_node(self, node):
        if not self.is_worker:
            return
        self.target_entity = node
        self.state = "harvest"
        self.attack_move_mode = False

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

    def _process_movement(self, dt):
        if not self.target_pos:
            self.state = "idle"
            self.attack_move_mode = False
            return

        tx, ty = self.target_pos
        dist = math.hypot(tx - self.x, ty - self.y)
        if dist < 5:
            self.x, self.y = tx, ty
            self.target_pos = None
            self.state = "idle"
            self.attack_move_mode = False
        else:
            dir_x = (tx - self.x) / dist
            dir_y = (ty - self.y) / dist
            self.facing_angle = math.atan2(dir_y, dir_x)
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt

    def _process_attack(self, dt, game_state):
        if not self.target_entity or not self.target_entity.alive:
            self.target_entity = None
            if self.target_pos and self.attack_move_mode:
                self.state = "move"
            else:
                self.state = "idle"
                self.attack_move_mode = False
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
                harvested = config.DEFAULT_HARVEST_RATE * dt
                self.carried_resource += harvested
                self.resource_type = "food"
            self.is_harvesting_anim = 0.2
            if self.carried_resource >= config.DEFAULT_HARVEST_CAPACITY or not getattr(self.target_entity, 'alive', True):
                self.state = "return_resource"

    def _process_return_resource(self, dt, game_state):
        deposit = self._find_nearest_deposit(game_state)
        if not deposit:
            self.state = "idle"
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

                if accepts:
                    dist = self.distance_to(b)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = b
        return nearest

    def _find_nearest_base(self, game_state):
        return self._find_nearest_deposit(game_state)
