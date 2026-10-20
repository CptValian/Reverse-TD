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

        pts_text = f"LandShard: {ls_pts}   |   SwarmerBlood: {sb_pts}   |   Pykrite: {py_pts}"
        pts_surf = self.bold_font.render(pts_text, True, config.COLOR_UI_TEXT)
        surface.blit(pts_surf, (self.screen_width // 2 - pts_surf.get_width() // 2, 58))

        buttons = {}

        # Tabs
        tab_w = 300
        tab_h = 42
        tab_y = 90
        start_x = self.screen_width // 2 - (tab_w * 3 + 20) // 2

        tab_tree_rect = pygame.Rect(start_x, tab_y, tab_w, tab_h)
        tab_troops_rect = pygame.Rect(start_x + tab_w + 10, tab_y, tab_w, tab_h)
        tab_bld_rect = pygame.Rect(start_x + (tab_w + 10) * 2, tab_y, tab_w, tab_h)

        def draw_tab(rect, label, is_active):
            bg_col = config.COLOR_UI_PANEL if not is_active else (60, 80, 110)
            border_col = config.COLOR_UI_ACCENT if is_active else (100, 100, 100)
            pygame.draw.rect(surface, bg_col, rect, border_radius=6)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=6)
            t_surf = self.bold_font.render(label, True, config.COLOR_UI_TEXT if is_active else (180, 180, 180))
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + 10))

        draw_tab(tab_tree_rect, "1. Tech Tree (LandShard)", self.active_tab == "skill_tree")
        draw_tab(tab_troops_rect, "2. Troops (SwarmerBlood)", self.active_tab == "troops")
        draw_tab(tab_bld_rect, "3. Buildings (Pykrite)", self.active_tab == "buildings")

        buttons["tab_tree"] = tab_tree_rect
        buttons["tab_troops"] = tab_troops_rect
        buttons["tab_buildings"] = tab_bld_rect

        upg_data = self.save_manager.data.get("upgrades", {})

        # Draw active tab content
        if self.active_tab == "skill_tree":
            self._draw_skill_tree_tab(surface, buttons, upg_data, ls_pts)
        elif self.active_tab == "troops":
            self._draw_troops_tab(surface, buttons, upg_data, sb_pts)
        elif self.active_tab == "buildings":
            self._draw_buildings_tab(surface, buttons, upg_data, py_pts)

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
            {
                "key": "starting_res_1",
                "name": "Starting Cache I",
                "desc": "+100 Starting Resources",
                "cost": 20,
                "parents": [],
                "pos": (200, 200)
            },
            {
                "key": "wood_stockpile_unlocked",
                "name": "Lumber Stockpile",
                "desc": "Drop-off for Wood Workers",
                "cost": 20,
                "parents": [],
                "pos": (550, 200)
            },
            {
                "key": "gold_stockpile_unlocked",
                "name": "Gold Stockpile",
                "desc": "Drop-off for Gold Workers",
                "cost": 20,
                "parents": [],
                "pos": (900, 200)
            },
            {
                "key": "food_stockpile_unlocked",
                "name": "Moulin / Grain Mill",
                "desc": "Drop-off for Food Workers",
                "cost": 20,
                "parents": [],
                "pos": (1250, 200)
            },
            {
                "key": "house_unlocked",
                "name": "Peasant Houses",
                "desc": "Build Houses for +5 Pop Max",
                "cost": 20,
                "parents": [],
                "pos": (1600, 200)
            },
            {
                "key": "extra_worker_start",
                "name": "Extra Worker",
                "desc": "Start with +1 Worker",
                "cost": 25,
                "parents": ["starting_res_1"],
                "pos": (100, 380)
            },
            {
                "key": "extra_melee_start",
                "name": "Extra Melee Unit",
                "desc": "Start with +1 Melee Unit",
                "cost": 25,
                "parents": ["starting_res_1"],
                "pos": (380, 380)
            },
            {
                "key": "archer_unlocked",
                "name": "Unlock Archers",
                "desc": "Train Archers in Barracks",
                "cost": 30,
                "parents": ["starting_res_1"],
                "pos": (660, 380)
            },
            {
                "key": "wall_unlocked",
                "name": "Wooden Walls",
                "desc": "Build Defensive Wooden Walls",
                "cost": 25,
                "parents": ["wood_stockpile_unlocked"],
                "pos": (940, 380)
            },
            {
                "key": "farm_unlocked",
                "name": "Farms & Grain",
                "desc": "Harvest Food for Troops",
                "cost": 25,
                "parents": ["wood_stockpile_unlocked"],
                "pos": (1500, 380)
            },
            {
                "key": "garrison_unlocked",
                "name": "Forum Garrison",
                "desc": "Garrison Peasants into Town Hall",
                "cost": 30,
                "parents": ["house_unlocked"],
                "pos": (1780, 380)
            },
            {
                "key": "ageing_up_2",
                "name": "Ageing Up II (Feudal)",
                "desc": "Advance Age (Boost Bld HP & unlocks)",
                "cost": 50,
                "parents": ["archer_unlocked", "wall_unlocked", "farm_unlocked"],
                "pos": (940, 560)
            },
            {
                "key": "tower_unlocked",
                "name": "Watchtower",
                "desc": "High sight range watchtower",
                "cost": 30,
                "parents": ["ageing_up_2"],
                "pos": (500, 740)
            },
            {
                "key": "arrow_tower_unlocked",
                "name": "Arrow Tower",
                "desc": "Defensive archer shooting tower",
                "cost": 35,
                "parents": ["ageing_up_2"],
                "pos": (780, 740)
            },
            {
                "key": "looting_unlocked",
                "name": "Looting",
                "desc": "+5 Food per troop kill",
                "cost": 30,
                "parents": ["ageing_up_2"],
                "pos": (940, 740)
            },
            {
                "key": "townhall_unlocked",
                "name": "Secondary Keep",
                "desc": "Build Additional Town Halls",
                "cost": 40,
                "parents": ["ageing_up_2"],
                "pos": (1220, 740)
            },
            {
                "key": "tower_range_unlocked",
                "name": "Arrow Tower Range",
                "desc": "Arrow tower +10% range",
                "cost": 25,
                "parents": ["arrow_tower_unlocked"],
                "pos": (780, 920)
            },
            {
                "key": "worker_spawn_speed",
                "name": "Fast Worker Guild",
                "desc": "Worker spawn time -10%",
                "cost": 15,
                "parents": ["extra_worker_start"],
                "pos": (100, 740)
            },
            {
                "key": "melee_spawn_speed",
                "name": "Footman Drill",
                "desc": "Melee spawn time -10%",
                "cost": 15,
                "parents": ["extra_melee_start"],
                "pos": (380, 740)
            },
            {
                "key": "archer_spawn_speed",
                "name": "Bowyer Crafting",
                "desc": "Archer spawn time -10%",
                "cost": 15,
                "parents": ["archer_unlocked"],
                "pos": (660, 560)
            },
            {
                "key": "forum_atk_sight_range",
                "name": "Forum Citadel",
                "desc": "Forum Atk & Sight Range +25%",
                "cost": 25,
                "parents": ["forum_atk_range"],
                "pos": (2060, 740)
            },
            {
                "key": "high_starting_res",
                "name": "Starting Cache II",
                "desc": "+250 Starting Resources",
                "cost": 20,
                "parents": ["starting_res_1"],
                "pos": (200, 560)
            },
            {
                "key": "start_with_scout",
                "name": "Frontier Scout",
                "desc": "Start with 1 Scout unit",
                "cost": 20,
                "parents": ["scout_unlocked"],
                "pos": (100, 920)
            },
            {
                "key": "bank_unlocked",
                "name": "Royal Bank",
                "desc": "Passive gold generation building",
                "cost": 30,
                "parents": ["gold_stockpile_unlocked"],
                "pos": (1220, 560)
            },
            {
                "key": "sanctuary_unlocked",
                "name": "Sanctuary / Healer",
                "desc": "Heals 1 troop @ 8 HP/sec",
                "cost": 30,
                "parents": ["farm_unlocked"],
                "pos": (1500, 560)
            },
            {
                "key": "forum_atk_range",
                "name": "Forum Ballista",
                "desc": "Forum Attack Range +10%",
                "cost": 30,
                "parents": ["garrison_unlocked"],
                "pos": (1780, 560)
            },
            {
                "key": "watchtower_sight",
                "name": "Tower Optics",
                "desc": "Watchtower Sight +20%",
                "cost": 25,
                "parents": ["tower_unlocked"],
                "pos": (500, 920)
            },
            {
                "key": "scout_unlocked",
                "name": "Unlock Scout",
                "desc": "Fast reconnaissance unit",
                "cost": 25,
                "parents": ["extra_worker_start"],
                "pos": (100, 560)
            },
            {
                "key": "building_repair_unlocked",
                "name": "Building Repair",
                "desc": "Workers repair structures",
                "cost": 30,
                "parents": ["house_unlocked"],
                "pos": (2060, 560)
            },
            {
                "key": "double_base_res_cap",
                "name": "Rich Deposit Caches",
                "desc": "Double resource capacity at Forum",
                "cost": 35,
                "parents": ["gold_stockpile_unlocked"],
                "pos": (1220, 380)
            },
            {
                "key": "forum_passive_arrow",
                "name": "Sentry Guard Bow",
                "desc": "Forum fires 1 arrow (+1 arrow)",
                "cost": 35,
                "parents": ["garrison_unlocked"],
                "pos": (1780, 740)
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
            txt_name = self.bold_font.render(f"{upg['name']}  [Niv. {lvl}]", True, config.COLOR_UI_TEXT)
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
