import random
import math
from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
from src.entities.unit import Unit
from src.entities.building import Building, BUILDING_TYPES
from src.entities.unit import UNIT_TYPES
import config

class AIController:
    def __init__(self, owner_id, faction=config.FACTION_ALIEN, difficulty=1):
        self.owner_id = owner_id
        self.faction = faction
        try:
            self.difficulty = int(difficulty)
        except (ValueError, TypeError):
            self.difficulty = 1
        self.config = AI_DIFFICULTY_LEVELS.get(self.difficulty, AI_DIFFICULTY_LEVELS[1])
        self.timer_wave = 0.0
        self.timer_macro = 0.0
        self.spawn_point = None

    def update(self, dt, game_state):
        self.timer_wave += dt
        self.timer_macro += dt

        # Continuous passive resource influx scaling with difficulty
        res_type = "biomass" if self.faction == config.FACTION_ALIEN else "gold"
        res_boost = 12 * self.config.get("resource_multiplier", 1.0) * dt
        if hasattr(game_state, 'add_resources'):
            game_state.add_resources(self.owner_id, res_type, res_boost)
            if self.faction == config.FACTION_HUMAN:
                game_state.add_resources(self.owner_id, "wood", res_boost * 0.8)

        ai_units = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id]
        ai_buildings = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id]

        # Determine home base spawn location
        bases = [b for b in ai_buildings if b.building_type in ["Hive", "TownHall"]]
        if bases:
            self.spawn_point = (bases[0].x, bases[0].y)
        elif not self.spawn_point and ai_units:
            self.spawn_point = (ai_units[0].x, ai_units[0].y)

        # 1. Base Reconstruction if Main Base was destroyed
        if not bases and self.spawn_point:
            main_b_type = "Hive" if self.faction == config.FACTION_ALIEN else "TownHall"
            cost_dict = BUILDING_TYPES.get(main_b_type, {}).get("cost", {res_type: 300})
            bx, by = self.spawn_point
            if game_state.can_place_building(main_b_type, bx, by):
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, main_b_type, bx, by, is_constructed=False)
                    game_state.buildings.append(nb)

        # 2. Worker Management & Harvesting
        ai_workers = [u for u in ai_units if u.is_worker]
        idle_workers = [w for w in ai_workers if w.state == "idle"]
        resources = [r for r in game_state.resources if r.alive]

        if idle_workers and resources:
            for w in idle_workers:
                nearest = min(resources, key=lambda r: w.distance_to(r))
                w.harvest_node(nearest)

        # 3. Macro Economy (Continuous Worker Training)
        max_workers = self.config.get("max_workers", 8)
        if len(ai_workers) < max_workers and bases:
            for base in bases:
                if base.is_constructed and len(base.production_queue) < 2:
                    unit_to_train = "Drone" if self.faction == config.FACTION_ALIEN else "Worker"
                    cost_dict = UNIT_TYPES.get(unit_to_train, {}).get("cost", {res_type: 50})
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        base.queue_unit(unit_to_train)

        # 4. Production Facilities (SpawningPools / Barracks Expansion)
        production_blds = [b for b in ai_buildings if b.building_type in ["SpawningPool", "Barracks"]]
        target_prod_blds = 3 if self.difficulty >= 4 else (2 if self.difficulty >= 2 else 1)

        if len(production_blds) < target_prod_blds and self.spawn_point:
            prod_type = "SpawningPool" if self.faction == config.FACTION_ALIEN else "Barracks"
            cost_dict = BUILDING_TYPES.get(prod_type, {}).get("cost", {res_type: 150})

            offset_x = random.randint(-120, 120)
            offset_y = random.randint(-120, 120)
            bx = self.spawn_point[0] + offset_x
            by = self.spawn_point[1] + offset_y

            if game_state.can_place_building(prod_type, bx, by):
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, prod_type, bx, by, is_constructed=False)
                    game_state.buildings.append(nb)

        # 5. Defensive Turrets / Spine Crawlers
        if self.config.get("can_build_defenses", True):
            defenses = [b for b in ai_buildings if b.building_type in ["SpineCrawler", "Tower"]]
            target_def = 3 if self.difficulty >= 4 else 1

            if len(defenses) < target_def and self.spawn_point:
                def_type = "SpineCrawler" if self.faction == config.FACTION_ALIEN else "Tower"
                cost_dict = BUILDING_TYPES.get(def_type, {}).get("cost", {res_type: 100})

                dx = self.spawn_point[0] + random.choice([-90, 90])
                dy = self.spawn_point[1] + random.choice([-90, 90])

                if game_state.can_place_building(def_type, dx, dy):
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        nb = Building(self.owner_id, self.faction, def_type, dx, dy, is_constructed=False)
                        game_state.buildings.append(nb)

        # 6. Army Unit Queueing (Swarmer & Spitter Tech)
        army_units = [u for u in ai_units if not u.is_worker]
        for prod in production_blds:
            if prod.is_constructed and len(prod.production_queue) < 3:
                available_troops = ["Swarmer"] if self.faction == config.FACTION_ALIEN else ["Infantry"]
                if self.config.get("can_tech_ranged", True):
                    if self.faction == config.FACTION_ALIEN:
                        available_troops.append("Spitter")
                    else:
                        available_troops.append("Archer")

                chosen_unit = random.choice(available_troops)
                cost_dict = UNIT_TYPES.get(chosen_unit, {}).get("cost", {res_type: 60})
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    prod.queue_unit(chosen_unit)

        # 7. Defense Response when base is under attack
        player_units = [u for u in game_state.units if u.alive and u.owner_id != self.owner_id]
        if self.spawn_point and player_units:
            nearby_threats = [u for u in player_units if math.hypot(u.x - self.spawn_point[0], u.y - self.spawn_point[1]) < 450]
            if nearby_threats:
                closest_threat = min(nearby_threats, key=lambda u: math.hypot(u.x - self.spawn_point[0], u.y - self.spawn_point[1]))
                for u in army_units:
                    if u.state == "idle":
                        u.attack_target(closest_threat)

        # 8. Continuous Strategic Wave Attacks
        wave_interval = self.config.get("attack_wave_interval", 45)
        min_wave_size = 2 if self.difficulty == 1 else 4

        if self.timer_wave >= wave_interval or len(army_units) >= self.config.get("max_army_size", 15):
            if len(army_units) >= min_wave_size:
                self.timer_wave = 0.0

                # Priority targeting: Workers > Production Buildings > Town Hall / Hive > Any unit
                player_targets = [e for e in game_state.buildings + game_state.units if e.alive and e.owner_id != self.owner_id]
                if player_targets:
                    p_workers = [e for e in player_targets if getattr(e, 'is_worker', False)]
                    p_townhalls = [e for e in player_targets if getattr(e, 'building_type', None) in ["TownHall", "Hive"]]
                    p_buildings = [e for e in player_targets if hasattr(e, 'building_type')]

                    if p_workers and random.random() < 0.4:
                        target = random.choice(p_workers)
                    elif p_townhalls and random.random() < 0.5:
                        target = p_townhalls[0]
                    elif p_buildings:
                        target = random.choice(p_buildings)
                    else:
                        target = random.choice(player_targets)

                    for u in army_units:
                        u.attack_move_to(target.x, target.y)
