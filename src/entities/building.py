from src.entities.base_entity import BaseEntity
import config

BUILDING_TYPES = {
    # Medieval
    "TownHall": {"cost": {"wood": 250, "gold": 300}, "hp": 1000, "radius": 45, "build_time": 30, "trainable": ["Worker", "Scout"], "pop_bonus": 10, "attack_power": 0, "range": 286, "vision": 350},
    "House": {"cost": {"wood": 100}, "hp": 250, "radius": 22, "build_time": 10, "trainable": [], "pop_bonus": 5, "vision": 200},
    "Barracks": {"cost": {"wood": 100, "gold": 50}, "hp": 500, "radius": 35, "build_time": 20, "trainable": ["Infantry", "Archer"], "vision": 250},
    "WatchTower": {"cost": {"wood": 60, "gold": 20}, "hp": 350, "radius": 25, "build_time": 12, "attack_power": 0, "range": 0, "trainable": [], "vision": 750},
    "ArrowTower": {"cost": {"wood": 80, "gold": 40}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 20, "range": 260, "trainable": [], "vision": 300},
    "Tower": {"cost": {"wood": 80, "gold": 40}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 20, "range": 260, "trainable": [], "vision": 300},
    "Wall": {"cost": {"wood": 30}, "hp": 750, "radius": 18, "build_time": 8, "trainable": []},
    "WoodStockpile": {"cost": {"wood": 80}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "GoldStockpile": {"cost": {"wood": 80, "gold": 20}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "FoodStockpile": {"cost": {"wood": 80}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "Farm": {"cost": {"wood": 160}, "hp": 300, "radius": 30, "build_time": 15, "trainable": []},
    "Bank": {"cost": {"wood": 200, "gold": 250}, "hp": 450, "radius": 30, "build_time": 25, "trainable": []},
    "Sanctuary": {"cost": {"wood": 150, "gold": 100}, "hp": 400, "radius": 30, "build_time": 20, "trainable": []},
    "Temple": {"cost": {"wood": 180, "gold": 150}, "hp": 400, "radius": 30, "build_time": 20, "trainable": ["Monk"], "vision": 250},

    # Alien
    "Hive": {"cost": {"biomass": 400}, "hp": 1000, "radius": 45, "build_time": 30, "trainable": ["Drone"], "pop_bonus": 10},
    "SpawningPool": {"cost": {"biomass": 150}, "hp": 500, "radius": 35, "build_time": 20, "trainable": ["Swarmer", "Spitter", "Queen"]},
    "SpineCrawler": {"cost": {"biomass": 100}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 24, "range": 234, "trainable": []},
    "BiomassGenerator": {"cost": {"biomass": 300}, "hp": 350, "radius": 30, "build_time": 25, "trainable": []},
    "BiomassStockpile": {"cost": {"biomass": 80}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "EvolutionChamber": {"cost": {"biomass": 200}, "hp": 500, "radius": 32, "build_time": 20, "trainable": []}
}

class Building(BaseEntity):
    def __init__(self, owner_id, faction, building_type, x, y, hp_bonus=0, armor_bonus=0, is_constructed=True, range_bonus=0, wall_length=40, wall_width=18, wall_angle=0.0):
        data = BUILDING_TYPES.get(building_type, {"cost": {"wood": 50}, "hp": 500, "radius": 35, "build_time": 10, "trainable": []})
        max_hp = data["hp"] + hp_bonus

        radius = data["radius"]
        if building_type == "Wall":
            radius = max(wall_length / 2.0, wall_width / 2.0)

        super().__init__(owner_id, faction, x, y, max_hp, radius=radius)
        self.building_type = building_type

        # Wall oriented rectangle parameters
        self.wall_length = wall_length
        self.wall_width = wall_width
        self.wall_angle = wall_angle
        self.is_wall_section = (building_type == "Wall")
        self.cost = data.get("cost", {"wood": 50})
        self.res_type = data.get("res_type", "gold" if faction == config.FACTION_HUMAN else "biomass")
        self.trainable_units = list(data.get("trainable", []))
        self.attack_power = data.get("attack_power", 0)
        self.attack_range = data.get("range", 0) + range_bonus
        self.attack_cooldown = 0
        self.armor = armor_bonus
        self.pop_bonus = data.get("pop_bonus", 0)
        self.vision_radius = data.get("vision", 250) + range_bonus

        # Construction
        self.is_constructed = is_constructed
        self.is_being_built = is_constructed
        self.total_build_time = data.get("build_time", 10)
        self.build_timer = 0.0 if is_constructed else self.total_build_time
        if not is_constructed:
            self.hp = max(1, int(self.max_hp * 0.10))

        # Garrisoning
        self.garrisoned_units = []  # liste d'unités de paysans abrités
        self.max_garrison = 10 if building_type == "TownHall" else (4 if building_type == "Farm" else 0)

        # Rally Point
        self.rally_point = None  # (x, y) tuple
        self.rally_target = None  # Target entity (e.g. ResourceNode)

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

    def build_progress(self, dt, speed_mult=1.0):
        if not self.is_constructed:
            prev_timer = self.build_timer
            self.build_timer -= dt * speed_mult
            if self.total_build_time > 0:
                prev_progress = max(0.0, min(1.0, 1.0 - (prev_timer / float(self.total_build_time))))
                curr_progress = max(0.0, min(1.0, 1.0 - (self.build_timer / float(self.total_build_time))))

                prev_target_hp = int(self.max_hp * (0.10 + 0.90 * prev_progress))
                curr_target_hp = int(self.max_hp * (0.10 + 0.90 * curr_progress))
                hp_delta = max(0, curr_target_hp - prev_target_hp)

                self.hp = min(self.max_hp, self.hp + hp_delta)

            if self.build_timer <= 0:
                self.is_constructed = True
                self.build_timer = 0.0
                self.hp = self.max_hp

    def take_damage(self, amount, attacker=None, game_state=None):
        dmg = amount
        if not self.is_constructed:
            dmg = amount * 2.5
        effective_damage = max(1, dmg - self.armor)
        super().take_damage(effective_damage, attacker=attacker, game_state=game_state)

    def queue_unit(self, unit_type, train_time=None, game_state=None):
        if not self.is_constructed:
            return False
        if train_time is None:
            from src.entities.unit import UNIT_TYPES
            train_time = UNIT_TYPES.get(unit_type, {}).get("train_time", 5)

        if game_state and hasattr(game_state, 'save_manager'):
            upgrades = game_state.save_manager.data.get("upgrades", {})
            if unit_type == "Worker" and upgrades.get("worker_spawn_speed"):
                train_time *= 0.90
            elif unit_type in ["Infantry", "Swarmer"] and upgrades.get("melee_spawn_speed"):
                train_time *= 0.90
            elif unit_type in ["Archer", "Spitter"] and upgrades.get("archer_spawn_speed"):
                train_time *= 0.90

        self.production_queue.append({"unit_type": unit_type, "time_remaining": float(train_time), "total_time": float(train_time)})
        return True

    def update(self, dt, game_state=None):
        if not self.alive:
            return None

        # Gestion de la construction du bâtiment
        if not self.is_constructed:
            if getattr(self, 'is_being_built', False):
                self.build_progress(dt, speed_mult=1.0)
            return None

        # Bank passive gold generation
        if self.building_type == "Bank" and game_state:
            game_state.add_resources(self.owner_id, "gold", 3.0 * dt)

        # Sanctuary troop healing (Base 8 HP/sec, or 12 HP/sec with sanctuary_boost upgrade, range 150 or 210)
        if self.building_type == "Sanctuary" and game_state:
            upgrades = game_state.save_manager.data.get("upgrades", {}) if hasattr(game_state, 'save_manager') else {}
            has_boost = upgrades.get("sanctuary_boost", 0) >= 1
            heal_range = 210 if has_boost else 150
            heal_rate = 12.0 if has_boost else 8.0

            for u in game_state.units:
                if u.alive and u.owner_id == self.owner_id and u.hp < u.max_hp:
                    if self.distance_to(u) <= heal_range:
                        u.hp = min(u.max_hp, u.hp + heal_rate * dt)
                        break

        # Mettre à jour la file de production
        produced_unit = None
        if self.production_queue:
            item = self.production_queue[0]
            item["time_remaining"] -= dt
            if item["time_remaining"] <= 0:
                produced_unit = item["unit_type"]
                self.production_queue.pop(0)

        # Farm food generation
        if self.building_type == "Farm" and self.garrisoned_units and game_state:
            harvest_rate = config.DEFAULT_HARVEST_RATE * 0.25
            food_collected = len(self.garrisoned_units) * harvest_rate * dt
            game_state.add_resources(self.owner_id, "food", food_collected)

        # Town Hall (Forum) multi-projectile attack logic
        if self.building_type == "TownHall" and game_state:
            num_projectiles = len(self.garrisoned_units)
            upgrades = game_state.save_manager.data.get("upgrades", {}) if hasattr(game_state, 'save_manager') and game_state.save_manager else {}
            if upgrades.get("forum_passive_arrow"):
                num_projectiles += 1

            if num_projectiles > 0 and self.attack_range > 0:
                self.attack_cooldown -= dt
                if self.attack_cooldown <= 0:
                    target = self.find_target(game_state)
                    if target:
                        from src.entities.projectile import Projectile
                        r = self.radius * 0.75
                        # 4 corners offset vectors
                        corners = [
                            (-r, -r),  # Top-left corner
                            (r, -r),   # Top-right corner
                            (r, r),    # Bottom-right corner
                            (-r, r)    # Bottom-left corner
                        ]
                        base_damage = 12  # Each worker adds 1 projectile with fixed damage 12

                        for i in range(num_projectiles):
                            corner_offset = corners[i % 4]
                            spawn_x = self.x + corner_offset[0]
                            spawn_y = self.y + corner_offset[1]
                            phase_delay = i * 0.08  # Slight phase offset delay between arrows

                            proj = Projectile(spawn_x, spawn_y, target, base_damage, speed=500, owner_id=self.owner_id, projectile_type="arrow", delay=phase_delay, attacker_entity=self)
                            if hasattr(game_state, 'projectiles'):
                                game_state.projectiles.append(proj)
                            else:
                                target.take_damage(base_damage, attacker=self, game_state=game_state)
                        self.attack_cooldown = 1.0

        elif self.attack_power > 0 and game_state and self.building_type != "TownHall":
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                target = self.find_target(game_state)
                if target:
                    from src.entities.projectile import Projectile
                    p_type = "arrow"

                    upgrades = game_state.save_manager.data.get("upgrades", {}) if hasattr(game_state, 'save_manager') and game_state.save_manager else {}
                    num_proj = 2 if (upgrades.get("tower_extra_projectile") and self.building_type in ["ArrowTower", "Tower", "WatchTower", "SpineCrawler"]) else 1

                    for i in range(num_proj):
                        delay = i * 0.08
                        proj = Projectile(self.x, self.y, target, self.attack_power, speed=500, owner_id=self.owner_id, projectile_type=p_type, delay=delay, attacker_entity=self)
                        if hasattr(game_state, 'projectiles'):
                            game_state.projectiles.append(proj)
                        else:
                            target.take_damage(self.attack_power, attacker=self, game_state=game_state)
                    self.attack_cooldown = 1.0

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
