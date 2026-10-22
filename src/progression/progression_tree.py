import pygame
import config

class ProgressionUI:
    def __init__(self, save_manager, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT):
        self.save_manager = save_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.font = pygame.font.SysFont("Arial", 16)
        self.bold_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 13)
        self.active_tab = "skill_tree"  # "skill_tree", "troops", "buildings"
        self.active_faction = config.FACTION_HUMAN  # FACTION_HUMAN or FACTION_ALIEN
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.zoom_level = 1.0
        self.is_dragging = False
        self.drag_start_pos = (0, 0)

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        title = self.title_font.render("UPGRADE CENTER & SKILL TREE", True, config.COLOR_UI_ACCENT)
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 20))

        # Display points
        pts = self.save_manager.get_points()
        ls_pts = pts.get("LandShard", pts.get("Commandement", 0))
        sb_pts = pts.get("SwarmerBlood", pts.get("Forge", 0))
        py_pts = pts.get("Pykrite", pts.get("Architecture", 0))
        muc_pts = pts.get("Muculus", 0)
        conj_pts = pts.get("Conjulat", 0)
        mass_pts = pts.get("Mass", 0)

        pts_text = f"LandShard: {ls_pts} | SwarmerBlood: {sb_pts} | Pykrite: {py_pts}   ||   Muculus: {muc_pts} | Conjulat: {conj_pts} | Mass: {mass_pts}"
        pts_surf = self.bold_font.render(pts_text, True, config.COLOR_UI_TEXT)
        surface.blit(pts_surf, (self.screen_width // 2 - pts_surf.get_width() // 2, 58))

        buttons = {}

        # Faction Switcher
        fac_w = 200
        fac_h = 36
        fac_y = 85
        fac_human_rect = pygame.Rect(self.screen_width // 2 - fac_w - 10, fac_y, fac_w, fac_h)
        fac_alien_rect = pygame.Rect(self.screen_width // 2 + 10, fac_y, fac_w, fac_h)

        def draw_faction_btn(rect, label, is_active):
            bg_col = (40, 70, 50) if (is_active and label == "ALIEN FACTION") else ((50, 70, 110) if is_active else (30, 32, 40))
            border_col = (100, 220, 120) if (is_active and label == "ALIEN FACTION") else (config.COLOR_UI_ACCENT if is_active else (80, 80, 80))
            pygame.draw.rect(surface, bg_col, rect, border_radius=6)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=6)
            t_surf = self.bold_font.render(label, True, (255, 255, 255) if is_active else (160, 160, 160))
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + 8))

        draw_faction_btn(fac_human_rect, "HUMAN FACTION", self.active_faction == config.FACTION_HUMAN)
        draw_faction_btn(fac_alien_rect, "ALIEN FACTION", self.active_faction == config.FACTION_ALIEN)

        buttons["fac_human"] = fac_human_rect
        buttons["fac_alien"] = fac_alien_rect

        # Tabs
        tab_w = 280
        tab_h = 40
        tab_y = 130
        start_x = self.screen_width // 2 - (tab_w * 3 + 20) // 2

        tab_tree_rect = pygame.Rect(start_x, tab_y, tab_w, tab_h)
        tab_troops_rect = pygame.Rect(start_x + tab_w + 10, tab_y, tab_w, tab_h)
        tab_bld_rect = pygame.Rect(start_x + (tab_w + 10) * 2, tab_y, tab_w, tab_h)

        def draw_tab(rect, label, is_active):
            bg_col = config.COLOR_UI_PANEL if not is_active else ((40, 75, 50) if self.active_faction == config.FACTION_ALIEN else (60, 80, 110))
            border_col = (100, 220, 120) if (is_active and self.active_faction == config.FACTION_ALIEN) else (config.COLOR_UI_ACCENT if is_active else (100, 100, 100))
            pygame.draw.rect(surface, bg_col, rect, border_radius=6)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=6)
            t_surf = self.bold_font.render(label, True, config.COLOR_UI_TEXT if is_active else (180, 180, 180))
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + 9))

        if self.active_faction == config.FACTION_HUMAN:
            draw_tab(tab_tree_rect, "1. Tech Tree (LandShard)", self.active_tab == "skill_tree")
            draw_tab(tab_troops_rect, "2. Troops (SwarmerBlood)", self.active_tab == "troops")
            draw_tab(tab_bld_rect, "3. Buildings (Pykrite)", self.active_tab == "buildings")
        else:
            draw_tab(tab_tree_rect, "1. Alien Tech (Muculus)", self.active_tab == "skill_tree")
            draw_tab(tab_troops_rect, "2. Alien Troops (Conjulat)", self.active_tab == "troops")
            draw_tab(tab_bld_rect, "3. Alien Structures (Mass)", self.active_tab == "buildings")

        buttons["tab_tree"] = tab_tree_rect
        buttons["tab_troops"] = tab_troops_rect
        buttons["tab_buildings"] = tab_bld_rect

        upg_data = self.save_manager.data.get("upgrades", {})

        # Draw active tab content according to active faction
        if self.active_faction == config.FACTION_HUMAN:
            if self.active_tab == "skill_tree":
                self._draw_skill_tree_tab(surface, buttons, upg_data, ls_pts)
            elif self.active_tab == "troops":
                self._draw_troops_tab(surface, buttons, upg_data, sb_pts)
            elif self.active_tab == "buildings":
                self._draw_buildings_tab(surface, buttons, upg_data, py_pts)
        else:
            if self.active_tab == "skill_tree":
                self._draw_alien_skill_tree_tab(surface, buttons, upg_data, muc_pts)
            elif self.active_tab == "troops":
                self._draw_alien_troops_tab(surface, buttons, upg_data, conj_pts)
            elif self.active_tab == "buildings":
                self._draw_alien_buildings_tab(surface, buttons, upg_data, mass_pts)

        # Back Button
        back_btn = pygame.Rect(self.screen_width // 2 - 120, self.screen_height - 65, 240, 45)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=6)
        back_txt = self.bold_font.render("BACK TO MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 12))
        buttons["back"] = back_btn

        return buttons

    def _draw_skill_tree_tab(self, surface, buttons, upg_data, points_available):
        nodes = [
            # --- ROW 1 (ROOT FOUNDATIONS) ---
            {
                "key": "starting_res_1",
                "name": "Starting Cache I",
                "desc": "+100 Starting Resources",
                "cost": 20,
                "parents": [],
                "pos": (300, 160)
            },
            {
                "key": "wood_stockpile_unlocked",
                "name": "Lumber Stockpile",
                "desc": "Drop-off for Wood Workers",
                "cost": 20,
                "parents": [],
                "pos": (700, 160)
            },
            {
                "key": "gold_stockpile_unlocked",
                "name": "Gold Stockpile",
                "desc": "Drop-off for Gold Workers",
                "cost": 20,
                "parents": [],
                "pos": (1100, 160)
            },
            {
                "key": "house_unlocked",
                "name": "Peasant Houses",
                "desc": "Build Houses for +5 Pop Max",
                "cost": 20,
                "parents": [],
                "pos": (1500, 160)
            },

            # --- ROW 2 ---
            {
                "key": "extra_worker_start",
                "name": "Extra Worker",
                "desc": "Start with +1 Worker",
                "cost": 25,
                "parents": ["starting_res_1"],
                "pos": (160, 320)
            },
            {
                "key": "extra_melee_start",
                "name": "Extra Melee Unit",
                "desc": "Start with +1 Melee Unit",
                "cost": 25,
                "parents": ["starting_res_1"],
                "pos": (440, 320)
            },
            {
                "key": "food_stockpile_unlocked",
                "name": "Moulin / Grain Mill",
                "desc": "Drop-off for Food Workers",
                "cost": 20,
                "parents": ["house_unlocked"],
                "pos": (1360, 320)
            },
            {
                "key": "garrison_unlocked",
                "name": "Forum Garrison",
                "desc": "Garrison Peasants into Town Hall",
                "cost": 30,
                "parents": ["house_unlocked"],
                "pos": (1640, 320)
            },
            {
                "key": "house_pop_1",
                "name": "Expanded Cottages I",
                "desc": "+1 population per House",
                "cost": 20,
                "parents": ["house_unlocked"],
                "pos": (1920, 320)
            },

            # --- ROW 3 ---
            {
                "key": "scout_unlocked",
                "name": "Unlock Scout",
                "desc": "Fast reconnaissance unit",
                "cost": 25,
                "parents": ["extra_worker_start"],
                "pos": (160, 480)
            },
            {
                "key": "high_starting_res",
                "name": "Starting Cache II",
                "desc": "+100 Starting Resources",
                "cost": 20,
                "parents": ["extra_melee_start"],
                "pos": (440, 480)
            },
            {
                "key": "archer_unlocked",
                "name": "Unlock Archers",
                "desc": "Train Archers in Barracks",
                "cost": 30,
                "parents": ["extra_melee_start", "wood_stockpile_unlocked"],
                "pos": (720, 480)
            },
            {
                "key": "wall_unlocked",
                "name": "Wooden Walls",
                "desc": "Build Defensive Wooden Walls",
                "cost": 25,
                "parents": ["wood_stockpile_unlocked"],
                "pos": (980, 480)
            },
            {
                "key": "double_base_res_cap",
                "name": "Rich Deposit Caches",
                "desc": "Double resource capacity at Forum",
                "cost": 35,
                "parents": ["gold_stockpile_unlocked"],
                "pos": (1240, 480)
            },
            {
                "key": "farm_unlocked",
                "name": "Farms & Grain",
                "desc": "Harvest Food for Troops",
                "cost": 25,
                "parents": ["food_stockpile_unlocked"],
                "pos": (1500, 480)
            },
            {
                "key": "building_repair_unlocked",
                "name": "Building Repair",
                "desc": "Workers repair structures",
                "cost": 30,
                "parents": ["garrison_unlocked"],
                "pos": (1760, 480)
            },
            {
                "key": "house_pop_2",
                "name": "Expanded Cottages II",
                "desc": "+1 population per House",
                "cost": 25,
                "parents": ["house_pop_1"],
                "pos": (2020, 480)
            },

            # --- ROW 4 ---
            {
                "key": "worker_spawn_speed",
                "name": "Fast Worker Guild",
                "desc": "Worker spawn time -10%",
                "cost": 15,
                "parents": ["scout_unlocked"],
                "pos": (160, 640)
            },
            {
                "key": "starting_cache_3",
                "name": "Starting Cache III",
                "desc": "+100 Starting Resources",
                "cost": 25,
                "parents": ["high_starting_res"],
                "pos": (440, 640)
            },
            {
                "key": "archer_spawn_speed",
                "name": "Bowyer Crafting",
                "desc": "Archer spawn time -10%",
                "cost": 15,
                "parents": ["archer_unlocked"],
                "pos": (720, 640)
            },
            {
                "key": "ageing_up_2",
                "name": "Ageing Up II (Feudal)",
                "desc": "Advance Age (Boost Bld HP & unlocks)",
                "cost": 50,
                "parents": ["archer_unlocked", "wall_unlocked", "farm_unlocked"],
                "pos": (980, 640)
            },
            {
                "key": "near_base_res_boost",
                "name": "Base Deposit Boost",
                "desc": "x1.5 Resource Node Quantity Near Base",
                "cost": 30,
                "parents": ["double_base_res_cap"],
                "pos": (1240, 640)
            },
            {
                "key": "sanctuary_unlocked",
                "name": "Sanctuary / Healer",
                "desc": "Heals 1 troop @ 8 HP/sec",
                "cost": 30,
                "parents": ["farm_unlocked"],
                "pos": (1500, 640)
            },
            {
                "key": "forum_atk_range",
                "name": "Forum Ballista",
                "desc": "Forum Attack Range +10%",
                "cost": 30,
                "parents": ["building_repair_unlocked"],
                "pos": (1760, 640)
            },
            {
                "key": "house_pop_3",
                "name": "Expanded Cottages III",
                "desc": "+1 population per House",
                "cost": 30,
                "parents": ["house_pop_2"],
                "pos": (2020, 640)
            },

            # --- ROW 5 ---
            {
                "key": "start_with_scout",
                "name": "Frontier Scout",
                "desc": "Start with 1 Scout unit",
                "cost": 20,
                "parents": ["worker_spawn_speed"],
                "pos": (160, 800)
            },
            {
                "key": "melee_spawn_speed",
                "name": "Footman Drill",
                "desc": "Melee spawn time -10%",
                "cost": 15,
                "parents": ["starting_cache_3"],
                "pos": (440, 800)
            },
            {
                "key": "hero_unlocked",
                "name": "Hero Knight",
                "desc": "Unlocks Hero Knight (Leveling & Kills)",
                "cost": 35,
                "parents": ["ageing_up_2"],
                "pos": (720, 800)
            },
            {
                "key": "tower_unlocked",
                "name": "Watchtower",
                "desc": "High sight range watchtower",
                "cost": 30,
                "parents": ["ageing_up_2"],
                "pos": (980, 800)
            },
            {
                "key": "arrow_tower_unlocked",
                "name": "Arrow Tower",
                "desc": "Defensive archer shooting tower",
                "cost": 35,
                "parents": ["ageing_up_2"],
                "pos": (1240, 800)
            },
            {
                "key": "looting_unlocked",
                "name": "Looting",
                "desc": "+5 Food per troop kill",
                "cost": 30,
                "parents": ["ageing_up_2"],
                "pos": (1500, 800)
            },
            {
                "key": "forum_passive_arrow",
                "name": "Sentry Guard Bow",
                "desc": "Forum fires 1 arrow (+1 arrow)",
                "cost": 35,
                "parents": ["forum_atk_range"],
                "pos": (1760, 800)
            },

            # --- ROW 6 ---
            {
                "key": "hero_archer",
                "name": "Hero Archer",
                "desc": "Hero attacks at range with longbow",
                "cost": 30,
                "parents": ["hero_unlocked"],
                "pos": (720, 960)
            },
            {
                "key": "watchtower_sight",
                "name": "Tower Optics",
                "desc": "Watchtower Sight +20%",
                "cost": 25,
                "parents": ["tower_unlocked"],
                "pos": (980, 960)
            },
            {
                "key": "tower_range_unlocked",
                "name": "Arrow Tower Range",
                "desc": "Arrow tower +10% range",
                "cost": 25,
                "parents": ["arrow_tower_unlocked"],
                "pos": (1240, 960)
            },
            {
                "key": "sanctuary_boost",
                "name": "Advanced Sanctuary",
                "desc": "Range +40% & Heals +4 HP/s",
                "cost": 30,
                "parents": ["sanctuary_unlocked"],
                "pos": (1500, 960)
            },
            {
                "key": "bank_unlocked",
                "name": "Royal Bank",
                "desc": "Passive gold generation building",
                "cost": 30,
                "parents": ["ageing_up_2", "double_base_res_cap"],
                "pos": (1760, 960)
            },
            {
                "key": "forum_atk_sight_range",
                "name": "Forum Citadel",
                "desc": "Forum Atk & Sight Range +25%",
                "cost": 25,
                "parents": ["forum_passive_arrow"],
                "pos": (2020, 960)
            },

            # --- ROW 7 ---
            {
                "key": "hero_range_boost",
                "name": "Heroic Range",
                "desc": "+25% attack range for Hero",
                "cost": 30,
                "parents": ["hero_archer"],
                "pos": (720, 1120)
            },
            {
                "key": "tower_extra_projectile",
                "name": "Tower Volley",
                "desc": "Defensive Towers fire +1 Arrow",
                "cost": 35,
                "parents": ["arrow_tower_unlocked"],
                "pos": (1240, 1120)
            },
            {
                "key": "temple_unlocked",
                "name": "Holy Temple & Monk",
                "desc": "Train Monks (+2 HP/s Healing Beam)",
                "cost": 35,
                "parents": ["sanctuary_unlocked"],
                "pos": (1500, 1120)
            },
            {
                "key": "townhall_unlocked",
                "name": "Secondary Keep",
                "desc": "Build Additional Town Halls",
                "cost": 40,
                "parents": ["ageing_up_2"],
                "pos": (1760, 1120)
            }
        ]

        node_map = {n["key"]: n for n in nodes}

        ox = self.camera_offset_x
        oy = self.camera_offset_y
        zoom = self.zoom_level

        # Helper to scale relative to center of view
        def transform_pos(pos):
            cx = (pos[0] - self.screen_width // 2) * zoom + self.screen_width // 2 + ox
            cy = (pos[1] - self.screen_height // 2) * zoom + self.screen_height // 2 + oy
            return int(cx), int(cy)

        # 1. Draw connecting lines between parents and children
        for n in nodes:
            cx, cy = transform_pos(n["pos"])
            cx, cy = transform_pos(n["pos"])
            for parent_key in n["parents"]:
                parent = node_map[parent_key]
                px, py = transform_pos(parent["pos"])
                is_parent_unlocked = upg_data.get(parent_key, 0) >= 1
                is_node_unlocked = upg_data.get(n["key"], 0) >= 1

                if is_node_unlocked:
                    line_color = (76, 175, 80)
                elif is_parent_unlocked:
                    line_color = (255, 179, 0)
                else:
                    line_color = (80, 80, 80)

                pygame.draw.line(surface, line_color, (px, py + int(40 * zoom)), (cx, cy - int(40 * zoom)), max(1, int(3 * zoom)))

        # Dynamic fonts based on zoom level so text stays anchored inside cards
        bold_size = max(8, min(22, int(15 * zoom)))
        small_size = max(6, min(18, int(12 * zoom)))
        z_bold_font = pygame.font.SysFont("Arial", bold_size, bold=True)
        z_small_font = pygame.font.SysFont("Arial", small_size)

        # 2. Draw node cards
        for n in nodes:
            key = n["key"]
            cx, cy = transform_pos(n["pos"])
            card_w = int(220 * zoom)
            card_h = int(82 * zoom)
            card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)

            is_unlocked = upg_data.get(key, 0) >= 1
            parents_unlocked = all(upg_data.get(p, 0) >= 1 for p in n["parents"])

            if is_unlocked:
                bg_col = (25, 50, 35)
                border_col = (76, 175, 80)
                status_txt = "UNLOCKED"
                status_col = (100, 255, 100)
            elif parents_unlocked:
                bg_col = config.COLOR_UI_PANEL
                border_col = config.COLOR_UI_ACCENT
                status_txt = f"Cost: {n['cost']} LandShard"
                status_col = config.COLOR_UI_ACCENT
            else:
                bg_col = (30, 32, 38)
                border_col = (70, 70, 75)
                status_txt = "LOCKED"
                status_col = (120, 120, 120)

            pygame.draw.rect(surface, bg_col, card_rect, border_radius=max(2, int(6 * zoom)))
            pygame.draw.rect(surface, border_col, card_rect, max(1, int(2 * zoom)), border_radius=max(2, int(6 * zoom)))

            # Title
            t_title = z_bold_font.render(n["name"], True, config.COLOR_UI_TEXT if parents_unlocked or is_unlocked else (140, 140, 140))
            surface.blit(t_title, (cx - t_title.get_width() // 2, cy - int(32 * zoom)))

            # Desc
            t_desc = z_small_font.render(n["desc"], True, (180, 180, 180) if parents_unlocked or is_unlocked else (100, 100, 100))
            surface.blit(t_desc, (cx - t_desc.get_width() // 2, cy - int(10 * zoom)))

            # Status / Button label
            t_stat = z_bold_font.render(status_txt, True, status_col)
            surface.blit(t_stat, (cx - t_stat.get_width() // 2, cy + int(12 * zoom)))

            if parents_unlocked and not is_unlocked:
                buttons[key] = {
                    "rect": card_rect,
                    "type": "LandShard",
                    "cost": n["cost"],
                    "is_tree_unlock": True
                }

    def _draw_troops_tab(self, surface, buttons, upg_data, points):
        available_upgrades = [
            {"key": "worker_hp_lvl", "unit": "Worker", "name": "Peasant Worker HP (+15%)", "cost_base": 10, "stats": "HP: 60 | Atk: 5 | Range: 25 | Spd: 100"},
            {"key": "worker_speed_lvl", "unit": "Worker", "name": "Peasant Worker Movement (+10%)", "cost_base": 12, "stats": "HP: 60 | Atk: 5 | Range: 25 | Spd: 100"},

            {"key": "infantry_hp_lvl", "unit": "Infantry", "name": "Footman Soldier HP (+10%)", "cost_base": 12, "stats": "HP: 150 | Atk: 18 | Range: 30 | Spd: 90"},
            {"key": "infantry_attack_lvl", "unit": "Infantry", "name": "Footman Attack Power (+10%)", "cost_base": 15, "stats": "HP: 150 | Atk: 18 | Range: 30 | Spd: 90"},
        ]

        if upg_data.get("archer_unlocked"):
            available_upgrades.append({"key": "archer_hp_lvl", "unit": "Archer", "name": "Archer HP (+10%)", "cost_base": 15, "stats": "HP: 90 | Atk: 14 | Range: 180 | Spd: 100"})
            available_upgrades.append({"key": "archer_attack_lvl", "unit": "Archer", "name": "Archer Attack Damage (+10%)", "cost_base": 18, "stats": "HP: 90 | Atk: 14 | Range: 180 | Spd: 100"})

        self._render_upgrade_list(surface, buttons, available_upgrades, "SwarmerBlood", upg_data)

    def _draw_buildings_tab(self, surface, buttons, upg_data, points):
        available_upgrades = [
            {"key": "townhall_hp_lvl", "bld": "TownHall", "name": "Town Hall Keep Durability (+15%)", "cost_base": 15, "stats": "HP: 1000 | Armor: 0 | Pop: +10 | Range: 220"},
            {"key": "barracks_hp_lvl", "bld": "Barracks", "name": "Barracks Fortification (+15%)", "cost_base": 12, "stats": "HP: 500 | Build Time: 20s"},
        ]

        if upg_data.get("wall_unlocked"):
            available_upgrades.append({"key": "wall_hp_lvl", "bld": "Wall", "name": "Wooden Wall Health (+20%)", "cost_base": 10, "stats": "HP: 250 | Width: 20 | Length: 40"})

        if upg_data.get("tower_unlocked"):
            available_upgrades.append({"key": "tower_hp_lvl", "bld": "Tower", "name": "Watchtower Health (+15%)", "cost_base": 15, "stats": "HP: 400 | Atk: 15 | Range: 200 | Vis: 550"})
            available_upgrades.append({"key": "tower_attack_lvl", "bld": "Tower", "name": "Watchtower Arrow Damage (+10%)", "cost_base": 20, "stats": "HP: 400 | Atk: 15 | Range: 200 | Vis: 550"})

        if upg_data.get("farm_unlocked"):
            available_upgrades.append({"key": "farm_hp_lvl", "bld": "Farm", "name": "Farm Structure HP (+15%)", "cost_base": 10, "stats": "HP: 300 | Food Harvest Source"})

        if upg_data.get("wood_stockpile_unlocked") or upg_data.get("gold_stockpile_unlocked"):
            available_upgrades.append({"key": "stockpile_hp_lvl", "bld": "Stockpiles", "name": "Stockpile Reinforced Walls (+15%)", "cost_base": 10, "stats": "HP: 350 | Drop-off Depot"})

        self._render_upgrade_list(surface, buttons, available_upgrades, "Pykrite", upg_data)

    def _draw_alien_skill_tree_tab(self, surface, buttons, upg_data, points_available):
        nodes = [
            {
                "key": "alien_starting_res_1",
                "name": "Biomass Cache I",
                "desc": "+100 Starting Biomass",
                "cost": 20,
                "parents": [],
                "pos": (400, 180)
            },
            {
                "key": "alien_biomass_stockpile_unlocked",
                "name": "Biomass Depot",
                "desc": "Drop-off for Drone workers",
                "cost": 20,
                "parents": [],
                "pos": (800, 180)
            },
            {
                "key": "alien_spawning_pool_unlocked",
                "name": "Spawning Pool",
                "desc": "Morph Swarmers & Spitters",
                "cost": 25,
                "parents": ["alien_starting_res_1"],
                "pos": (400, 360)
            },
            {
                "key": "alien_biomass_gen_unlocked",
                "name": "Biomass Chamber",
                "desc": "Passive Biomass generation",
                "cost": 25,
                "parents": ["alien_biomass_stockpile_unlocked"],
                "pos": (800, 360)
            },
            {
                "key": "alien_spine_crawler_unlocked",
                "name": "Spine Crawler",
                "desc": "Defensive Organism Tower",
                "cost": 30,
                "parents": ["alien_spawning_pool_unlocked"],
                "pos": (250, 540)
            },
            {
                "key": "alien_spitter_unlocked",
                "name": "Acid Spitter",
                "desc": "Ranged Acid Spitter unit",
                "cost": 30,
                "parents": ["alien_spawning_pool_unlocked"],
                "pos": (550, 540)
            },
            {
                "key": "alien_evolution_chamber_unlocked",
                "name": "Evolution Chamber",
                "desc": "Research Bio Upgrades",
                "cost": 35,
                "parents": ["alien_biomass_gen_unlocked"],
                "pos": (800, 540)
            },
            {
                "key": "alien_creep_spread_unlocked",
                "name": "Creep Spread",
                "desc": "+25% Speed & ATK near Hive",
                "cost": 35,
                "parents": ["alien_spitter_unlocked"],
                "pos": (400, 720)
            },
            {
                "key": "alien_second_hive_unlocked",
                "name": "Secondary Hive",
                "desc": "Expand with 2nd Hive Keep",
                "cost": 40,
                "parents": ["alien_evolution_chamber_unlocked"],
                "pos": (800, 720)
            },
            {
                "key": "alien_queen_unlocked",
                "name": "Insect Queen Hero",
                "desc": "Hero Queen unit (Morph Swarmers)",
                "cost": 45,
                "parents": ["alien_creep_spread_unlocked"],
                "pos": (400, 900)
            },
            {
                "key": "alien_hive_enrage_unlocked",
                "name": "Hive Frenzy Ability",
                "desc": "+20% Attack/Speed Frenzy burst",
                "cost": 50,
                "parents": ["alien_queen_unlocked", "alien_second_hive_unlocked"],
                "pos": (600, 1080)
            }
        ]

        node_map = {n["key"]: n for n in nodes}
        ox = self.camera_offset_x
        oy = self.camera_offset_y
        zoom = self.zoom_level

        def transform_pos(pos):
            cx = (pos[0] - self.screen_width // 2) * zoom + self.screen_width // 2 + ox
            cy = (pos[1] - self.screen_height // 2) * zoom + self.screen_height // 2 + oy
            return int(cx), int(cy)

        for n in nodes:
            cx, cy = transform_pos(n["pos"])
            for parent_key in n["parents"]:
                parent = node_map[parent_key]
                px, py = transform_pos(parent["pos"])
                is_parent_unlocked = upg_data.get(parent_key, 0) >= 1
                is_node_unlocked = upg_data.get(n["key"], 0) >= 1

                if is_node_unlocked:
                    line_color = (100, 220, 120)
                elif is_parent_unlocked:
                    line_color = (255, 179, 0)
                else:
                    line_color = (80, 80, 80)

                pygame.draw.line(surface, line_color, (px, py + int(40 * zoom)), (cx, cy - int(40 * zoom)), max(1, int(3 * zoom)))

        bold_size = max(8, min(22, int(15 * zoom)))
        small_size = max(6, min(18, int(12 * zoom)))
        z_bold_font = pygame.font.SysFont("Arial", bold_size, bold=True)
        z_small_font = pygame.font.SysFont("Arial", small_size)

        for n in nodes:
            key = n["key"]
            cx, cy = transform_pos(n["pos"])
            card_w = int(220 * zoom)
            card_h = int(82 * zoom)
            card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)

            is_unlocked = upg_data.get(key, 0) >= 1
            parents_unlocked = all(upg_data.get(p, 0) >= 1 for p in n["parents"])

            if is_unlocked:
                bg_col = (20, 55, 30)
                border_col = (100, 220, 120)
                status_txt = "UNLOCKED"
                status_col = (120, 255, 140)
            elif parents_unlocked:
                bg_col = (35, 45, 38)
                border_col = (100, 200, 120)
                status_txt = f"Cost: {n['cost']} Muculus"
                status_col = (100, 220, 120)
            else:
                bg_col = (30, 32, 38)
                border_col = (70, 70, 75)
                status_txt = "LOCKED"
                status_col = (120, 120, 120)

            pygame.draw.rect(surface, bg_col, card_rect, border_radius=max(2, int(6 * zoom)))
            pygame.draw.rect(surface, border_col, card_rect, max(1, int(2 * zoom)), border_radius=max(2, int(6 * zoom)))

            t_title = z_bold_font.render(n["name"], True, config.COLOR_UI_TEXT if parents_unlocked or is_unlocked else (140, 140, 140))
            surface.blit(t_title, (cx - t_title.get_width() // 2, cy - int(32 * zoom)))

            t_desc = z_small_font.render(n["desc"], True, (180, 180, 180) if parents_unlocked or is_unlocked else (100, 100, 100))
            surface.blit(t_desc, (cx - t_desc.get_width() // 2, cy - int(10 * zoom)))

            t_stat = z_bold_font.render(status_txt, True, status_col)
            surface.blit(t_stat, (cx - t_stat.get_width() // 2, cy + int(12 * zoom)))

            if parents_unlocked and not is_unlocked:
                buttons[key] = {
                    "rect": card_rect,
                    "type": "Muculus",
                    "cost": n["cost"],
                    "is_tree_unlock": True
                }

    def _draw_alien_troops_tab(self, surface, buttons, upg_data, points):
        available_upgrades = [
            {"key": "drone_hp_lvl", "unit": "Drone", "name": "Drone Worker HP (+15%)", "cost_base": 10, "stats": "HP: 55 | Atk: 6 | Range: 25 | Spd: 105"},
            {"key": "drone_speed_lvl", "unit": "Drone", "name": "Drone Movement Speed (+10%)", "cost_base": 12, "stats": "HP: 55 | Atk: 6 | Range: 25 | Spd: 105"},

            {"key": "swarmer_hp_lvl", "unit": "Swarmer", "name": "Swarmer Vitality (+10%)", "cost_base": 12, "stats": "HP: 100 | Atk: 15 | Range: 25 | Spd: 125"},
            {"key": "swarmer_attack_lvl", "unit": "Swarmer", "name": "Swarmer Mandible Damage (+10%)", "cost_base": 15, "stats": "HP: 100 | Atk: 15 | Range: 25 | Spd: 125"},
        ]

        if upg_data.get("alien_spitter_unlocked"):
            available_upgrades.append({"key": "spitter_hp_lvl", "unit": "Spitter", "name": "Spitter HP (+10%)", "cost_base": 15, "stats": "HP: 80 | Atk: 16 | Range: 170 | Spd: 95"})
            available_upgrades.append({"key": "spitter_attack_lvl", "unit": "Spitter", "name": "Spitter Acid Power (+10%)", "cost_base": 18, "stats": "HP: 80 | Atk: 16 | Range: 170 | Spd: 95"})

        if upg_data.get("alien_queen_unlocked"):
            available_upgrades.append({"key": "queen_hp_lvl", "unit": "Queen", "name": "Insect Queen HP (+15%)", "cost_base": 20, "stats": "HP: 220 | Atk: 22 | Range: 160 | Spd: 90"})
            available_upgrades.append({"key": "queen_attack_lvl", "unit": "Queen", "name": "Insect Queen Damage (+10%)", "cost_base": 25, "stats": "HP: 220 | Atk: 22 | Range: 160 | Spd: 90"})

        self._render_upgrade_list(surface, buttons, available_upgrades, "Conjulat", upg_data)

    def _draw_alien_buildings_tab(self, surface, buttons, upg_data, points):
        available_upgrades = [
            {"key": "hive_hp_lvl", "bld": "Hive", "name": "Hive Central Durability (+15%)", "cost_base": 15, "stats": "HP: 1000 | Pop: +10"},
        ]

        if upg_data.get("alien_spawning_pool_unlocked"):
            available_upgrades.append({"key": "spawning_pool_hp_lvl", "bld": "SpawningPool", "name": "Spawning Pool Carapace (+15%)", "cost_base": 12, "stats": "HP: 500 | Build Time: 20s"})

        if upg_data.get("alien_spine_crawler_unlocked"):
            available_upgrades.append({"key": "spine_crawler_hp_lvl", "bld": "SpineCrawler", "name": "Spine Crawler Health (+15%)", "cost_base": 15, "stats": "HP: 400 | Atk: 24 | Range: 234"})
            available_upgrades.append({"key": "spine_crawler_attack_lvl", "bld": "SpineCrawler", "name": "Spine Crawler Attack Damage (+10%)", "cost_base": 20, "stats": "HP: 400 | Atk: 24 | Range: 234"})

        if upg_data.get("alien_biomass_gen_unlocked"):
            available_upgrades.append({"key": "biomass_gen_hp_lvl", "bld": "BiomassGenerator", "name": "Biomass Generator Durability (+15%)", "cost_base": 15, "stats": "HP: 350 | Passive Biomass Influx"})

        self._render_upgrade_list(surface, buttons, available_upgrades, "Mass", upg_data)

    def _render_upgrade_list(self, surface, buttons, upgrades, point_type, upg_data):
        y = 170
        x_left = self.screen_width // 2 - 380
        width = 760

        for upg in upgrades:
            key = upg["key"]
            lvl = upg_data.get(key, 0)
            cost = upg["cost_base"] * (lvl + 1)

            card_rect = pygame.Rect(x_left, y, width, 58)
            pygame.draw.rect(surface, config.COLOR_UI_PANEL, card_rect, border_radius=6)
            pygame.draw.rect(surface, (70, 75, 85), card_rect, 1, border_radius=6)

            # Name & Level
            txt_name = self.bold_font.render(f"{upg['name']}  [Lvl {lvl}]", True, config.COLOR_UI_TEXT)
            surface.blit(txt_name, (x_left + 20, y + 8))

            # Stats line
            if "stats" in upg:
                t_stats = self.small_font.render(f"Base Stats: {upg['stats']}", True, (180, 200, 220))
                surface.blit(t_stats, (x_left + 20, y + 32))

            # Upgrade Button
            btn_rect = pygame.Rect(x_left + width - 180, y + 10, 160, 38)
            pygame.draw.rect(surface, (50, 70, 95), btn_rect, border_radius=4)
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)

            btn_txt = self.font.render(f"+1 (Cost: {cost})", True, config.COLOR_UI_TEXT)
            surface.blit(btn_txt, (btn_rect.x + btn_rect.width // 2 - btn_txt.get_width() // 2, btn_rect.y + 8))

            buttons[key] = {
                "rect": btn_rect,
                "type": point_type,
                "cost_base": upg["cost_base"],
                "is_tree_unlock": False
            }

            y += 68
