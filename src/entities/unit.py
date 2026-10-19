import math
from src.entities.base_entity import BaseEntity
import config

UNIT_TYPES = {
    # Médiéval
    "Worker": {"cost": 50, "hp": 60, "speed": 120, "attack": 5, "range": 25, "is_worker": True, "radius": 12},
    "Infantry": {"cost": 100, "hp": 150, "speed": 100, "attack": 18, "range": 30, "is_worker": False, "radius": 15},
    "Archer": {"cost": 120, "hp": 90, "speed": 110, "attack": 14, "range": 180, "is_worker": False, "radius": 13},

    # Alien
    "Drone": {"cost": 50, "hp": 55, "speed": 130, "attack": 6, "range": 25, "is_worker": True, "radius": 12},
    "Swarmer": {"cost": 80, "hp": 110, "speed": 140, "attack": 15, "range": 25, "is_worker": False, "radius": 12},
    "Spitter": {"cost": 130, "hp": 80, "speed": 105, "attack": 16, "range": 170, "is_worker": False, "radius": 14}
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

    def move_to(self, target_x, target_y):
        self.target_pos = (target_x, target_y)
        self.target_entity = None
        self.state = "move"

    def attack_target(self, target):
        self.target_entity = target
        self.state = "attack"

    def harvest_node(self, node):
        if not self.is_worker:
            return
        self.target_entity = node
        self.state = "harvest"

    def update(self, dt, game_state):
        if not self.alive:
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.state == "move":
            self._process_movement(dt)

        elif self.state == "attack":
            self._process_attack(dt, game_state)

        elif self.state == "harvest":
            self._process_harvest(dt, game_state)

        elif self.state == "return_resource":
            self._process_return_resource(dt, game_state)

    def _process_movement(self, dt):
        if not self.target_pos:
            self.state = "idle"
            return

        tx, ty = self.target_pos
        dist = math.hypot(tx - self.x, ty - self.y)
        if dist < 5:
            self.x, self.y = tx, ty
            self.target_pos = None
            self.state = "idle"
        else:
            dir_x = (tx - self.x) / dist
            dir_y = (ty - self.y) / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt

    def _process_attack(self, dt, game_state):
        if not self.target_entity or not self.target_entity.alive:
            self.target_entity = None
            self.state = "idle"
            return

        dist = self.distance_to(self.target_entity)
        if dist > self.attack_range + self.radius + self.target_entity.radius:
            # Se rapprocher du cible
            dir_x = (self.target_entity.x - self.x) / dist
            dir_y = (self.target_entity.y - self.y) / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # À portée d'attaque
            if self.attack_cooldown <= 0:
                self.target_entity.take_damage(self.attack_power)
                self.attack_cooldown = 1.0  # Temps de recharge d'attaque

    def _process_harvest(self, dt, game_state):
        if not self.target_entity or not self.target_entity.alive:
            self.target_entity = None
            self.state = "idle"
            return

        dist = self.distance_to(self.target_entity)
        if dist > self.radius + self.target_entity.radius + 10:
            # Se rapprocher du gisement
            dir_x = (self.target_entity.x - self.x) / dist
            dir_y = (self.target_entity.y - self.y) / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # Récolter
            harvested = self.target_entity.harvest(config.DEFAULT_HARVEST_RATE * dt)
            self.carried_resource += harvested
            self.resource_type = self.target_entity.resource_type
            if self.carried_resource >= config.DEFAULT_HARVEST_CAPACITY or not self.target_entity.alive:
                self.state = "return_resource"

    def _process_return_resource(self, dt, game_state):
        # Trouver le centre-ville/ruche le plus proche
        base = self._find_nearest_base(game_state)
        if not base:
            self.state = "idle"
            return

        dist = self.distance_to(base)
        if dist > self.radius + base.radius + 10:
            dir_x = (base.x - self.x) / dist
            dir_y = (base.y - self.y) / dist
            self.x += dir_x * self.speed * dt
            self.y += dir_y * self.speed * dt
        else:
            # Déposer les ressources
            game_state.add_resources(self.owner_id, self.resource_type, self.carried_resource)
            self.carried_resource = 0
            # Repartir récolter
            if self.target_entity and self.target_entity.alive:
                self.state = "harvest"
            else:
                self.state = "idle"

    def _find_nearest_base(self, game_state):
        nearest = None
        min_dist = float('inf')
        base_types = ["TownHall", "Hive"]
        for b in game_state.buildings:
            if b.alive and b.owner_id == self.owner_id and b.building_type in base_types:
                dist = self.distance_to(b)
                if dist < min_dist:
                    min_dist = dist
                    nearest = b
        return nearest
