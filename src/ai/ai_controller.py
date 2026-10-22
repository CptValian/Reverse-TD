import random
import math
from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
from src.entities.unit import Unit
from src.entities.building import Building, BUILDING_TYPES
from src.entities.unit import UNIT_TYPES
import config

class BaseAIController:
    def __init__(self, owner_id, faction, difficulty=1):
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
        self.reflection_interval = 0.5
        self.reflection_timer = self.reflection_interval

    def _find_valid_building_position(self, game_state, building_type, center_x, center_y, min_building_gap=50, min_resource_gap=75, search_radius=300):
        """Searches for a building placement position around center that maintains spacious clearance
        from other buildings and resource nodes so paths stay wide open and uncluttered."""
        radius = BUILDING_TYPES.get(building_type, {}).get("radius", 35)

        step_r = 30
        for r in range(0, search_radius + 1, step_r):
            num_angles = max(8, int(2 * math.pi * max(1, r) / 25)) if r > 0 else 1
            angles = [i * (2 * math.pi / num_angles) for i in range(num_angles)] if r > 0 else [0.0]
            random.shuffle(angles)

            for angle in angles:
                bx = center_x + math.cos(angle) * r
                by = center_y + math.sin(angle) * r

                if not game_state.can_place_building(building_type, bx, by, owner_id=self.owner_id):
                    continue

                too_close_bld = False
                for b in game_state.buildings:
                    if b.alive:
                        dist_sq = (b.x - bx)**2 + (b.y - by)**2
                        req_dist = b.radius + radius + min_building_gap
                        if dist_sq < req_dist * req_dist:
                            too_close_bld = True
                            break
                if too_close_bld:
                    continue

                too_close_res = False
                for res in game_state.resources:
                    if res.alive:
                        dist_sq = (res.x - bx)**2 + (res.y - by)**2
                        req_dist = res.radius + radius + min_resource_gap
                        if dist_sq < req_dist * req_dist:
                            too_close_res = True
                            break
                if too_close_res:
                    continue

                if building_type in ["Barracks", "SpawningPool", "Hive", "TownHall"]:
                    exit_clear = False
                    for exit_angle in [0, math.pi/2, math.pi, 3*math.pi/2, math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
                        ex = bx + math.cos(exit_angle) * (radius + 40)
                        ey = by + math.sin(exit_angle) * (radius + 40)
                        if 0 <= ex <= config.MAP_WIDTH and 0 <= ey <= config.MAP_HEIGHT:
                            blocked = any(b.alive and math.hypot(b.x - ex, b.y - ey) < b.radius + 15 for b in game_state.buildings)
                            if not blocked:
                                exit_clear = True
                                break
                    if not exit_clear:
                        continue

                return (bx, by)

        return None

    def _check_enemy(self, owner1, owner2, game_state):
        if hasattr(game_state, 'are_enemies'):
            return game_state.are_enemies(owner1, owner2)
        return owner1 != owner2

    def notify_under_attack(self, attacker, target, game_state):
        if not attacker or not getattr(attacker, 'alive', True):
            return
        ai_units = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id]
        army_units = [u for u in ai_units if not u.is_worker]
        for u in army_units:
            if u.state in ["idle", "move"] or (u.target_entity and not u.target_entity.alive):
                if u.distance_to(target) <= 900 or u.distance_to(attacker) <= 900:
                    u.attack_target(attacker, game_state)

    def _handle_common_combat_tactics(self, dt, game_state, ai_units):
        army_units = [u for u in ai_units if not u.is_worker]

        # Determine home spawn
        bases = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id and b.building_type in ["Hive", "TownHall"]]
        if bases:
            self.spawn_point = (bases[0].x, bases[0].y)
        elif not self.spawn_point and ai_units:
            self.spawn_point = (ai_units[0].x, ai_units[0].y)

        enemy_units = [u for u in game_state.units if u.alive and self._check_enemy(self.owner_id, u.owner_id, game_state)]
        enemy_targets = [e for e in game_state.buildings + game_state.units if e.alive and self._check_enemy(self.owner_id, e.owner_id, game_state)]

        # 1. Base Defense Call against encroaching threats
        if self.spawn_point and enemy_units:
            nearby_threats = [u for u in enemy_units if math.hypot(u.x - self.spawn_point[0], u.y - self.spawn_point[1]) < 650]
            if nearby_threats:
                closest_threat = min(nearby_threats, key=lambda u: math.hypot(u.x - self.spawn_point[0], u.y - self.spawn_point[1]))
                for u in army_units:
                    if u.state in ["idle", "move"] or (u.target_entity and not u.target_entity.alive):
                        u.attack_target(closest_threat, game_state)

        # 2. Tactical Retreat for heavily wounded troops
        if self.spawn_point:
            for u in army_units:
                if u.hp < u.max_hp * 0.35 and u.state == "attack":
                    u.move_to(self.spawn_point[0] + random.randint(-50, 50), self.spawn_point[1] + random.randint(-50, 50), game_state)

        # 3. Strategic Attack Execution
        total_ai_power = sum([u.attack_power + u.hp * 0.1 for u in army_units])
        total_player_power = sum([u.attack_power + u.hp * 0.1 for u in enemy_units]) + 1.0
        force_ratio = total_ai_power / total_player_power

        p_workers = [e for e in enemy_targets if getattr(e, 'is_worker', False)]
        p_townhalls = [e for e in enemy_targets if getattr(e, 'building_type', None) in ["TownHall", "Hive"]]
        p_defenses = [e for e in enemy_targets if getattr(e, 'building_type', None) in ["WatchTower", "ArrowTower", "Tower", "SpineCrawler"]]
        p_buildings = [e for e in enemy_targets if hasattr(e, 'building_type')]

        army_threshold = min(12, max(4, int(self.config.get("max_army_size", 12) * 0.8)))

        should_strike = False
        if len(army_units) >= army_threshold and force_ratio >= 1.0:
            should_strike = True
        elif len(army_units) >= army_threshold + 3:
            should_strike = True
        elif len(army_units) >= 3 and p_workers and not enemy_units:
            should_strike = True

        if should_strike and enemy_targets:
            idle_or_moving_army = [
                u for u in army_units
                if u.state == "idle" or (u.state == "move" and not getattr(u, 'attack_move_mode', False)) or not u.target_entity or not u.target_entity.alive
            ]
            if idle_or_moving_army:
                if p_townhalls and random.random() < 0.5:
                    target = p_townhalls[0]
                elif p_defenses and random.random() < 0.3:
                    target = random.choice(p_defenses)
                elif p_workers and random.random() < 0.4:
                    target = min(p_workers, key=lambda w: min([math.hypot(w.x - u.x, w.y - u.y) for u in idle_or_moving_army] or [9999]))
                elif p_buildings:
                    target = min(p_buildings, key=lambda b: min([math.hypot(b.x - u.x, b.y - u.y) for u in idle_or_moving_army] or [9999]))
                else:
                    target = random.choice(enemy_targets)

                if len(idle_or_moving_army) >= 6:
                    mid = len(idle_or_moving_army) // 2
                    group1 = idle_or_moving_army[:mid]
                    group2 = idle_or_moving_army[mid:]
                    flank1 = (target.x - 140, target.y - 140)
                    flank2 = (target.x + 140, target.y + 140)

                    for u in group1:
                        u.attack_move_to(flank1[0], flank1[1], game_state)
                    for u in group2:
                        u.attack_move_to(flank2[0], flank2[1], game_state)
                else:
                    for u in idle_or_moving_army:
                        u.attack_move_to(target.x, target.y, game_state)


