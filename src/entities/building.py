from src.entities.base_entity import BaseEntity
import config

BUILDING_TYPES = {
    # Medieval
    "TownHall": {"cost": {"wood": 250, "gold": 300}, "hp": 1000, "radius": 45, "build_time": 30, "trainable": ["Worker", "Scout"], "pop_bonus": 10, "attack_power": 0, "range": 220, "vision": 350},
    "House": {"cost": {"wood": 60}, "hp": 250, "radius": 22, "build_time": 10, "trainable": [], "pop_bonus": 5, "vision": 200},
    "Barracks": {"cost": {"wood": 100, "gold": 50}, "hp": 500, "radius": 35, "build_time": 20, "trainable": ["Infantry", "Archer"], "vision": 250},
    "Tower": {"cost": {"wood": 80, "gold": 40}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 0, "range": 0, "trainable": [], "vision": 700},
    "ArrowTower": {"cost": {"wood": 100, "gold": 60}, "hp": 450, "radius": 25, "build_time": 18, "attack_power": 16, "range": 220, "trainable": [], "vision": 300},
    "Wall": {"cost": {"wood": 30}, "hp": 750, "radius": 18, "build_time": 8, "trainable": []},  # 3x HP (750)
    "WoodStockpile": {"cost": {"wood": 80}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "GoldStockpile": {"cost": {"wood": 80, "gold": 20}, "hp": 350, "radius": 25, "build_time": 12, "trainable": []},
    "Farm": {"cost": {"wood": 100}, "hp": 300, "radius": 30, "build_time": 15, "trainable": []},
    "Bank": {"cost": {"wood": 300, "gold": 300}, "hp": 450, "radius": 30, "build_time": 25, "trainable": []},
    "HealingShrine": {"cost": {"wood": 200, "gold": 150}, "hp": 400, "radius": 30, "build_time": 20, "trainable": []},

    # Alien
    "Hive": {"cost": {"biomass": 400}, "hp": 1000, "radius": 45, "build_time": 30, "trainable": ["Drone"], "pop_bonus": 10},
    "SpawningPool": {"cost": {"biomass": 150}, "hp": 500, "radius": 35, "build_time": 20, "trainable": ["Swarmer", "Spitter"]},
    "SpineCrawler": {"cost": {"biomass": 100}, "hp": 400, "radius": 25, "build_time": 16, "attack_power": 18, "range": 180, "trainable": []},
    "BiomassGenerator": {"cost": {"biomass": 300}, "hp": 350, "radius": 30, "build_time": 25, "trainable": []}
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
        self.total_build_time = data.get("build_time", 10)
        self.build_timer = 0.0 if is_constructed else self.total_build_time
        # Initial HP for unconstructed buildings: 10% HP
        if not is_constructed:
            self.hp = max(1, int(self.max_hp * 0.10))

        # Alien auto-construction when worker morphs/sacrifices
        self.auto_building = False

        # Garrisoning
        self.garrisoned_units = []
        self.max_garrison = 10 if building_type == "TownHall" else 0

        # Rally Point
        self.rally_point = None
        self.rally_target = None

        # Production queue
        self.production_queue = []

        # Healing shrine timer
        self.heal_cooldown = 0.0

    def garrison_unit(self, unit):
        if len(self.garrisoned_units) < self.max_garrison:
            unit.alive = False
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
            if self.build_timer <= 0:
                self.is_constructed = True
                self.build_timer = 0.0
                self.hp = self.max_hp
            else:
                # Progress ratio from 0.10 to 1.0
                progress_ratio = 0.10 + 0.90 * (1.0 - self.build_timer / max(0.001, self.total_build_time))
                self.hp = max(self.hp, int(self.max_hp * progress_ratio))

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

        # Auto construction (e.g., Alien building sacrificed Drone)
        if not self.is_constructed:
            if self.auto_building:
                self.build_progress(dt, speed_mult=1.0)
            return None

        # Bank passive gold income (yields gold passively every second)
        if self.building_type == "Bank" and game_state:
            game_state.add_resources(self.owner_id, "gold", 4.0 * dt)

        # Healing Shrine (Heals 1 friendly unit in low range 120 at 8 HP/sec)
        if self.building_type == "HealingShrine" and game_state:
            heal_range = 120
            heal_amount = 8.0 * dt
            # Find 1 injured friendly unit nearby
            injured = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id and u.hp < u.max_hp and self.distance_to(u) <= heal_range]
            if injured:
                # Heal lowest HP ratio unit
                target_heal = min(injured, key=lambda u: u.hp / max(1.0, u.max_hp))
                target_heal.hp = min(target_heal.max_hp, target_heal.hp + heal_amount)

        # Mettre à jour la file de production
        produced_unit = None
        if self.production_queue:
            item = self.production_queue[0]
            item["time_remaining"] -= dt
            if item["time_remaining"] <= 0:
                produced_unit = item["unit_type"]
                self.production_queue.pop(0)

        # Effective attack power (TownHall garrison arrows / passive arrow)
        effective_attack = self.attack_power
        if self.building_type == "TownHall":
            num_arrows = len(self.garrisoned_units)
            upgrades = game_state.save_manager.data.get("upgrades", {}) if game_state and hasattr(game_state, 'save_manager') else {}
            if upgrades.get("forum_passive_arrow"):
                num_arrows += 1
            effective_attack = num_arrows * 12

        if effective_attack > 0 and game_state:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                target = self.find_target(game_state)
                if target:
                    # Ranged projectile shot handled in game_state / projectile system
                    if hasattr(game_state, 'spawn_projectile'):
                        proj_type = "ballista" if self.building_type == "TownHall" else ("arrow" if self.building_type in ["Tower", "ArrowTower"] else "spitter")
                        game_state.spawn_projectile(self, target, effective_attack, proj_type=proj_type)
                    else:
                        target.take_damage(effective_attack)
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
