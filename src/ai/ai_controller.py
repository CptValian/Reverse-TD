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

        # 2. Gestion des Bâtiments et Production
        ai_buildings = [b for b in game_state.buildings if b.alive and b.owner_id == self.owner_id]
        res = game_state.resources_player.get(self.owner_id, {"gold": 0, "biomass": 0})
        res_type = "biomass" if self.faction == config.FACTION_ALIEN else "gold"

        # Entraînement d'ouvriers
        bases = [b for b in ai_buildings if b.building_type in ["Hive", "TownHall"]]
        if len(ai_workers) < 6 and bases:
            for base in bases:
                if len(base.production_queue) == 0 and res[res_type] >= 50:
                    unit_to_train = "Drone" if self.faction == config.FACTION_ALIEN else "Worker"
                    base.queue_unit(unit_to_train, train_time=5)
                    game_state.deduct_resources(self.owner_id, res_type, 50)

        # Construction d'un bâtiment de recrutement (SpawningPool / Barracks) s'il n'y en a pas
        barracks = [b for b in ai_buildings if b.building_type in ["SpawningPool", "Barracks"]]
        if not barracks and res[res_type] >= 150 and ai_workers:
            worker = ai_workers[0]
            b_type = "SpawningPool" if self.faction == config.FACTION_ALIEN else "Barracks"
            game_state.deduct_resources(self.owner_id, res_type, 150)
            new_building = Building(self.owner_id, self.faction, b_type, worker.x + 50, worker.y + 50)
            game_state.buildings.append(new_building)

        # Entraînement d'unités militaires
        army_units = [u for u in ai_units if not u.is_worker]
        if len(army_units) < self.config["max_army_size"]:
            for b in barracks:
                if len(b.production_queue) == 0 and res[res_type] >= 80:
                    unit_to_train = "Swarmer" if self.faction == config.FACTION_ALIEN else "Infantry"
                    b.queue_unit(unit_to_train, train_time=6)
                    game_state.deduct_resources(self.owner_id, res_type, 80)

        # 3. Lancement d'une Vague d'Attaque
        if self.timer_wave >= self.config["attack_wave_interval"]:
            self.timer_wave = 0.0
            if army_units:
                # Cible: la base ennemie principale (owner_id 0)
                player_bases = [b for b in game_state.buildings if b.alive and b.owner_id != self.owner_id]
                player_units = [u for u in game_state.units if u.alive and u.owner_id != self.owner_id]
                target = None
                if player_bases:
                    target = player_bases[0]
                elif player_units:
                    target = player_units[0]

                if target:
                    for u in army_units:
                        u.attack_target(target)
