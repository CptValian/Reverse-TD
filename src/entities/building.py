from src.entities.base_entity import BaseEntity
import config

BUILDING_TYPES = {
    # Médiéval
    "TownHall": {"cost": 400, "hp": 1000, "radius": 45, "build_time": 0, "trainable": ["Worker"]},
    "Barracks": {"cost": 150, "hp": 500, "radius": 35, "build_time": 10, "trainable": ["Infantry", "Archer"]},
    "Tower": {"cost": 100, "hp": 400, "radius": 25, "build_time": 8, "attack_power": 15, "range": 200, "trainable": []},

    # Alien
    "Hive": {"cost": 400, "hp": 1000, "radius": 45, "build_time": 0, "trainable": ["Drone"]},
    "SpawningPool": {"cost": 150, "hp": 500, "radius": 35, "build_time": 10, "trainable": ["Swarmer", "Spitter"]},
    "SpineCrawler": {"cost": 100, "hp": 400, "radius": 25, "build_time": 8, "attack_power": 18, "range": 180, "trainable": []}
}

class Building(BaseEntity):
    def __init__(self, owner_id, faction, building_type, x, y, hp_bonus=0, armor_bonus=0):
        data = BUILDING_TYPES.get(building_type, {"hp": 500, "radius": 35, "trainable": []})
        max_hp = data["hp"] + hp_bonus
        super().__init__(owner_id, faction, x, y, max_hp, radius=data["radius"])
        self.building_type = building_type
        self.trainable_units = data.get("trainable", [])
        self.attack_power = data.get("attack_power", 0)
        self.attack_range = data.get("range", 0)
        self.attack_cooldown = 0
        self.armor = armor_bonus

        # File de production
        self.production_queue = []  # liste de tuples (unit_type, time_remaining, total_time)

    def take_damage(self, amount):
        effective_damage = max(1, amount - self.armor)
        super().take_damage(effective_damage)

    def queue_unit(self, unit_type, train_time=5):
        self.production_queue.append({"unit_type": unit_type, "time_remaining": train_time, "total_time": train_time})

    def update(self, dt, game_state=None):
        # Mettre à jour la file de production
        produced_unit = None
        if self.production_queue:
            item = self.production_queue[0]
            item["time_remaining"] -= dt
            if item["time_remaining"] <= 0:
                produced_unit = item["unit_type"]
                self.production_queue.pop(0)

        # Attaque pour les tours de défense
        if self.attack_power > 0 and game_state:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                # Trouver un ennemi à portée
                target = self.find_target(game_state)
                if target:
                    target.take_damage(self.attack_power)
                    self.attack_cooldown = 1.0  # Attaque chaque seconde

        return produced_unit

    def find_target(self, game_state):
        best_target = None
        min_dist = self.attack_range
        for entity in game_state.units + game_state.buildings:
            if entity.alive and entity.owner_id != self.owner_id:
                dist = self.distance_to(entity)
                if dist <= min_dist:
                    min_dist = dist
                    best_target = entity
        return best_target
