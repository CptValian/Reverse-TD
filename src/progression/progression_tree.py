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

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        title = self.title_font.render("CENTRE D'AMÉLIORATIONS & ARBRE DE COMPÉTENCES", True, config.COLOR_UI_ACCENT)
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

        # Onglets / Tabs
        tab_w = 260
        tab_h = 38
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
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + 8))

        draw_tab(tab_tree_rect, "1. Arbre de Compétences", self.active_tab == "skill_tree")
        draw_tab(tab_troops_rect, "2. Troupes (SwarmerBlood)", self.active_tab == "troops")
        draw_tab(tab_bld_rect, "3. Bâtiments (Pykrite)", self.active_tab == "buildings")

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
        back_btn = pygame.Rect(self.screen_width // 2 - 100, self.screen_height - 60, 200, 42)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=6)
        back_txt = self.bold_font.render("RETOUR", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 10))
        buttons["back"] = back_btn

        return buttons

    def _draw_skill_tree_tab(self, surface, buttons, upg_data, points_available):
        nodes = [
            {
                "key": "starting_res_1",
                "name": "Ressources Départ 1",
                "desc": "+100 ressources au départ",
                "cost": 20,
                "parents": [],
                "pos": (250, 200)
            },
            {
                "key": "wood_stockpile_unlocked",
                "name": "Stock de bois",
                "desc": "Dépôt de bois pour ouvriers",
                "cost": 20,
                "parents": [],
                "pos": (640, 200)
            },
            {
                "key": "gold_stockpile_unlocked",
                "name": "Stock d'or",
                "desc": "Dépôt d'or pour ouvriers",
                "cost": 20,
                "parents": [],
                "pos": (1030, 200)
            },
            {
                "key": "archer_unlocked",
                "name": "Débloquer Archer",
                "desc": "Entraîner Archers à la Caserne",
                "cost": 30,
                "parents": ["starting_res_1"],
                "pos": (250, 360)
            },
            {
                "key": "wall_unlocked",
                "name": "Murs en bois",
                "desc": "Construire des murs en bois",
                "cost": 25,
                "parents": ["wood_stockpile_unlocked"],
                "pos": (520, 360)
            },
            {
                "key": "farm_unlocked",
                "name": "Ferme",
                "desc": "Production passive de nourriture",
                "cost": 25,
                "parents": ["wood_stockpile_unlocked"],
                "pos": (760, 360)
            },
            {
                "key": "tower_unlocked",
                "name": "Tour d'archer",
                "desc": "Construire tours de défense",
                "cost": 35,
                "parents": ["archer_unlocked", "wall_unlocked"],
                "pos": (385, 510)
            },
            {
                "key": "townhall_unlocked",
                "name": "Autre Forum",
                "desc": "Construire un autre Forum",
                "cost": 40,
                "parents": ["farm_unlocked", "gold_stockpile_unlocked"],
                "pos": (895, 510)
            }
        ]

        node_map = {n["key"]: n for n in nodes}

        # 1. Draw connecting lines between parents and children
        for n in nodes:
            cx, cy = n["pos"]
            for parent_key in n["parents"]:
                parent = node_map[parent_key]
                px, py = parent["pos"]
                is_parent_unlocked = upg_data.get(parent_key, 0) >= 1
                is_node_unlocked = upg_data.get(n["key"], 0) >= 1

                if is_node_unlocked:
                    line_color = (76, 175, 80)
                elif is_parent_unlocked:
                    line_color = (255, 179, 0)
                else:
                    line_color = (80, 80, 80)

                pygame.draw.line(surface, line_color, (px, py + 40), (cx, cy - 40), 3)

        # 2. Draw node cards
        for n in nodes:
            key = n["key"]
            cx, cy = n["pos"]
            card_w, card_h = 220, 82
            card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)

            is_unlocked = upg_data.get(key, 0) >= 1
            parents_unlocked = all(upg_data.get(p, 0) >= 1 for p in n["parents"])

            if is_unlocked:
                bg_col = (25, 50, 35)
                border_col = (76, 175, 80)
                status_txt = "DÉBLOQUÉ"
                status_col = (100, 255, 100)
            elif parents_unlocked:
                bg_col = config.COLOR_UI_PANEL
                border_col = config.COLOR_UI_ACCENT
                status_txt = f"Coût: {n['cost']} LandShard"
                status_col = config.COLOR_UI_ACCENT
            else:
                bg_col = (30, 32, 38)
                border_col = (70, 70, 75)
                status_txt = "VERROUILLÉ"
                status_col = (120, 120, 120)

            pygame.draw.rect(surface, bg_col, card_rect, border_radius=6)
            pygame.draw.rect(surface, border_col, card_rect, 2, border_radius=6)

            # Title
            t_title = self.bold_font.render(n["name"], True, config.COLOR_UI_TEXT if parents_unlocked or is_unlocked else (140, 140, 140))
            surface.blit(t_title, (cx - t_title.get_width() // 2, cy - 32))

            # Desc
            t_desc = self.small_font.render(n["desc"], True, (180, 180, 180) if parents_unlocked or is_unlocked else (100, 100, 100))
            surface.blit(t_desc, (cx - t_desc.get_width() // 2, cy - 10))

            # Status / Button label
            t_stat = self.bold_font.render(status_txt, True, status_col)
            surface.blit(t_stat, (cx - t_stat.get_width() // 2, cy + 12))

            if parents_unlocked and not is_unlocked:
                buttons[key] = {
                    "rect": card_rect,
                    "type": "LandShard",
                    "cost": n["cost"],
                    "is_tree_unlock": True
                }

    def _draw_troops_tab(self, surface, buttons, upg_data, points):
        available_upgrades = [
            # Worker (Toujours débloqué)
            {"key": "worker_hp_lvl", "unit": "Ouvrier", "name": "PV Ouvrier (+15%)", "cost_base": 10},
            {"key": "worker_speed_lvl", "unit": "Ouvrier", "name": "Vitesse Ouvrier (+10%)", "cost_base": 12},

            # Infantry (Toujours débloqué)
            {"key": "infantry_hp_lvl", "unit": "Soldat CàC", "name": "PV Soldat CàC (+10%)", "cost_base": 12},
            {"key": "infantry_attack_lvl", "unit": "Soldat CàC", "name": "Attaque Soldat CàC (+10%)", "cost_base": 15},
        ]

        # Archer (Uniquement si débloqué)
        if upg_data.get("archer_unlocked"):
            available_upgrades.append({"key": "archer_hp_lvl", "unit": "Archer", "name": "PV Archer (+10%)", "cost_base": 15})
            available_upgrades.append({"key": "archer_attack_lvl", "unit": "Archer", "name": "Attaque Archer (+10%)", "cost_base": 18})

        self._render_upgrade_list(surface, buttons, available_upgrades, "SwarmerBlood", upg_data)

    def _draw_buildings_tab(self, surface, buttons, upg_data, points):
        available_upgrades = [
            # TownHall & Barracks (Débloqués par défaut)
            {"key": "townhall_hp_lvl", "bld": "Forum Base", "name": "PV Forum Principal (+15%)", "cost_base": 15},
            {"key": "barracks_hp_lvl", "bld": "Caserne", "name": "PV Caserne (+15%)", "cost_base": 12},
        ]

        if upg_data.get("wall_unlocked"):
            available_upgrades.append({"key": "wall_hp_lvl", "bld": "Murs en bois", "name": "PV Murs (+20%)", "cost_base": 10})

        if upg_data.get("tower_unlocked"):
            available_upgrades.append({"key": "tower_hp_lvl", "bld": "Tour d'archer", "name": "PV Tour (+15%)", "cost_base": 15})
            available_upgrades.append({"key": "tower_attack_lvl", "bld": "Tour d'archer", "name": "Attaque Tour (+10%)", "cost_base": 20})

        if upg_data.get("farm_unlocked"):
            available_upgrades.append({"key": "farm_hp_lvl", "bld": "Ferme", "name": "PV Ferme (+15%)", "cost_base": 10})

        if upg_data.get("wood_stockpile_unlocked") or upg_data.get("gold_stockpile_unlocked"):
            available_upgrades.append({"key": "stockpile_hp_lvl", "bld": "Stocks", "name": "PV Stocks (+15%)", "cost_base": 10})

        self._render_upgrade_list(surface, buttons, available_upgrades, "Pykrite", upg_data)

    def _render_upgrade_list(self, surface, buttons, upgrades, point_type, upg_data):
        y = 170
        x_left = self.screen_width // 2 - 350
        width = 700

        for upg in upgrades:
            key = upg["key"]
            lvl = upg_data.get(key, 0)
            cost = upg["cost_base"] * (lvl + 1)

            card_rect = pygame.Rect(x_left, y, width, 52)
            pygame.draw.rect(surface, config.COLOR_UI_PANEL, card_rect, border_radius=6)
            pygame.draw.rect(surface, (70, 75, 85), card_rect, 1, border_radius=6)

            # Name & Level
            txt_name = self.bold_font.render(f"{upg['name']}  [Niv. {lvl}]", True, config.COLOR_UI_TEXT)
            surface.blit(txt_name, (x_left + 20, y + 15))

            # Upgrade Button
            btn_rect = pygame.Rect(x_left + width - 180, y + 8, 160, 36)
            pygame.draw.rect(surface, (50, 70, 95), btn_rect, border_radius=4)
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)

            btn_txt = self.font.render(f"+1 (Coût: {cost})", True, config.COLOR_UI_TEXT)
            surface.blit(btn_txt, (btn_rect.x + btn_rect.width // 2 - btn_txt.get_width() // 2, btn_rect.y + 8))

            buttons[key] = {
                "rect": btn_rect,
                "type": point_type,
                "cost_base": upg["cost_base"],
                "is_tree_unlock": False
            }

            y += 62