class AlienAIController(BaseAIController):
    def __init__(self, owner_id, difficulty=1):
        super().__init__(owner_id, faction=config.FACTION_ALIEN, difficulty=difficulty)
        self.hive_enrage_cooldown = 0.0
        self.hive_enrage_active_timer = 0.0
        self.evo_upgrades = {
            "troop_hp": 0,
            "swarmer_discount": 0,
            "bio_gen_boost": 0
        }

    def _assign_builder_to_building(self, nb, ai_units, game_state):
        if not nb or getattr(nb, 'is_constructed', True) or getattr(nb, 'is_being_built', False):
            return
        idle_builders = [u for u in ai_units if u.alive and u.is_worker and u.state == "idle"]
        if idle_builders:
            builder = min(idle_builders, key=lambda u: u.distance_to(nb))
            builder.construct_building(nb, game_state)
        elif len([u for u in ai_units if u.alive and u.is_worker]) > 1:
            active_workers = [u for u in ai_units if u.alive and u.is_worker and u.state in ["harvest", "return_resource"]]
            if active_workers:
                builder = min(active_workers, key=lambda u: u.distance_to(nb))
                builder.construct_building(nb, game_state)

    def update(self, dt, game_state):
        self.timer_wave += dt
        self.timer_macro += dt
        self.reflection_timer += dt

        if self.hive_enrage_cooldown > 0:
            self.hive_enrage_cooldown -= dt
        if self.hive_enrage_active_timer > 0:
            self.hive_enrage_active_timer -= dt

        # Continuous passive biomass influx scaling with difficulty
        res_boost = 12 * self.config.get("resource_multiplier", 1.0) * dt
        if hasattr(game_state, 'add_resources'):
            game_state.add_resources(self.owner_id, "biomass", res_boost)

        ai_buildings = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id]
        bio_gens = [b for b in ai_buildings if b.building_type == "BiomassGenerator" and b.is_constructed]
        if bio_gens and hasattr(game_state, 'add_resources'):
            gen_rate = 5 * (1.0 + 0.05 * self.evo_upgrades["bio_gen_boost"])
            game_state.add_resources(self.owner_id, "biomass", gen_rate * len(bio_gens) * dt)

        if self.reflection_timer < self.reflection_interval:
            return
        self.reflection_timer = 0.0

        ai_units = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id]

        # Hive Enrage Ability Activation
        enrage_lvl = self.config.get("hive_enrage_level", 0)
        if enrage_lvl > 0 and self.hive_enrage_cooldown <= 0:
            hives = [b for b in ai_buildings if b.building_type == "Hive" and b.is_constructed]
            if hives:
                self.hive_enrage_cooldown = 60.0
                self.hive_enrage_active_timer = 5.0
                bonus_pct = 0.10 if enrage_lvl == 1 else 0.20
                for u in ai_units:
                    if not u.is_worker:
                        u.speed = int(u.speed * (1.0 + bonus_pct))
                        u.attack_power = int(u.attack_power * (1.0 + bonus_pct))
                        u._enraged = True

        if self.hive_enrage_active_timer <= 0:
            enrage_lvl = self.config.get("hive_enrage_level", 0)
            bonus_pct = 0.10 if enrage_lvl == 1 else 0.20
            for u in ai_units:
                if getattr(u, '_enraged', False):
                    u.speed = int(u.speed / (1.0 + bonus_pct))
                    u.attack_power = int(u.attack_power / (1.0 + bonus_pct))
                    u._enraged = False

        bases = [b for b in ai_buildings if b.building_type == "Hive"]
        if bases:
            self.spawn_point = (bases[0].x, bases[0].y)

        # 1. Base Reconstruction if Hive was destroyed
        if not bases and self.spawn_point:
            cost_dict = BUILDING_TYPES.get("Hive", {}).get("cost", {"biomass": 300})
            pos = self._find_valid_building_position(game_state, "Hive", self.spawn_point[0], self.spawn_point[1], min_building_gap=60, min_resource_gap=80)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "Hive", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_builder_to_building(nb, ai_units, game_state)

        # 2. Worker Management & Harvesting (with node load balancing)
        ai_workers = [u for u in ai_units if u.is_worker]
        idle_workers = [w for w in ai_workers if w.state == "idle"]
        resources = [r for r in game_state.resources if r.alive and r.resource_type == "biomass"]

        if idle_workers and resources:
            node_counts = {id(r): 0 for r in resources}
            for w in ai_workers:
                if w.target_entity and id(w.target_entity) in node_counts:
                    node_counts[id(w.target_entity)] += 1

            for w in idle_workers:
                nearest = min(resources, key=lambda r: w.distance_to(r) + node_counts[id(r)] * 90)
                node_counts[id(nearest)] += 1
                w.harvest_node(nearest, game_state)

        # 3. Drone Production
        max_workers = self.config.get("max_workers", 8)
        if len(ai_workers) < max_workers and bases:
            for base in bases:
                if base.is_constructed and len(base.production_queue) < 2:
                    cost_dict = UNIT_TYPES.get("Drone", {}).get("cost", {"biomass": 50})
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        base.queue_unit("Drone")

        # 4. Spawning Pool Facilities
        production_blds = [b for b in ai_buildings if b.building_type == "SpawningPool"]
        target_prod_blds = 3 if self.difficulty >= 4 else (2 if self.difficulty >= 2 else 1)

        if len(production_blds) < target_prod_blds and self.spawn_point:
            cost_dict = BUILDING_TYPES.get("SpawningPool", {}).get("cost", {"biomass": 150})
            pos = self._find_valid_building_position(game_state, "SpawningPool", self.spawn_point[0], self.spawn_point[1], min_building_gap=55, min_resource_gap=80)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "SpawningPool", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_builder_to_building(nb, ai_units, game_state)

        # 5. Spine Crawlers
        if self.difficulty >= 4 and self.config.get("can_build_defenses", True):
            defenses = [b for b in ai_buildings if b.building_type == "SpineCrawler"]
            target_def = 3 if self.difficulty >= 6 else 2

            if len(defenses) < target_def and self.spawn_point:
                cost_dict = BUILDING_TYPES.get("SpineCrawler", {}).get("cost", {"biomass": 100})
                pos = self._find_valid_building_position(game_state, "SpineCrawler", self.spawn_point[0], self.spawn_point[1], min_building_gap=45, min_resource_gap=75)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, "SpineCrawler", pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_builder_to_building(nb, ai_units, game_state)

        # Biomass Generators
        bio_gens = [b for b in ai_buildings if b.building_type == "BiomassGenerator"]
        if self.config.get("can_build_biomass_gen") and self.spawn_point:
            if len(bio_gens) < 3:
                cost_dict = BUILDING_TYPES.get("BiomassGenerator", {}).get("cost", {"biomass": 300})
                pos = self._find_valid_building_position(game_state, "BiomassGenerator", self.spawn_point[0], self.spawn_point[1], min_building_gap=50, min_resource_gap=75)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, "BiomassGenerator", pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_builder_to_building(nb, ai_units, game_state)

        # Evolution Chamber
        evo_chambers = [b for b in ai_buildings if b.building_type == "EvolutionChamber"]
        if self.config.get("can_build_evolution_chamber") and self.spawn_point and len(evo_chambers) < 1:
            cost_dict = BUILDING_TYPES.get("EvolutionChamber", {}).get("cost", {"biomass": 200})
            pos = self._find_valid_building_position(game_state, "EvolutionChamber", self.spawn_point[0], self.spawn_point[1], min_building_gap=50, min_resource_gap=75)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "EvolutionChamber", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_builder_to_building(nb, ai_units, game_state)

        active_evos = [b for b in evo_chambers if b.is_constructed]
        if active_evos:
            if self.evo_upgrades["troop_hp"] == 0:
                if game_state.deduct_resources(self.owner_id, "biomass", 150):
                    self.evo_upgrades["troop_hp"] = 1
                    for u in ai_units:
                        u.max_hp = int(u.max_hp * 1.10)
                        u.hp = int(u.hp * 1.10)
            elif self.evo_upgrades["swarmer_discount"] == 0:
                if game_state.deduct_resources(self.owner_id, "biomass", 150):
                    self.evo_upgrades["swarmer_discount"] = 1
            elif self.evo_upgrades["bio_gen_boost"] == 0:
                if game_state.deduct_resources(self.owner_id, "biomass", 150):
                    self.evo_upgrades["bio_gen_boost"] = 1

        # Biomass Stockpile
        stockpiles = [b for b in ai_buildings if b.building_type == "BiomassStockpile"]
        if self.config.get("can_build_biomass_stockpile") and resources and len(stockpiles) < 3:
            distant_res = [r for r in resources if min([math.hypot(r.x - b.x, r.y - b.y) for b in bases + stockpiles] or [9999]) > 400]
            if distant_res:
                target_r = distant_res[0]
                cost_dict = BUILDING_TYPES.get("BiomassStockpile", {}).get("cost", {"biomass": 80})
                pos = self._find_valid_building_position(game_state, "BiomassStockpile", target_r.x, target_r.y, min_building_gap=45, min_resource_gap=70, search_radius=180)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, "BiomassStockpile", pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_builder_to_building(nb, ai_units, game_state)

        # Second Hive Expansion
        if self.config.get("can_build_second_hive") and len(bases) < 2 and resources:
            far_res = [r for r in resources if min([math.hypot(r.x - b.x, r.y - b.y) for b in bases] or [0]) > 600]
            if far_res:
                target_r = far_res[0]
                cost_dict = BUILDING_TYPES.get("Hive", {}).get("cost", {"biomass": 400})
                pos = self._find_valid_building_position(game_state, "Hive", target_r.x, target_r.y, min_building_gap=60, min_resource_gap=80, search_radius=220)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, "Hive", pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_builder_to_building(nb, ai_units, game_state)

        # Ensure all unconstructed Alien buildings have an assigned Alien Drone builder
        unconstructed_ai_blds = [b for b in ai_buildings if not b.is_constructed and not getattr(b, 'is_being_built', False)]
        for ub in unconstructed_ai_blds:
            if not any(u.alive and u.target_entity == ub for u in ai_units):
                self._assign_builder_to_building(ub, ai_units, game_state)

        # Stat Bonuses & Creep
        hp_mult = self.config.get("unit_hp_bonus", 0.0)
        atk_mult = self.config.get("unit_atk_bonus", 0.0)
        speed_frenzy = 25 if self.config.get("swarm_frenzy") else 0

        for u in ai_units:
            if not getattr(u, '_ai_buffed', False):
                u.base_speed = u.speed
                u.base_attack = u.attack_power
                u.max_hp = int(u.max_hp * (1.0 + hp_mult))
                u.hp = min(u.hp, u.max_hp)
                u.attack_power = int(u.attack_power * (1.0 + atk_mult))
                u.speed += speed_frenzy
                u._ai_buffed = True

            if self.config.get("creep_spread") and bases:
                near_base = any(math.hypot(u.x - b.x, u.y - b.y) <= 300 for b in bases)
                if near_base and not getattr(u, '_on_creep', False):
                    u.speed = int(u.speed * 1.25)
                    u.attack_power = int(u.attack_power * 1.25)
                    u._on_creep = True
                elif not near_base and getattr(u, '_on_creep', False):
                    u.speed = int(u.speed / 1.25)
                    u.attack_power = int(u.attack_power / 1.25)
                    u._on_creep = False

        # Army Queueing
        for prod in production_blds:
            if prod.is_constructed and len(prod.production_queue) < 4:
                available_troops = ["Swarmer"]
                if self.difficulty >= 6 and self.config.get("can_tech_ranged", True):
                    available_troops.append("Spitter")
                if self.config.get("can_train_queen"):
                    available_troops.append("Queen")

                chosen_unit = random.choice(available_troops)
                cost_dict = dict(UNIT_TYPES.get(chosen_unit, {}).get("cost", {"biomass": 60}))
                if chosen_unit == "Swarmer" and self.evo_upgrades["swarmer_discount"] > 0:
                    cost_dict["biomass"] = int(cost_dict["biomass"] * 0.90)

                if game_state.deduct_resources(self.owner_id, cost_dict):
                    prod.queue_unit(chosen_unit)

        self._handle_common_combat_tactics(dt, game_state, ai_units)


