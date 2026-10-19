from src.entities.base_entity import BaseEntity
import config

BUILDING_TYPES = {
    # Medieval
    "TownHall": {"cost": {"wood": 250, "gold": 300}, "hp": 1000, "radius": 45, "build_time": 30, "trainable": ["Worker"], "pop_bonus": 10, "attack_power": 0, "range": 220},
    "House": {"cost": {"wood": 60}, "hp": 250, "radius": 22, "build_time": 10, "trainable": [], "pop_bonus": 5},
    "Barracks": {"cost": {"wood": 100, "gold": 50}, "hp": 500, "radius": 35, "build_time": 20, "trainable": ["Infantry", "Archer"]},
    "Tower": {"cost": {"wood": 80, "gold": 40}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 15, "range": 200, "trainable": []},
    "Wall": {"cost": {"wood": 30}, "hp": 250, "radius": 18, "build_time": 8, "trainable": []},
    "WoodStockpile": {"cost": {"wood": 80}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "GoldStockpile": {"cost": {"wood": 80, "gold": 20}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "Farm": {"cost": {"wood": 100}, "hp": 300, "radius": 30, "build_time": 15, "trainable": []},

    # Alien
    "Hive": {"cost": {"biomass": 400}, "hp": 1000, "radius": 45, "build_time": 30, "trainable": ["Drone"], "pop_bonus": 10},
    "SpawningPool": {"cost": {"biomass": 150}, "hp": 500, "radius": 35, "build_time": 20, "trainable": ["Swarmer", "Spitter"]},
    "SpineCrawler": {"cost": {"biomass": 100}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 18, "range": 180, "trainable": []}
}

class Building(BaseEntity):
    def __init__(self, owner_id, faction, building_type, x, y, hp_bonus=0, armor_bonus=0, is_constructed=True):
        data = BUILDING_TYPES.get(building_type, {"cost": {"wood": 50}, "hp": 500, "radius": 35, "build_time": 10, "trainable": []})
        max_hp = data["hp"] + hp_bonus
        super().__init__(owner_id, faction, x, y, max_hp, radius=data["radius"])
        self.building_type = building_type
        self.cost = data.get("cost", {"wood": 50})
        self.res_type = data.get("res_type", "gold" if faction == config.FACTION_HUMAN else "biomass")
        self.trainable_units = list(data.get("trainable", []))
        self.attack_power = data.get("attack_power", 0)
        self.attack_range = data.get("range", 0)
        self.attack_cooldown = 0
        self.armor = armor_bonus
        self.pop_bonus = data.get("pop_bonus", 0)

        # Construction
        self.is_constructed = is_constructed
        self.total_build_time = data.get("build_time", 10)
        self.build_timer = 0.0 if is_constructed else self.total_build_time

        # Garrisoning
        self.garrisoned_units = []  # liste d'unités de paysans abrités
        self.max_garrison = 10 if building_type == "TownHall" else 0

        # File de production
        self.production_queue = []  # liste de dicts {"unit_type": str, "time_remaining": float, "total_time": float}

    def garrison_unit(self, unit):
        if len(self.garrisoned_units) < self.max_garrison:
            unit.alive = False  # temporairement masquée/hors carte
            unit.garrisoned_in = self
            self.garrisoned_units.append(unit)
            return True
        return False

    def ungarrison_all(self, game_state):
        released = list(self.garrisoned_units)
        self.garrisoned_units.clear()
        for idx, u in enumerate(released):
            u.alive = True
            u.garrisoned_in = None
            u.x = self.x + (idx + 1) * 15
            u.y = self.y + self.radius + 20
            u.state = "idle"
            if u not in game_state.units:
                game_state.units.append(u)
        return released

    def take_damage(self, amount):
        effective_damage = max(1, amount - self.armor)
        super().take_damage(effective_damage)

    def queue_unit(self, unit_type, train_time=None):
        if not self.is_constructed:
            return False
        if train_time is None:
            from src.entities.unit import UNIT_TYPES
            train_time = UNIT_TYPES.get(unit_type, {}).get("train_time", 5)
        self.production_queue.append({"unit_type": unit_type, "time_remaining": float(train_time), "total_time": float(train_time)})
        return True

    def update(self, dt, game_state=None):
        if not self.alive:
            return None

        # Gestion de la construction du bâtiment
        if not self.is_constructed:
            self.build_timer -= dt
            if self.build_timer <= 0:
                self.is_constructed = True
                self.build_timer = 0.0
            return None

        # Mettre à jour la file de production
        produced_unit = None
        if self.production_queue:
            item = self.production_queue[0]
            item["time_remaining"] -= dt
            if item["time_remaining"] <= 0:
                produced_unit = item["unit_type"]
                self.production_queue.pop(0)

        # Effective attack power (each garrisoned peasant adds 1 arrow / +12 damage)
        effective_attack = self.attack_power
        if self.building_type == "TownHall":
            num_arrows = len(self.garrisoned_units)
            effective_attack = num_arrows * 12

        if effective_attack > 0 and game_state:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                # Trouver un ennemi à portée
                target = self.find_target(game_state)
                if target:
                    target.take_damage(effective_attack)
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
