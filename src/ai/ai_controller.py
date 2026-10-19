from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
from src.entities.unit import Unit
from src.entities.building import Building
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

    def update(self, dt, game_state):
        self.timer_wave += dt

        # Apply resource multiplier trick over time
        if self.config.get("resource_multiplier", 1.0) > 1.0:
            res_boost = 10 * (self.config["resource_multiplier"] - 1.0) * dt
            game_state.add_resources(self.owner_id, "biomass" if self.faction == config.FACTION_ALIEN else "gold", res_boost)

        # 1. Worker Management (Harvesting)
        ai_units = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id]
        ai_workers = [u for u in ai_units if u.is_worker]
        idle_workers = [w for w in ai_workers if w.state == "idle"]

        if idle_workers:
            resources = [r for r in game_state.resources if r.alive]
            if resources:
                for w in idle_workers:
                    nearest = min(resources, key=lambda r: w.distance_to(r))
                    w.harvest_node(nearest)

        # 2. Economy & Building Production
        ai_buildings = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id]
        res_type = "biomass" if self.faction == config.FACTION_ALIEN else "gold"

        # Worker Training Limit based on difficulty
        max_workers = self.config.get("max_workers", 6)
        bases = [b for b in ai_buildings if b.building_type in ["Hive", "TownHall"] and b.is_constructed]
        if len(ai_workers) < max_workers and bases:
            for base in bases:
                unit_to_train = "Drone" if self.faction == config.FACTION_ALIEN else "Worker"
                from src.entities.unit import UNIT_TYPES
                cost_dict = UNIT_TYPES.get(unit_to_train, {}).get("cost", {res_type: 50})
                if len(base.production_queue) < 2:
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        base.queue_unit(unit_to_train)

        # Spawning Pool / Barracks Production
        spawning_pools = [b for b in ai_buildings if b.building_type in ["SpawningPool", "Barracks"]]
        target_pools = 2 if self.difficulty >= 5 else 1

        if len(spawning_pools) < target_pools and ai_workers:
            worker = ai_workers[0]
            b_type = "SpawningPool" if self.faction == config.FACTION_ALIEN else "Barracks"
            from src.entities.building import BUILDING_TYPES
            cost_dict = BUILDING_TYPES.get(b_type, {}).get("cost", {res_type: 150})

            bx = worker.x + 60 * len(spawning_pools) + 40
            by = worker.y + 40
            if game_state.can_place_building(b_type, bx, by):
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    new_b = Building(self.owner_id, self.faction, b_type, bx, by, is_constructed=False)
                    game_state.buildings.append(new_b)

        # Defense building (SpineCrawler) for higher difficulties
        if self.config.get("can_build_defenses", False):
            defenses = [b for b in ai_buildings if b.building_type in ["SpineCrawler", "Tower"]]
            if len(defenses) < 2 and ai_workers:
                worker = ai_workers[-1]
                def_type = "SpineCrawler" if self.faction == config.FACTION_ALIEN else "Tower"
                from src.entities.building import BUILDING_TYPES
                cost_dict = BUILDING_TYPES.get(def_type, {}).get("cost", {res_type: 100})
                bx = worker.x - 50 * (len(defenses) + 1)
                by = worker.y - 50
                if game_state.can_place_building(def_type, bx, by):
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        new_def = Building(self.owner_id, self.faction, def_type, bx, by, is_constructed=False)
                        game_state.buildings.append(new_def)

        # Army Production (Swarmers & Ranged Spitters if unlocked)
        army_units = [u for u in ai_units if not u.is_worker]
        for sp in spawning_pools:
            if sp.is_constructed and len(sp.production_queue) < 3:
                available_troops = ["Swarmer"] if self.faction == config.FACTION_ALIEN else ["Infantry"]
                if self.config.get("can_tech_ranged", False) and "Spitter" in self.config.get("unlocked_techs", []):
                    if self.faction == config.FACTION_ALIEN:
                        available_troops.append("Spitter")
                    else:
                        available_troops.append("Archer")

                import random
                u_type = random.choice(available_troops)
                from src.entities.unit import UNIT_TYPES
                cost_dict = UNIT_TYPES.get(u_type, {}).get("cost", {res_type: 60})
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    sp.queue_unit(u_type)

        # 3. Attack Waves
        min_swarm_size = 2 if self.difficulty == 1 else (3 if self.difficulty == 2 else 5)
        if self.timer_wave >= self.config["attack_wave_interval"] or len(army_units) >= self.config["max_army_size"]:
            if len(army_units) >= min_swarm_size:
                self.timer_wave = 0.0
                player_targets = [e for e in game_state.buildings + game_state.units if e.alive and e.owner_id != self.owner_id]
                if player_targets:
                    target = min(player_targets, key=lambda e: e.hp)
                    for u in army_units:
                        u.attack_move_to(target.x, target.y)