class MedievalAIController(BaseAIController):
    def __init__(self, owner_id, difficulty=1):
        super().__init__(owner_id, faction=config.FACTION_HUMAN, difficulty=difficulty)

    def _assign_worker_to_building(self, nb, ai_units, game_state):
        if not nb or getattr(nb, 'is_constructed', True):
            return
        idle_workers = [u for u in ai_units if u.alive and u.is_worker and u.state == "idle"]
        if idle_workers:
            worker = min(idle_workers, key=lambda u: u.distance_to(nb))
            worker.construct_building(nb, game_state)
        elif len([u for u in ai_units if u.alive and u.is_worker]) > 1:
            active_workers = [u for u in ai_units if u.alive and u.is_worker and u.state in ["harvest", "return_resource"]]
            if active_workers:
                worker = min(active_workers, key=lambda u: u.distance_to(nb))
                worker.construct_building(nb, game_state)

    def update(self, dt, game_state):
        self.timer_wave += dt
        self.timer_macro += dt
        self.reflection_timer += dt

        # Scaling passive resource influx for Medieval AI
        income_mult = self.config.get("resource_multiplier", 1.0)
        gold_boost = 10 * income_mult * dt
        wood_boost = 10 * income_mult * dt
        food_boost = 8 * income_mult * dt

        if hasattr(game_state, 'add_resources'):
            game_state.add_resources(self.owner_id, "gold", gold_boost)
            game_state.add_resources(self.owner_id, "wood", wood_boost)
            game_state.add_resources(self.owner_id, "food", food_boost)

        ai_buildings = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id]
        active_banks = [b for b in ai_buildings if b.building_type == "Bank" and b.is_constructed]
        if active_banks and hasattr(game_state, 'add_resources'):
            game_state.add_resources(self.owner_id, "gold", 8 * len(active_banks) * dt)

        ai_units = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id]
        sanctuaries = [b for b in ai_buildings if b.building_type == "Sanctuary" and b.is_constructed]
        for sanc in sanctuaries:
            for u in ai_units:
                if u.hp < u.max_hp and math.hypot(u.x - sanc.x, u.y - sanc.y) <= 220:
                    u.hp = min(u.max_hp, u.hp + 8 * dt)

        if self.reflection_timer < self.reflection_interval:
            return
        self.reflection_timer = 0.0

        # Apply Medieval AI Difficulty Skill Tree Perks & Stat Buffs
        hp_mult = 0.05 * self.difficulty
        atk_mult = 0.05 * self.difficulty
        for u in ai_units:
            if not getattr(u, '_medieval_buffed', False):
                u.max_hp = int(u.max_hp * (1.0 + hp_mult))
                u.hp = min(u.hp, u.max_hp)
                u.attack_power = int(u.attack_power * (1.0 + atk_mult))
                u._medieval_buffed = True

        bases = [b for b in ai_buildings if b.building_type == "TownHall"]
        if bases:
            self.spawn_point = (bases[0].x, bases[0].y)

            # Forum Ballista attack & range upgrades at difficulty 8+
            if self.difficulty >= 8:
                for b in bases:
                    if b.attack_range == 0:
                        b.attack_range = 240
                        b.attack_power = 20

        # 1. Base Reconstruction if main TownHall destroyed
        if not bases and self.spawn_point:
            cost_dict = {"gold": 300, "wood": 300}
            pos = self._find_valid_building_position(game_state, "TownHall", self.spawn_point[0], self.spawn_point[1], min_building_gap=60, min_resource_gap=80)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "TownHall", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_worker_to_building(nb, ai_units, game_state)

        # 2. Worker Management & Resource Harvesting (with node load balancing)
        ai_workers = [u for u in ai_units if u.is_worker]
        idle_workers = [w for w in ai_workers if w.state == "idle"]
        resources = [r for r in game_state.resources if r.alive and r.resource_type in ["gold", "wood", "food"]]

        if idle_workers and resources:
            node_counts = {id(r): 0 for r in resources}
            for w in ai_workers:
                if w.target_entity and id(w.target_entity) in node_counts:
                    node_counts[id(w.target_entity)] += 1

            for w in idle_workers:
                nearest = min(resources, key=lambda r: w.distance_to(r) + node_counts[id(r)] * 90)
                node_counts[id(nearest)] += 1
                w.harvest_node(nearest, game_state)

        # 3. Peasant Worker Production
        max_workers = self.config.get("max_workers", 8)
        if len(ai_workers) < max_workers and bases:
            for base in bases:
                if base.is_constructed and len(base.production_queue) < 2:
                    cost_dict = {"food": 50}
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        base.queue_unit("Worker")

        # 4. Houses & Population Cap Management (Difficulty 3+)
        if self.difficulty >= 3 and self.spawn_point:
            pop_curr = game_state.get_unit_count(self.owner_id)
            pop_max = game_state.get_pop_max(self.owner_id)
            houses = [b for b in ai_buildings if b.building_type == "House"]

            if pop_curr >= pop_max - 2 and len(houses) < 6:
                cost_dict = {"wood": 60}
                pos = self._find_valid_building_position(game_state, "House", self.spawn_point[0], self.spawn_point[1], min_building_gap=45, min_resource_gap=75)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, "House", pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_worker_to_building(nb, ai_units, game_state)

        # 5. Barracks Production Facilities
        barracks = [b for b in ai_buildings if b.building_type == "Barracks"]
        target_barracks = 3 if self.difficulty >= 6 else (2 if self.difficulty >= 3 else 1)

        if len(barracks) < target_barracks and self.spawn_point:
            cost_dict = {"wood": 150, "gold": 100}
            pos = self._find_valid_building_position(game_state, "Barracks", self.spawn_point[0], self.spawn_point[1], min_building_gap=55, min_resource_gap=80)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "Barracks", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_worker_to_building(nb, ai_units, game_state)

        # 6. Farms & Grain Fields (Difficulty 3+)
        farms = [b for b in ai_buildings if b.building_type == "Farm"]
        if self.difficulty >= 3 and self.spawn_point and len(farms) < 3:
            cost_dict = {"wood": 80}
            pos = self._find_valid_building_position(game_state, "Farm", self.spawn_point[0], self.spawn_point[1], min_building_gap=50, min_resource_gap=75)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "Farm", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_worker_to_building(nb, ai_units, game_state)

        # 7. Defensive Arrow Towers & Wooden Walls (Difficulty 4+)
        if self.difficulty >= 4 and self.spawn_point:
            towers = [b for b in ai_buildings if b.building_type in ["WatchTower", "ArrowTower", "Tower"]]
            target_towers = 3 if self.difficulty >= 8 else 2

            if len(towers) < target_towers:
                t_type = "ArrowTower" if self.difficulty >= 8 else "WatchTower"
                cost_dict = {"wood": 120, "gold": 50}
                pos = self._find_valid_building_position(game_state, t_type, self.spawn_point[0], self.spawn_point[1], min_building_gap=45, min_resource_gap=75)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, t_type, pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_worker_to_building(nb, ai_units, game_state)

        # 8. Royal Bank (Difficulty 10+)
        banks = [b for b in ai_buildings if b.building_type == "Bank"]
        if self.difficulty >= 10 and self.spawn_point and len(banks) < 2:
            cost_dict = {"wood": 200, "gold": 250}
            pos = self._find_valid_building_position(game_state, "Bank", self.spawn_point[0], self.spawn_point[1], min_building_gap=50, min_resource_gap=75)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "Bank", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_worker_to_building(nb, ai_units, game_state)

        # 9. Healing Sanctuary (Difficulty 10+)
        sanctuaries = [b for b in ai_buildings if b.building_type == "Sanctuary"]
        if self.difficulty >= 10 and self.spawn_point and len(sanctuaries) < 1:
            cost_dict = {"wood": 180, "gold": 150}
            pos = self._find_valid_building_position(game_state, "Sanctuary", self.spawn_point[0], self.spawn_point[1], min_building_gap=50, min_resource_gap=75)
            if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                nb = Building(self.owner_id, self.faction, "Sanctuary", pos[0], pos[1], is_constructed=False)
                game_state.buildings.append(nb)
                self._assign_worker_to_building(nb, ai_units, game_state)

        # 10. Secondary TownHall Keep Expansion (Difficulty 15+)
        if self.difficulty >= 15 and len(bases) < 2 and resources:
            far_res = [r for r in resources if min([math.hypot(r.x - b.x, r.y - b.y) for b in bases] or [0]) > 600]
            if far_res:
                target_r = far_res[0]
                cost_dict = {"wood": 400, "gold": 400}
                pos = self._find_valid_building_position(game_state, "TownHall", target_r.x, target_r.y, min_building_gap=60, min_resource_gap=80, search_radius=220)
                if pos and game_state.deduct_resources(self.owner_id, cost_dict):
                    nb = Building(self.owner_id, self.faction, "TownHall", pos[0], pos[1], is_constructed=False)
                    game_state.buildings.append(nb)
                    self._assign_worker_to_building(nb, ai_units, game_state)

        # Ensure all unconstructed Medieval buildings have an assigned Medieval worker
        unconstructed_blds = [b for b in ai_buildings if not b.is_constructed]
        for ub in unconstructed_blds:
            if not any(u.alive and u.target_entity == ub for u in ai_units):
                self._assign_worker_to_building(ub, ai_units, game_state)

        # 11. Hero Knight Spawn (Difficulty 12+)
        heroes = [u for u in ai_units if u.is_hero]
        if self.difficulty >= 12 and not heroes and bases:
            hero_u = Unit(self.owner_id, self.faction, "Hero", bases[0].x + 30, bases[0].y + 30)
            if self.difficulty >= 14:
                hero_u.is_hero_archer = True
                hero_u.attack_range = 220
            game_state.units.append(hero_u)

        # 12. Military Unit Queueing in Barracks
        for bkr in barracks:
            if bkr.is_constructed and len(bkr.production_queue) < 4:
                available_troops = ["Infantry"]
                if self.difficulty >= 6:
                    available_troops.append("Archer")
                if self.difficulty >= 6:
                    available_troops.append("Scout")

                chosen_unit = random.choice(available_troops)
                cost_dict = UNIT_TYPES.get(chosen_unit, {}).get("cost", {"food": 60, "gold": 40})
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    bkr.queue_unit(chosen_unit)

        self._handle_common_combat_tactics(dt, game_state, ai_units)


def AIController(owner_id, faction=config.FACTION_ALIEN, difficulty=1):
    """Factory function instantiating the specialized AI Controller according to Faction."""
    if faction == config.FACTION_HUMAN:
        return MedievalAIController(owner_id=owner_id, difficulty=difficulty)
    else:
        return AlienAIController(owner_id=owner_id, difficulty=difficulty)
