import math
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
        extra_res_bonus = 100 if upgrades.get("starting_res_1") else 0
        self.resources_player[0] = {
            "gold": 200 + extra_res_bonus,
            "wood": 200 + extra_res_bonus,
            "food": 150 + extra_res_bonus,
            "biomass": 0
        }
        for ai_id in range(1, self.num_ais + 1):
            self.resources_player[ai_id] = {
                "gold": 0,
                "wood": 0,
                "food": 0,
                "biomass": 300
            }

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
            if res_type not in self.resources_player[owner_id]:
                self.resources_player[owner_id][res_type] = 0
            self.resources_player[owner_id][res_type] += amount

    def deduct_resources(self, owner_id, res_type, amount=None):
        if owner_id not in self.resources_player:
            return False
        if isinstance(res_type, dict):
            for r_name, r_cost in res_type.items():
                if self.resources_player[owner_id].get(r_name, 0) < r_cost:
                    return False
            for r_name, r_cost in res_type.items():
                self.resources_player[owner_id][r_name] -= r_cost
            return True
        else:
            if self.resources_player[owner_id].get(res_type, 0) >= amount:
                self.resources_player[owner_id][res_type] -= amount
                return True
            return False

    def get_unit_count(self, owner_id):
        return len([u for u in self.units if u.alive and u.owner_id == owner_id])

    def can_place_building(self, building_type, x, y, owner_id=None):
        from src.entities.building import BUILDING_TYPES
        radius = BUILDING_TYPES.get(building_type, {}).get("radius", 35)

        # Vérifier hors limites carte
        if x - radius < 0 or x + radius > config.MAP_WIDTH or y - radius < 0 or y + radius > config.MAP_HEIGHT:
            return False

        # Collision avec d'autres bâtiments
        for b in self.buildings:
            if b.alive:
                dist = math.hypot(b.x - x, b.y - y)
                if dist < b.radius + radius + 10:
                    return False

        # Collision avec ressources
        for r in self.resources:
            if r.alive:
                dist = math.hypot(r.x - x, r.y - y)
                if dist < r.radius + radius + 10:
                    return False

        return True

    def resolve_unit_collisions(self):
        units_list = [u for u in self.units if u.alive]
        num_units = len(units_list)
        for i in range(num_units):
            u1 = units_list[i]
            for j in range(i + 1, num_units):
                u2 = units_list[j]
                dx = u2.x - u1.x
                dy = u2.y - u1.y
                dist = math.hypot(dx, dy)
                min_dist = u1.radius + u2.radius

                if dist < min_dist:
                    overlap = min_dist - dist
                    if dist == 0:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    nx = dx / dist
                    ny = dy / dist

                    # Repousser les deux unités à parts égales
                    push_x = nx * (overlap / 2.0)
                    push_y = ny * (overlap / 2.0)

                    u1.x -= push_x
                    u1.y -= push_y
                    u2.x += push_x
                    u2.y += push_y

        # Résoudre également la collision unités / bâtiments
        for u in units_list:
            for b in self.buildings:
                if b.alive:
                    dx = u.x - b.x
                    dy = u.y - b.y
                    dist = math.hypot(dx, dy)
                    min_dist = u.radius + b.radius
                    if dist < min_dist:
                        overlap = min_dist - dist
                        if dist == 0:
                            dx, dy, dist = 1.0, 0.0, 1.0
                        nx = dx / dist
                        ny = dy / dist
                        u.x += nx * overlap
                        u.y += ny * overlap

    def update(self, dt):
        if self.state != "PLAYING":
            return

        # Résolution des collisions d'unités (Empêcher l'overlap)
        self.resolve_unit_collisions()

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
            self.save_manager.add_points(
                landshard=rewards[config.POINT_TYPE_COMMAND],
                swarmerblood=rewards[config.POINT_TYPE_FORGE],
                pykrite=rewards[config.POINT_TYPE_ARCHITECTURE]
            )

        elif not ai_buildings and not ai_units:
            self.state = "VICTORY"
            rewards = Rewards.calculate_rewards(True, self.num_ais, self.ai_difficulty)
            self.save_manager.add_points(
                landshard=rewards[config.POINT_TYPE_COMMAND],
                swarmerblood=rewards[config.POINT_TYPE_FORGE],
                pykrite=rewards[config.POINT_TYPE_ARCHITECTURE]
            )
