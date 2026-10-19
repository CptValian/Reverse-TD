import config
from src.engine.camera import Camera
from src.engine.map_generator import MapGenerator
from src.entities.unit import Unit
from src.entities.building import Building
from src.entities.resource_node import ResourceNode
from src.ai.ai_controller import AIController
from src.progression.save_manager import SaveManager
from src.progression.rewards import Rewards

class GameState:
    def __init__(self, save_manager, num_ais=1, ai_difficulty="Très Facile"):
        self.save_manager = save_manager
        self.num_ais = num_ais
        self.ai_difficulty = ai_difficulty

        self.state = "MENU"  # "MENU", "SKILL_TREE", "PLAYING", "VICTORY", "DEFEAT"

        self.units = []
        self.buildings = []
        self.resources = []
        self.ai_controllers = []

        # Statistiques des joueurs (owner_id 0 = Humain, owner_id 1..N = IA)
        self.resources_player = {}

        self.selection_box = None  # Tuple (start_x, start_y, current_x, current_y)

    def start_new_game(self):
        self.units.clear()
        self.buildings.clear()
        self.resources.clear()
        self.ai_controllers.clear()
        self.resources_player.clear()

        # Application des améliorations de méta-progression
        upgrades = self.save_manager.data.get("upgrades", {})
        extra_res = upgrades.get("starting_resources_lvl", 0) * 100
        hp_bonus_units = upgrades.get("unit_hp_lvl", 0) * 0.10
        atk_bonus_units = upgrades.get("unit_attack_lvl", 0) * 0.10
        hp_bonus_bld = upgrades.get("building_hp_lvl", 0) * 0.15
        armor_bonus_bld = upgrades.get("building_armor_lvl", 0) * 1.0

        # Initialisation des ressources des joueurs
        self.resources_player[0] = {"gold": 300 + extra_res, "biomass": 0}
        for ai_id in range(1, self.num_ais + 1):
            self.resources_player[ai_id] = {"gold": 0, "biomass": 300}

        # Génération de la carte
        map_gen = MapGenerator(config.MAP_WIDTH, config.MAP_HEIGHT)
        map_data = map_gen.generate_map(num_players=self.num_ais + 1)

        # Création des ressources sur la carte
        for res_data in map_data["resources"]:
            self.resources.append(ResourceNode(res_data.type, res_data.x, res_data.y, res_data.amount))

        # Spawns des joueurs
        for spawn in map_data["spawns"]:
            owner_id = spawn["id"]
            faction = spawn["faction"]
            sx, sy = spawn["x"], spawn["y"]

            if faction == config.FACTION_HUMAN:
                # Base humaine
                base = Building(owner_id, faction, "TownHall", sx, sy,
                                hp_bonus=int(1000 * hp_bonus_bld), armor_bonus=armor_bonus_bld)
                self.buildings.append(base)

                # 3 ouvriers de départ
                for offset in [(-30, 40), (0, 50), (30, 40)]:
                    u = Unit(owner_id, faction, "Worker", sx + offset[0], sy + offset[1],
                             hp_bonus=int(60 * hp_bonus_units), attack_bonus=int(5 * atk_bonus_units))
                    self.units.append(u)
            else:
                # Base Alien IA
                base = Building(owner_id, faction, "Hive", sx, sy)
                self.buildings.append(base)

                # 3 Drones de départ
                for offset in [(-30, 40), (0, 50), (30, 40)]:
                    u = Unit(owner_id, faction, "Drone", sx + offset[0], sy + offset[1])
                    self.units.append(u)

                # Contrôleur d'IA
                ai_ctrl = AIController(owner_id=owner_id, faction=faction, difficulty=self.ai_difficulty)
                self.ai_controllers.append(ai_ctrl)

        self.state = "PLAYING"

    def add_resources(self, owner_id, res_type, amount):
        if owner_id in self.resources_player:
            self.resources_player[owner_id][res_type] += amount

    def deduct_resources(self, owner_id, res_type, amount):
        if owner_id in self.resources_player and self.resources_player[owner_id].get(res_type, 0) >= amount:
            self.resources_player[owner_id][res_type] -= amount
            return True
        return False

    def get_unit_count(self, owner_id):
        return len([u for u in self.units if u.alive and u.owner_id == owner_id])

    def update(self, dt):
        if self.state != "PLAYING":
            return

        # Mise à jour des unités
        for unit in list(self.units):
            if unit.alive:
                unit.update(dt, self)
            else:
                self.units.remove(unit)

        # Mise à jour des bâtiments et production
        for building in list(self.buildings):
            if building.alive:
                produced_unit = building.update(dt, self)
                if produced_unit:
                    # Spawner l'unité produite au pied du bâtiment
                    new_u = Unit(building.owner_id, building.faction, produced_unit, building.x, building.y + building.radius + 15)
                    self.units.append(new_u)
            else:
                self.buildings.remove(building)

        # Nettoyage des gisements épuisés
        self.resources = [r for r in self.resources if r.alive]

        # Mise à jour des IA
        for ai in self.ai_controllers:
            ai.update(dt, self)

        # Vérification des conditions de victoire/défaite (destruction totale)
        player_buildings = [b for b in self.buildings if b.owner_id == 0]
        player_units = [u for u in self.units if u.owner_id == 0]

        ai_buildings = [b for b in self.buildings if b.owner_id != 0]
        ai_units = [u for u in self.units if u.owner_id != 0]

        if not player_buildings and not player_units:
            self.state = "DEFEAT"
            rewards = Rewards.calculate_rewards(False, self.num_ais, self.ai_difficulty)
            self.save_manager.add_points(**{
                "command": rewards[config.POINT_TYPE_COMMAND],
                "forge": rewards[config.POINT_TYPE_FORGE],
                "architecture": rewards[config.POINT_TYPE_ARCHITECTURE]
            })

        elif not ai_buildings and not ai_units:
            self.state = "VICTORY"
            rewards = Rewards.calculate_rewards(True, self.num_ais, self.ai_difficulty)
            self.save_manager.add_points(**{
                "command": rewards[config.POINT_TYPE_COMMAND],
                "forge": rewards[config.POINT_TYPE_FORGE],
                "architecture": rewards[config.POINT_TYPE_ARCHITECTURE]
            })
