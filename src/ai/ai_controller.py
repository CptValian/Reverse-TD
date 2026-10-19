from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
from src.entities.unit import Unit
from src.entities.building import Building
import config

class AIController:
    def __init__(self, owner_id, faction=config.FACTION_ALIEN, difficulty="Très Facile"):
        self.owner_id = owner_id
        self.faction = faction
        self.difficulty = difficulty
        self.config = AI_DIFFICULTY_LEVELS.get(difficulty, AI_DIFFICULTY_LEVELS["Très Facile"])
        self.timer_wave = 0.0

    def update(self, dt, game_state):
        self.timer_wave += dt

        # 1. Gestion des Ouvriers (Harvesting)
        ai_units = [u for u in game_state.units if u.alive and u.owner_id == self.owner_id]
        ai_workers = [u for u in ai_units if u.is_worker]
        idle_workers = [w for w in ai_workers if w.state == "idle"]

        if idle_workers:
            # Trouver un gisement de ressources disponible
            resources = [r for r in game_state.resources if r.alive]
            if resources:
                for w in idle_workers:
                    # Choisir le gisement le plus proche
                    nearest = min(resources, key=lambda r: w.distance_to(r))
                    w.harvest_node(nearest)

        # 2. Gestion Zerg (Aliens Insectes) : Production en masse, multiples bassins, essaim rapide
        ai_buildings = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id]
        res = game_state.resources_player.get(self.owner_id, {"gold": 0, "biomass": 0})
        res_type = "biomass" if self.faction == config.FACTION_ALIEN else "gold"

        # Production d'ouvriers/drones rapide (jusqu'à 8-10 drones)
        bases = [b for b in ai_buildings if b.building_type in ["Hive", "TownHall"] and b.is_constructed]
        if len(ai_workers) < 8 and bases:
            for base in bases:
                unit_to_train = "Drone" if self.faction == config.FACTION_ALIEN else "Worker"
                from src.entities.unit import UNIT_TYPES
                cost_dict = UNIT_TYPES.get(unit_to_train, {}).get("cost", {res_type: 50})
                if len(base.production_queue) < 2:
                    if game_state.deduct_resources(self.owner_id, cost_dict):
                        base.queue_unit(unit_to_train)

        # Construction de SpawningPools
        spawning_pools = [b for b in ai_buildings if b.building_type in ["SpawningPool", "Barracks"]]
        target_pools = 2 if self.faction == config.FACTION_ALIEN else 1

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

        # Entraînement en essaim
        army_units = [u for u in ai_units if not u.is_worker]
        for sp in spawning_pools:
            if sp.is_constructed and len(sp.production_queue) < 3:
                u_type = "Swarmer" if self.faction == config.FACTION_ALIEN else "Infantry"
                from src.entities.unit import UNIT_TYPES
                cost_dict = UNIT_TYPES.get(u_type, {}).get("cost", {res_type: 60})
                if game_state.deduct_resources(self.owner_id, cost_dict):
                    sp.queue_unit(u_type)

        # 3. Lancement d'une Vague d'Attaque massive en Essaim Zerg
        # L'IA Zerg attend d'avoir au moins un essaim minimal (ex: 6-8 Swarmers) pour tout déferler d'un coup
        min_swarm_size = 6 if self.faction == config.FACTION_ALIEN else 4
        if self.timer_wave >= self.config["attack_wave_interval"] or len(army_units) >= self.config["max_army_size"]:
            if len(army_units) >= min_swarm_size:
                self.timer_wave = 0.0
                player_targets = [e for e in game_state.buildings + game_state.units if e.alive and e.owner_id != self.owner_id]
                if player_targets:
                    # Choisir la cible ennemie la plus faible ou la base
                    target = min(player_targets, key=lambda e: e.hp)
                    for u in army_units:
                        # Attaque en vague groupée avec mode attack-move vers la cible
                        u.attack_move_to(target.x, target.y)
