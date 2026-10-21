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
        self.map_type = map_type  # 1: Standard, 2: Désavantage I, 3: Désavantage II, 4: Avantage I, 5: Avantage II

        self.state = "MENU"  # "MENU", "SKILL_TREE", "PLAYING", "VICTORY", "DEFEAT", "SPECTATOR_END", "IACIA_SETUP"
        self.is_spectator = False
        self.teams = {}  # {owner_id: team_id}
        self.winning_team = None

        self.units = []
        self.buildings = []
        self.resources = []
        self.projectiles = []
        self.ai_controllers = []

        # Statistiques des joueurs
        self.resources_player = {}
        self.resources_gathered_player = {}

        self.selection_box = None  # Tuple (start_x, start_y, current_x, current_y)
        self.game_time = 0.0
        self.player_age = 1

        # Configuration IAcIA par défaut
        self.iacia_config = {
            "preset_name": "3v5",
            "map_type": 1,
            "ai_players": [
                {"id": 1, "team": 1, "difficulty": 5, "faction": config.FACTION_HUMAN},
                {"id": 2, "team": 1, "difficulty": 5, "faction": config.FACTION_HUMAN},
                {"id": 3, "team": 1, "difficulty": 5, "faction": config.FACTION_HUMAN},
                {"id": 4, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
                {"id": 5, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
                {"id": 6, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
                {"id": 7, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
                {"id": 8, "team": 2, "difficulty": 5, "faction": config.FACTION_ALIEN},
            ]
        }

    def are_enemies(self, owner1, owner2):
        if owner1 == owner2:
            return False
        t1 = self.teams.get(owner1, owner1)
        t2 = self.teams.get(owner2, owner2)
        return t1 != t2

    def is_fog_of_war_enabled(self):
        if self.is_spectator:
            return False
        if hasattr(self, 'save_manager') and self.save_manager:
            if self.save_manager.get_setting("disable_fog_of_war", False):
                return False
        return self.ai_difficulty > 4

    def is_point_visible(self, x, y, owner_id=0):
        if not self.is_fog_of_war_enabled() or self.is_spectator:
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

    def start_new_game(self, is_iacia=False):
        self.game_time = 0.0
        self.units.clear()
        self.buildings.clear()
        self.resources.clear()
        self.projectiles.clear()
        self.ai_controllers.clear()
        self.resources_player.clear()
        self.resources_gathered_player.clear()
        self.teams.clear()
        self.is_spectator = is_iacia
        self.winning_team = None

        if is_iacia:
            self._start_iacia_game()
        else:
            self._start_standard_game()

        self.state = "PLAYING"

    def _start_standard_game(self):
        # Human player is owner_id 0 (Team 1)
        self.teams[0] = 1
        for ai_id in range(1, self.num_ais + 1):
            self.teams[ai_id] = 2  # Enemy team

        upgrades = self.save_manager.data.get("upgrades", {}) if hasattr(self, 'save_manager') and self.save_manager else {}
        hp_bonus_units = upgrades.get("unit_hp_lvl", 0) * 0.10
        atk_bonus_units = upgrades.get("unit_attack_lvl", 0) * 0.10
        hp_bonus_bld = upgrades.get("building_hp_lvl", 0) * 0.15
        armor_bonus_bld = upgrades.get("building_armor_lvl", 0) * 1.0

        extra_res_bonus = (100 if upgrades.get("starting_res_1") else 0) + (250 if upgrades.get("high_starting_res") else 0)
        self.resources_player[0] = {
            "gold": 200 + extra_res_bonus,
            "wood": 200 + extra_res_bonus,
            "food": 150 + extra_res_bonus,
            "biomass": 0
        }
        self.resources_gathered_player[0] = dict(self.resources_player[0])

        for ai_id in range(1, self.num_ais + 1):
            self.resources_player[ai_id] = {"gold": 0, "wood": 0, "food": 0, "biomass": 300}
            self.resources_gathered_player[ai_id] = dict(self.resources_player[ai_id])

        map_gen = MapGenerator(config.MAP_WIDTH, config.MAP_HEIGHT)
        map_data = map_gen.generate_map(num_players=self.num_ais + 1, map_type=self.map_type)

        from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
        ai_cfg = AI_DIFFICULTY_LEVELS.get(self.ai_difficulty, {})
        double_biomass = ai_cfg.get("double_map_biomass", False)

        for res_data in map_data["resources"]:
            amount = res_data.amount
            if double_biomass and res_data.type == "biomass":
                amount *= 2
            self.resources.append(ResourceNode(res_data.type, res_data.x, res_data.y, amount))

        for spawn in map_data["spawns"]:
            owner_id = spawn["id"]
            faction = spawn["faction"]
            sx, sy = spawn["x"], spawn["y"]

            if owner_id == 0:
                range_bonus = (22 if upgrades.get("forum_atk_range") else 0) + (55 if upgrades.get("forum_atk_sight_range") else 0)
                base = Building(owner_id, faction, "TownHall", sx, sy,
                                hp_bonus=int(1000 * hp_bonus_bld), armor_bonus=armor_bonus_bld, range_bonus=range_bonus)
                if upgrades.get("forum_atk_sight_range"):
                    base.vision_radius = int(base.vision_radius * 1.25)
                self.buildings.append(base)

                if upgrades.get("double_base_res_cap"):
                    for r in self.resources:
                        if math.hypot(r.x - sx, r.y - sy) < 400:
                            r.amount *= 2
                            r.max_amount *= 2

                num_workers = 3 + (1 if upgrades.get("extra_worker_start") else 0)
                worker_offsets = [(-30, 40), (0, 50), (30, 40), (-45, 50), (45, 50)]
                for i in range(num_workers):
                    offset = worker_offsets[i % len(worker_offsets)]
                    u = Unit(owner_id, faction, "Worker", sx + offset[0], sy + offset[1],
                             hp_bonus=int(60 * hp_bonus_units), attack_bonus=int(5 * atk_bonus_units))
                    self.units.append(u)

                if upgrades.get("extra_melee_start"):
                    u_inf = Unit(owner_id, faction, "Infantry", sx, sy + 60,
                                 hp_bonus=int(150 * hp_bonus_units), attack_bonus=int(18 * atk_bonus_units))
                    self.units.append(u_inf)

                if upgrades.get("start_with_scout"):
                    u_scout = Unit(owner_id, faction, "Scout", sx + 60, sy + 30,
                                   hp_bonus=int(70 * hp_bonus_units), attack_bonus=int(6 * atk_bonus_units))
                    self.units.append(u_scout)

                if upgrades.get("hero_unlocked"):
                    hero_u = Unit(owner_id, faction, "Hero", sx + 20, sy - 50,
                                  hp_bonus=int(200 * hp_bonus_units), attack_bonus=int(25 * atk_bonus_units))
                    if upgrades.get("hero_archer"):
                        hero_u.is_hero_archer = True
                        hero_u.attack_range = 180
                    if upgrades.get("hero_range_boost"):
                        hero_u.attack_range = int(hero_u.attack_range * 1.25)
                    self.units.append(hero_u)
            else:
                base_type = "Hive" if faction == config.FACTION_ALIEN else "TownHall"
                base = Building(owner_id, faction, base_type, sx, sy)
                self.buildings.append(base)

                a_cfg = AI_DIFFICULTY_LEVELS.get(self.ai_difficulty, {})
                num_sw = a_cfg.get("extra_starting_swarmers", 0)
                for i in range(num_sw):
                    u_type = "Swarmer" if faction == config.FACTION_ALIEN else "Infantry"
                    u_sw = Unit(owner_id, faction, u_type, sx + (i + 1) * 20, sy - 30)
                    self.units.append(u_sw)

                num_drones = 3 + a_cfg.get("extra_starting_drones", 0)
                worker_type = "Drone" if faction == config.FACTION_ALIEN else "Worker"
                offsets = [(-30, 40), (0, 50), (30, 40), (-45, 50), (45, 50), (-60, 40), (60, 40)]
                for i in range(num_drones):
                    offset = offsets[i % len(offsets)]
                    u = Unit(owner_id, faction, worker_type, sx + offset[0], sy + offset[1])
                    self.units.append(u)

                ai_ctrl = AIController(owner_id=owner_id, faction=faction, difficulty=self.ai_difficulty)
                self.ai_controllers.append(ai_ctrl)

    def _start_iacia_game(self):
        ai_players = self.iacia_config.get("ai_players", [])
        m_type = self.iacia_config.get("map_type", 1)
        self.map_type = m_type

        # Setup teams
        for p in ai_players:
            pid = p["id"]
            self.teams[pid] = p["team"]
            f = p.get("faction", config.FACTION_ALIEN)
            if f == config.FACTION_HUMAN:
                self.resources_player[pid] = {"gold": 300, "wood": 300, "food": 200, "biomass": 0}
            else:
                self.resources_player[pid] = {"gold": 0, "wood": 0, "food": 0, "biomass": 300}
            self.resources_gathered_player[pid] = dict(self.resources_player[pid])

        map_gen = MapGenerator(config.MAP_WIDTH, config.MAP_HEIGHT)
        map_data = map_gen.generate_map(num_players=len(ai_players), map_type=m_type)

        for res_data in map_data["resources"]:
            self.resources.append(ResourceNode(res_data.type, res_data.x, res_data.y, res_data.amount))

        from src.ai.ai_tech import AI_DIFFICULTY_LEVELS
        for idx, spawn in enumerate(map_data["spawns"]):
            if idx >= len(ai_players):
                break
            p_data = ai_players[idx]
            owner_id = p_data["id"]
            faction = p_data.get("faction", spawn["faction"])
            diff = p_data.get("difficulty", 5)
            sx, sy = spawn["x"], spawn["y"]

            b_type = "Hive" if faction == config.FACTION_ALIEN else "TownHall"
            base = Building(owner_id, faction, b_type, sx, sy)
            self.buildings.append(base)

            a_cfg = AI_DIFFICULTY_LEVELS.get(diff, {})
            w_type = "Drone" if faction == config.FACTION_ALIEN else "Worker"
            num_workers = 3 + a_cfg.get("extra_starting_drones", 0)
            offsets = [(-30, 40), (0, 50), (30, 40), (-45, 50), (45, 50), (-60, 40), (60, 40)]
            for i in range(num_workers):
                offset = offsets[i % len(offsets)]
                u = Unit(owner_id, faction, w_type, sx + offset[0], sy + offset[1])
                self.units.append(u)

            num_sw = a_cfg.get("extra_starting_swarmers", 0)
            sw_type = "Swarmer" if faction == config.FACTION_ALIEN else "Infantry"
            for i in range(num_sw):
                u_sw = Unit(owner_id, faction, sw_type, sx + (i + 1) * 20, sy - 30)
                self.units.append(u_sw)

            ai_ctrl = AIController(owner_id=owner_id, faction=faction, difficulty=diff)
            self.ai_controllers.append(ai_ctrl)

    def get_map_resource_factor(self):
        if self.map_type == 2:
            return 0.75
        elif self.map_type == 3:
            return 0.50
        elif self.map_type == 4:
            return 1.25
        elif self.map_type == 5:
            return 1.50
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
        upgrades = self.save_manager.data.get("upgrades", {}) if hasattr(self, 'save_manager') else {}
        house_extra_pop = (1 if upgrades.get("house_pop_1") else 0) + (1 if upgrades.get("house_pop_2") else 0) + (1 if upgrades.get("house_pop_3") else 0)

        bonus_pop = 0
        for b in self.buildings:
            if b.alive and b.owner_id == owner_id and getattr(b, 'is_constructed', True):
                p_bonus = b.pop_bonus
                if b.building_type == "House" and owner_id == 0:
                    p_bonus += house_extra_pop
                bonus_pop += p_bonus

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
                    # AI Level 9 double swarmer check
                    units_to_spawn = [produced_unit]
                    if building.owner_id != 0 and produced_unit == "Swarmer":
                        for ai in self.ai_controllers:
                            if ai.owner_id == building.owner_id and ai.config.get("double_swarmer_production"):
                                units_to_spawn.append("Swarmer")
                                break

                    for p_unit in units_to_spawn:
                        # Spawner l'unité produite au pied du bâtiment
                        new_u = Unit(building.owner_id, building.faction, p_unit, building.x, building.y + building.radius + 15)

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

        # Mise à jour des projectiles
        for proj in list(self.projectiles):
            if proj.alive:
                proj.update(dt, self)
            else:
                self.projectiles.remove(proj)

        # Mise à jour des IA
        for ai in self.ai_controllers:
            ai.update(dt, self)

        # Vérification des conditions de victoire/défaite/spectateur
        if self.is_spectator:
            active_teams = set()
            for entity in self.units + self.buildings:
                if entity.alive:
                    t = self.teams.get(entity.owner_id, entity.owner_id)
                    active_teams.add(t)

            if len(active_teams) <= 1:
                self.state = "SPECTATOR_END"
                self.winning_team = list(active_teams)[0] if active_teams else None
        else:
            player_buildings = [b for b in self.buildings if b.owner_id == 0]
            player_units = [u for u in self.units if u.owner_id == 0]

            enemy_buildings = [b for b in self.buildings if self.are_enemies(0, b.owner_id)]
            enemy_units = [u for u in self.units if self.are_enemies(0, u.owner_id)]

            if not player_buildings and not player_units:
                self.state = "DEFEAT"
                rewards = Rewards.calculate_rewards(False, self.num_ais, self.ai_difficulty, survival_time=self.game_time, map_type=self.map_type)
                self.last_match_rewards = rewards
                if hasattr(self, 'save_manager') and self.save_manager:
                    self.save_manager.add_points(
                        landshard=rewards[config.POINT_TYPE_COMMAND],
                        swarmerblood=rewards[config.POINT_TYPE_FORGE],
                        pykrite=rewards[config.POINT_TYPE_ARCHITECTURE]
                    )

            elif not enemy_buildings and not enemy_units:
                self.state = "VICTORY"
                rewards = Rewards.calculate_rewards(True, self.num_ais, self.ai_difficulty, survival_time=self.game_time, map_type=self.map_type)
                self.last_match_rewards = rewards
                if hasattr(self, 'save_manager') and self.save_manager:
                    self.save_manager.add_points(
                        landshard=rewards[config.POINT_TYPE_COMMAND],
                        swarmerblood=rewards[config.POINT_TYPE_FORGE],
                        pykrite=rewards[config.POINT_TYPE_ARCHITECTURE]
                    )
