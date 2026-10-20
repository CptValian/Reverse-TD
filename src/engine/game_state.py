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
    def __init__(self, save_manager, num_ais=1, ai_difficulty=1, map_type=1):
        self.save_manager = save_manager
        self.num_ais = num_ais
        try:
            self.ai_difficulty = int(ai_difficulty)
        except (ValueError, TypeError):
            self.ai_difficulty = 1
        self.map_type = map_type  # 1: Standard, 2: Désavantageuse, 3: Très Désavantageuse

        self.state = "MENU"  # "MENU", "SKILL_TREE", "PLAYING", "VICTORY", "DEFEAT"

        self.units = []
        self.buildings = []
        self.resources = []
        self.ai_controllers = []

        # Statistiques des joueurs (owner_id 0 = Humain, owner_id 1..N = IA)
        self.resources_player = {}
        self.resources_gathered_player = {}

        self.selection_box = None  # Tuple (start_x, start_y, current_x, current_y)
        self.game_time = 0.0
        self.player_age = 1

    def is_fog_of_war_enabled(self):
        return self.ai_difficulty > 4

    def is_point_visible(self, x, y, owner_id=0):
        if not self.is_fog_of_war_enabled():
            return True

        # Player units vision
        for u in self.units:
            if u.alive and u.owner_id == owner_id:
                dist = math.hypot(u.x - x, u.y - y)
                if dist <= getattr(u, 'vision_radius', 220):
                    return True

        # Player buildings vision
        for b in self.buildings:
            if b.alive and b.owner_id == owner_id:
                dist = math.hypot(b.x - x, b.y - y)
                if dist <= getattr(b, 'vision_radius', 250):
                    return True

        return False

    def age_up(self, owner_id=0):
        if owner_id == 0:
            self.player_age += 1
            # Strengthen all buildings HP by * 1.2
            for b in self.buildings:
                if b.alive and b.owner_id == owner_id:
                    hp_ratio = b.hp / max(1.0, b.max_hp)
                    b.max_hp = int(b.max_hp * 1.2)
                    b.hp = int(b.max_hp * hp_ratio)

    def start_new_game(self):
        self.game_time = 0.0
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
        self.resources_gathered_player[0] = {
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
            self.resources_gathered_player[ai_id] = {
                "gold": 0,
                "wood": 0,
                "food": 0,
                "biomass": 300
            }

        # Génération de la carte selon map_type
        map_gen = MapGenerator(config.MAP_WIDTH, config.MAP_HEIGHT)
        map_data = map_gen.generate_map(num_players=self.num_ais + 1, map_type=self.map_type)

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
                range_bonus = 22 if upgrades.get("forum_atk_range") else 0
                base = Building(owner_id, faction, "TownHall", sx, sy,
                                hp_bonus=int(1000 * hp_bonus_bld), armor_bonus=armor_bonus_bld, range_bonus=range_bonus)
                self.buildings.append(base)

                # Doubler la capacité des gisements autour du forum de départ si l'amélioration est active
                if upgrades.get("double_base_res_cap"):
                    for r in self.resources:
                        if math.hypot(r.x - sx, r.y - sy) < 400:
                            r.amount *= 2
                            r.max_amount *= 2

                # Ouvriers de départ (3 de base + 1 si extra_worker_start)
                num_workers = 3 + (1 if upgrades.get("extra_worker_start") else 0)
                worker_offsets = [(-30, 40), (0, 50), (30, 40), (-45, 50), (45, 50)]
                for i in range(num_workers):
                    offset = worker_offsets[i % len(worker_offsets)]
                    u = Unit(owner_id, faction, "Worker", sx + offset[0], sy + offset[1],
                             hp_bonus=int(60 * hp_bonus_units), attack_bonus=int(5 * atk_bonus_units))
                    self.units.append(u)

                # Unité de mêlée de départ si extra_melee_start
                if upgrades.get("extra_melee_start"):
                    u_inf = Unit(owner_id, faction, "Infantry", sx, sy + 60,
                                 hp_bonus=int(150 * hp_bonus_units), attack_bonus=int(18 * atk_bonus_units))
                    self.units.append(u_inf)
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

    def get_map_resource_factor(self):
        if self.map_type == 2:
            return 0.75
        elif self.map_type == 3:
            return 0.50
        return 1.0

    def add_resources(self, owner_id, res_type, amount):
        if owner_id in self.resources_player:
            effective_amount = amount
            if owner_id == 0:
                effective_amount = amount * self.get_map_resource_factor()

            if res_type not in self.resources_player[owner_id]:
                self.resources_player[owner_id][res_type] = 0
            self.resources_player[owner_id][res_type] += effective_amount

            if owner_id not in self.resources_gathered_player:
                self.resources_gathered_player[owner_id] = {}
            if res_type not in self.resources_gathered_player[owner_id]:
                self.resources_gathered_player[owner_id][res_type] = 0
            self.resources_gathered_player[owner_id][res_type] += effective_amount

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

    def get_pop_max(self, owner_id):
        base_pop = 10
        bonus_pop = sum(b.pop_bonus for b in self.buildings if b.alive and b.owner_id == owner_id and getattr(b, 'is_constructed', True))
        return base_pop + bonus_pop

    def get_queued_and_current_pop(self, owner_id):
        curr_pop = self.get_unit_count(owner_id)
        queued_pop = 0
        for b in self.buildings:
            if b.alive and b.owner_id == owner_id:
                queued_pop += len(b.production_queue)
        return curr_pop + queued_pop

    def can_place_building(self, building_type, x, y, owner_id=None):
        from src.entities.building import BUILDING_TYPES
        radius = BUILDING_TYPES.get(building_type, {}).get("radius", 35)

        # Vérifier hors limites carte
        if x - radius < 0 or x + radius > config.MAP_WIDTH or y - radius < 0 or y + radius > config.MAP_HEIGHT:
            return False

        # Collision avec d'autres bâtiments
        for b in self.buildings:
            if b.alive:
                if building_type == "Wall" and b.building_type == "Wall":
                    continue  # Wall sections can connect seamlessly adjacent to each other
                min_req = b.radius + radius + 10
                if (b.x - x)**2 + (b.y - y)**2 < min_req * min_req:
                    return False

        # Collision avec ressources
        for r in self.resources:
            if r.alive:
                min_req = r.radius + radius + 10
                if (r.x - x)**2 + (r.y - y)**2 < min_req * min_req:
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
                dist_sq = dx * dx + dy * dy
                min_dist = u1.radius + u2.radius

                if dist_sq < min_dist * min_dist:
                    dist = math.sqrt(dist_sq)
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

        # Résoudre également la collision unités / bâtiments (AABB / OBB pour Murs, Cercles pour autres bâtiments)
        for u in units_list:
            for b in self.buildings:
                if not b.alive:
                    continue

                if b.building_type == "Wall":
                    # Exact Oriented Bounding Box (OBB) vs Unit Circle collision
                    w_len = getattr(b, 'wall_length', 40)
                    w_wid = getattr(b, 'wall_width', 18)
                    w_ang = getattr(b, 'wall_angle', 0.0)

                    hl = w_len / 2.0
                    hw = w_wid / 2.0

                    dx = u.x - b.x
                    dy = u.y - b.y

                    cos_a = math.cos(-w_ang)
                    sin_a = math.sin(-w_ang)

                    local_x = dx * cos_a - dy * sin_a
                    local_y = dx * sin_a + dy * cos_a

                    cx = max(-hl, min(hl, local_x))
                    cy = max(-hw, min(hw, local_y))

                    lx = local_x - cx
                    ly = local_y - cy
                    dist_sq = lx * lx + ly * ly

                    if dist_sq < u.radius * u.radius:
                        dist = math.sqrt(dist_sq)
                        if dist > 0.0001:
                            overlap = u.radius - dist
                            nx = lx / dist
                            ny = ly / dist
                        else:
                            # Center is inside rectangle - push along closest edge
                            d_pos_x = hl - local_x
                            d_neg_x = local_x + hl
                            d_pos_y = hw - local_y
                            d_neg_y = local_y + hw
                            min_d = min(d_pos_x, d_neg_x, d_pos_y, d_neg_y)
                            if min_d == d_pos_x:
                                nx, ny = 1.0, 0.0; overlap = d_pos_x + u.radius
                            elif min_d == d_neg_x:
                                nx, ny = -1.0, 0.0; overlap = d_neg_x + u.radius
                            elif min_d == d_pos_y:
                                nx, ny = 0.0, 1.0; overlap = d_pos_y + u.radius
                            else:
                                nx, ny = 0.0, -1.0; overlap = d_neg_y + u.radius

                        push_lx = nx * overlap
                        push_ly = ny * overlap

                        cos_back = math.cos(w_ang)
                        sin_back = math.sin(w_ang)

                        u.x += push_lx * cos_back - push_ly * sin_back
                        u.y += push_lx * sin_back + push_ly * cos_back
                else:
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

        self.game_time += dt

        # Résolution des collisions d'unités (Empêcher l'overlap)
        self.resolve_unit_collisions()

        # Mise à jour des unités
        upgrades = self.save_manager.data.get("upgrades", {})
        has_looting = upgrades.get("looting_unlocked", 0) >= 1

        for unit in list(self.units):
            if unit.alive:
                unit.update(dt, self)
            else:
                if has_looting and unit.owner_id != 0:
                    self.add_resources(0, "food", 5)

                # AI Level 12 Biomass Reward on enemy kill
                if unit.owner_id == 0:
                    for ai in self.ai_controllers:
                        if ai.config.get("biomass_on_kill"):
                            self.add_resources(ai.owner_id, "biomass", 15)

                self.units.remove(unit)

        # Mise à jour des bâtiments et production
        for building in list(self.buildings):
            if building.alive:
                produced_unit = building.update(dt, self)
                if produced_unit:
                    # Spawner l'unité produite au pied du bâtiment
                    new_u = Unit(building.owner_id, building.faction, produced_unit, building.x, building.y + building.radius + 15)

                    # Appliquer le point de ralliement (Rally Point) si défini
                    if building.rally_point:
                        rx, ry = building.rally_point
                        rt = building.rally_target
                        if new_u.is_worker and rt and getattr(rt, 'alive', True) and (hasattr(rt, 'harvest') or getattr(rt, 'building_type', None) == "Farm"):
                            new_u.harvest_node(rt)
                        elif rt and getattr(rt, 'alive', True) and rt.owner_id != building.owner_id:
                            new_u.attack_target(rt)
                        else:
                            new_u.move_to(rx, ry)

                    self.units.append(new_u)
            else:
                building.ungarrison_all(self)
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
            rewards = Rewards.calculate_rewards(False, self.num_ais, self.ai_difficulty, survival_time=self.game_time)
            self.last_match_rewards = rewards
            self.save_manager.add_points(
                landshard=rewards[config.POINT_TYPE_COMMAND],
                swarmerblood=rewards[config.POINT_TYPE_FORGE],
                pykrite=rewards[config.POINT_TYPE_ARCHITECTURE]
            )

        elif not ai_buildings and not ai_units:
            self.state = "VICTORY"
            rewards = Rewards.calculate_rewards(True, self.num_ais, self.ai_difficulty, survival_time=self.game_time)
            self.last_match_rewards = rewards
            self.save_manager.add_points(
                landshard=rewards[config.POINT_TYPE_COMMAND],
                swarmerblood=rewards[config.POINT_TYPE_FORGE],
                pykrite=rewards[config.POINT_TYPE_ARCHITECTURE]
            )
