import pygame
import math
import config

class Menu:
    def __init__(self, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_font = pygame.font.SysFont("Trebuchet MS", 54, bold=True)
        self.subtitle_font = pygame.font.SysFont("Trebuchet MS", 24, italic=True)
        self.btn_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font = pygame.font.SysFont("Segoe UI", 20)
        self.small_font = pygame.font.SysFont("Segoe UI", 16)
        self.anim_time = 0.0
        self.ai_info_scroll_y = 0

    def draw_main_menu(self, surface, selected_ai_count=1, selected_difficulty=1, selected_map_type=1):
        self.anim_time += 0.016

        # Atmospheric Background Gradient & Art Elements
        surface.fill((15, 18, 26))

        # Medieval vs Insect Alien split ambient glows
        left_glow = pygame.Surface((self.screen_width // 2, self.screen_height), pygame.SRCALPHA)
        right_glow = pygame.Surface((self.screen_width // 2, self.screen_height), pygame.SRCALPHA)

        for r in range(300, 0, -30):
            alpha = int(18 * (r / 300))
            pygame.draw.circle(left_glow, (30, 136, 229, alpha), (200, self.screen_height // 2), r)
            pygame.draw.circle(right_glow, (216, 27, 96, alpha), (self.screen_width // 2 - 200, self.screen_height // 2), r)

        surface.blit(left_glow, (0, 0))
        surface.blit(right_glow, (self.screen_width // 2, 0))

        # Subtle decorative grid pattern
        for x in range(0, self.screen_width, 80):
            pygame.draw.line(surface, (25, 30, 42), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 80):
            pygame.draw.line(surface, (25, 30, 42), (0, y), (self.screen_width, y), 1)

        # Title Card Banner
        banner_rect = pygame.Rect(self.screen_width // 2 - 450, 80, 900, 140)
        pygame.draw.rect(surface, (22, 27, 38, 220), banner_rect, border_radius=12)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, banner_rect, 2, border_radius=12)

        # Main Title & Subtitle in English
        title = self.title_font.render("MEDIEVAL VS ALIEN INSECT", True, (255, 215, 0))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        subtitle = self.subtitle_font.render("Real-Time Strategy Warfare", True, (180, 200, 220))
        surface.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 168))

        # Main Navigation Buttons
        btn_width = 380
        btn_height = 48
        start_y = 265
        gap = 14

        start_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y, btn_width, btn_height)
        skill_tree_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + btn_height + gap, btn_width, btn_height)
        ai_info_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 2, btn_width, btn_height)
        options_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 3, btn_width, btn_height)
        quit_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 4, btn_width, btn_height)

        def draw_button(rect, text, is_primary=False):
            mouse_p = pygame.mouse.get_pos()
            hovered = rect.collidepoint(mouse_p)
            bg_col = (45, 55, 75) if hovered else ((32, 40, 56) if not is_primary else (40, 80, 120))
            border_col = (255, 215, 0) if hovered else (config.COLOR_UI_ACCENT if is_primary else (90, 110, 140))

            pygame.draw.rect(surface, bg_col, rect, border_radius=8)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)

            t_surf = self.btn_font.render(text, True, (255, 255, 255) if hovered else config.COLOR_UI_TEXT)
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + rect.height // 2 - t_surf.get_height() // 2))

        draw_button(start_btn, "LAUNCH GAME", is_primary=True)
        draw_button(skill_tree_btn, "SKILL TREE & UPGRADES")
        draw_button(ai_info_btn, "AI TECHS & INFO")
        draw_button(options_btn, "OPTIONS")
        draw_button(quit_btn, "QUIT")

        # Game Setup Panel (AI, Difficulty, Map Type Selector)
        setup_rect = pygame.Rect(self.screen_width // 2 - 420, 580, 840, 210)
        pygame.draw.rect(surface, (24, 30, 42), setup_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 75, 100), setup_rect, 2, border_radius=10)

        setup_title = self.btn_font.render("GAME SETUP & MAP CONFIGURATION", True, config.COLOR_UI_ACCENT)
        surface.blit(setup_title, (self.screen_width // 2 - setup_title.get_width() // 2, setup_rect.y + 12))

        # AI Count Selector Buttons
        ai_label = self.font.render("Enemy AI Opponents:", True, config.COLOR_UI_TEXT)
        surface.blit(ai_label, (setup_rect.x + 30, setup_rect.y + 58))

        ai_minus_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 52, 40, 35)
        ai_plus_btn = pygame.Rect(setup_rect.x + 370, setup_rect.y + 52, 40, 35)

        draw_button(ai_minus_btn, "-")
        draw_button(ai_plus_btn, "+")

        ai_val_txt = self.btn_font.render(str(selected_ai_count), True, (255, 215, 0))
        surface.blit(ai_val_txt, (setup_rect.x + 322, setup_rect.y + 54))

        # Difficulty Selector Buttons (Left < and Right > arrows)
        diff_label = self.font.render("AI Difficulty:", True, config.COLOR_UI_TEXT)
        surface.blit(diff_label, (setup_rect.x + 30, setup_rect.y + 108))

        diff_minus_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 100, 40, 38)
        diff_plus_btn = pygame.Rect(setup_rect.x + 480, setup_rect.y + 100, 40, 38)
        diff_btn = pygame.Rect(setup_rect.x + 310, setup_rect.y + 100, 160, 38)

        draw_button(diff_minus_btn, "<")
        draw_button(diff_plus_btn, ">")

        diff_val_txt = self.btn_font.render(f"Niveau {selected_difficulty}", True, (255, 215, 0))
        surface.blit(diff_val_txt, (diff_btn.x + diff_btn.width // 2 - diff_val_txt.get_width() // 2, diff_btn.y + 5))

        # Map Selector Cycle Button
        map_label = self.font.render("Map Advantage:", True, config.COLOR_UI_TEXT)
        surface.blit(map_label, (setup_rect.x + 30, setup_rect.y + 158))

        map_names = {
            1: "Standard (Equilibrée)",
            2: "Désavantageuse (Ressources raréfiées)",
            3: "Très Désavantageuse (Ressources éloignées)"
        }
        map_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 150, 520, 38)
        draw_button(map_btn, f"{map_names.get(selected_map_type, 'Standard')}")

        # Footer info
        footer = self.small_font.render("Resolution: 1920x1080 | Alt+Tab Friendly Borderless Fullscreen Mode", True, (120, 140, 160))
        surface.blit(footer, (self.screen_width // 2 - footer.get_width() // 2, self.screen_height - 35))

        return {
            "start": start_btn,
            "skill_tree": skill_tree_btn,
            "ai_info": ai_info_btn,
            "options": options_btn,
            "quit": quit_btn,
            "ai_minus": ai_minus_btn,
            "ai_plus": ai_plus_btn,
            "difficulty": diff_btn,
            "diff_minus": diff_minus_btn,
            "diff_plus": diff_plus_btn,
            "map_type": map_btn
        }

    def draw_options_menu(self, surface, save_manager):
        surface.fill((15, 18, 26))

        # Header Title
        header_rect = pygame.Rect(0, 0, self.screen_width, 80)
        pygame.draw.rect(surface, (22, 27, 38), header_rect)
        pygame.draw.line(surface, config.COLOR_UI_ACCENT, (0, 80), (self.screen_width, 80), 2)

        t_title = self.title_font.render("OPTIONS DU JEU", True, (255, 215, 0))
        surface.blit(t_title, (self.screen_width // 2 - t_title.get_width() // 2, 12))

        # Panel Box
        panel_w, panel_h = 800, 450
        panel_rect = pygame.Rect((self.screen_width - panel_w) // 2, 180, panel_w, panel_h)
        pygame.draw.rect(surface, (24, 30, 42), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 75, 100), panel_rect, 2, border_radius=12)

        # Checkbox for Fog of War Toggle
        is_fog_disabled = save_manager.get_setting("disable_fog_of_war", False)

        box_size = 32
        cb_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 80, box_size, box_size)
        pygame.draw.rect(surface, (40, 50, 70), cb_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 0) if is_fog_disabled else (100, 120, 150), cb_rect, 2, border_radius=6)

        if is_fog_disabled:
            # Draw Checkmark
            pts = [(cb_rect.x + 6, cb_rect.y + 16), (cb_rect.x + 13, cb_rect.y + 24), (cb_rect.x + 26, cb_rect.y + 8)]
            pygame.draw.lines(surface, (0, 255, 128), False, pts, 4)

        t_cb_label = self.btn_font.render("Dissiper le brouillard de guerre pour toutes les parties", True, config.COLOR_UI_TEXT)
        surface.blit(t_cb_label, (cb_rect.x + box_size + 20, cb_rect.y + 2))

        t_cb_desc = self.font.render("(Dévoile l'intégralité de la carte et supprime la brume sombre sur le champ de bataille)", True, (160, 180, 200))
        surface.blit(t_cb_desc, (cb_rect.x + box_size + 20, cb_rect.y + 38))

        # Back Button
        back_btn = pygame.Rect(self.screen_width // 2 - 140, self.screen_height - 120, 280, 50)
        mouse_p = pygame.mouse.get_pos()
        hovered = back_btn.collidepoint(mouse_p)
        pygame.draw.rect(surface, (45, 55, 75) if hovered else config.COLOR_UI_PANEL, back_btn, border_radius=8)
        pygame.draw.rect(surface, (255, 215, 0) if hovered else config.COLOR_UI_ACCENT, back_btn, 2, border_radius=8)

        back_txt = self.btn_font.render("RETOUR AU MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 10))

        return {
            "back": back_btn,
            "fog_checkbox": cb_rect
        }

    def draw_ai_info_screen(self, surface, scroll_y=0):
        self.ai_info_scroll_y = scroll_y
        surface.fill((15, 18, 26))

        # Title (Fixed Header)
        header_rect = pygame.Rect(0, 0, self.screen_width, 70)
        pygame.draw.rect(surface, (22, 27, 38), header_rect)
        pygame.draw.line(surface, config.COLOR_UI_ACCENT, (0, 70), (self.screen_width, 70), 2)

        t_title = self.title_font.render("CIVILISATION INSECTE ALIEN & NIVEAUX D'IA", True, (255, 215, 0))
        surface.blit(t_title, (self.screen_width // 2 - t_title.get_width() // 2, 10))

        # Scrollable Viewport Surface
        viewport_y = 75
        viewport_h = self.screen_height - 150
        viewport_w = min(1100, self.screen_width - 40)
        viewport_x = (self.screen_width - viewport_w) // 2

        # Create virtual canvas surface
        from src.ai.ai_tech import AI_DIFFICULTY_LEVELS

        num_lvls = len(AI_DIFFICULTY_LEVELS)
        content_h = 240 + num_lvls * 115 + 40
        canvas = pygame.Surface((viewport_w, content_h))
        canvas.fill((15, 18, 26))

        civ_desc_lines = [
            "• Économie de Biomasse: Les Insectes aliens récoltent de la biomasse organique pour concevoir leurs structures et muter leurs troupes.",
            "• Conscience Collective (Hive Mind): Prise de décision stratégique en temps réel et intelligence adaptative au sommet pour toutes les IA.",
            "• Troupes Alien: Drones (ouvriers polyvalents), Swarmers (combattants au corps-à-corps rapides), Spitters (tireurs d'acide) et la Reine Alien (tireuse de spores qui transforme ses victimes tuées en Swarmers).",
            "• Bâtiments & Technologies: Hive (Ruche centrale), Spawning Pool (Bassin de ponte), Spine Crawler (Défense), Biomass Generator (Revenu passive) et Evolution Chamber (Améliorations génétiques)."
        ]

        def wrap_text(text, font, max_w):
            words = text.split(" ")
            lines = []
            cur = []
            for word in words:
                test_l = " ".join(cur + [word])
                if font.size(test_l)[0] <= max_w:
                    cur.append(word)
                else:
                    if cur:
                        lines.append(" ".join(cur))
                    cur = [word]
            if cur:
                lines.append(" ".join(cur))
            return lines

        wrapped_desc_lines = []
        max_line_w = viewport_w - 60
        for raw_line in civ_desc_lines:
            wrapped_desc_lines.extend(wrap_text(raw_line, self.font, max_line_w))

        civ_box_h = 50 + len(wrapped_desc_lines) * 24 + 10
        civ_box = pygame.Rect(10, 10, viewport_w - 20, civ_box_h)

        ai_head_y = civ_box.y + civ_box_h + 15
        t_lvl_head = self.btn_font.render("DESCRIPTIFS DES NIVEAUX DE DIFFICULTÉ DE L'IA (1 à 18)", True, config.COLOR_UI_ACCENT)

        ai_descriptions = {
            1: "Niveau 1: Revenu x1.0. Troupes: Drones & Swarmers. Moteur de réflexion stratégique complet.",
            2: "Niveau 2: Revenu x1.1. Débloque +1 Swarmer au début de la partie.",
            3: "Niveau 3: Revenu x1.2. Débloque +1 Drone au début de la partie.",
            4: "Niveau 4: Revenu x1.3. Débloque les Spine Crawlers défensifs. +15% HP/Atk.",
            5: "Niveau 5 (Biomasse Depot): Revenu x1.4. Bâtit des Stockpiles de biomasse.",
            6: "Niveau 6 (Spitters): Revenu x1.5. Débloque les Spitters à distance.",
            7: "Niveau 7 (Enrage Ruche): Revenu x1.6. Pouvoir activable Ruche (60s CD): +10% Speed/Atk pendant 5s.",
            8: "Niveau 8 (Mucus Creep): Revenu x1.7. Mucus autour des Ruches (+25% Vitesse/Attaque sur Mucus).",
            9: "Niveau 9 (Double Swarmer): Revenu x1.85. La production d'un Swarmer en produit 2.",
            10: "Niveau 10 (Générateurs Biomasse): Revenu x2.0. Bâtit des Générateurs de Biomasse.",
            11: "Niveau 11 (Frenzy): Revenu x2.2. Swarm Frenzy (+25% Vitesse). +45% HP, +60% Atk.",
            12: "Niveau 12 (Moisson Suprême): Revenu x2.5. Tuer un ennemi rapporte de la Biomasse.",
            13: "Niveau 13 (Enrage Amélioré): Revenu x2.8. Améliore le pouvoir de la Ruche à +20% Speed/Atk.",
            14: "Niveau 14 (Reine Alien): Revenu x3.2. Débloque la Reine (transforme victimes en Swarmers).",
            15: "Niveau 15 (Seconde Ruche & Drones): Revenu x3.6. Bâtit une 2nde Ruche & +2 Drones de départ.",
            16: "Niveau 16 (Gisements Doublés): Revenu x4.0. Gisements de biomasse avec 2x plus de biomasse.",
            17: "Niveau 17 (Essaim de Drones): Revenu x4.5. +4 Drones supplémentaires au début.",
            18: "Niveau 18 (Bâtiment d'Évolution): Revenu x5.0. Bâtiment d'évolution (+10% HP, -10% prix Swarmer, +5% prod biomasse)."
        }

        # Calculate card heights and dynamic lines
        cards_data = []
        card_w = viewport_w - 20
        text_max_w = card_w - 30

        for lvl in range(1, num_lvls + 1):
            data = AI_DIFFICULTY_LEVELS.get(lvl, {})
            mult = data.get("resource_multiplier", 1.0)
            m_army = data.get("max_army_size", 10)
            m_work = data.get("max_workers", 5)
            techs = ", ".join(data.get("unlocked_techs", []))
            hp_b = int(data.get("unit_hp_bonus", 0.0) * 100)
            atk_b = int(data.get("unit_atk_bonus", 0.0) * 100)

            desc_text = ai_descriptions.get(lvl, "")
            l1_wrapped = wrap_text(f"Description: {desc_text}", self.small_font, text_max_w)
            l2_wrapped = wrap_text(f"Revenu: x{mult} | Max Ouvriers: {m_work} | Armée Max: {m_army} | Techs: [{techs}] | Bonus: HP +{hp_b}%, Atk +{atk_b}%", self.small_font, text_max_w)

            total_text_lines = len(l1_wrapped) + len(l2_wrapped)
            c_height = 36 + total_text_lines * 20 + 12
            cards_data.append({
                "lvl": lvl,
                "data": data,
                "height": c_height,
                "l1_lines": l1_wrapped,
                "l2_lines": l2_wrapped
            })

        total_cards_h = sum([c["height"] + 10 for c in cards_data])
        content_h = ai_head_y + 35 + total_cards_h + 40

        canvas = pygame.Surface((viewport_w, content_h))
        canvas.fill((15, 18, 26))

        # Redraw top section on resized canvas
        pygame.draw.rect(canvas, (28, 34, 48), civ_box, border_radius=10)
        pygame.draw.rect(canvas, (216, 27, 96), civ_box, 2, border_radius=10)
        t_civ_head = self.btn_font.render("FONCTIONNEMENT DE LA CIVILISATION INSECTE ALIEN", True, (216, 27, 96))
        canvas.blit(t_civ_head, (civ_box.x + 20, civ_box.y + 12))

        curr_y = civ_box.y + 45
        for line in wrapped_desc_lines:
            t_line = self.font.render(line, True, config.COLOR_UI_TEXT)
            canvas.blit(t_line, (civ_box.x + 20, curr_y))
            curr_y += 24

        canvas.blit(t_lvl_head, (15, ai_head_y))

        card_y = ai_head_y + 35
        for c in cards_data:
            lvl = c["lvl"]
            data = c["data"]
            card_h = c["height"]
            card_rect = pygame.Rect(10, card_y, viewport_w - 20, card_h)

            is_extreme = lvl >= 8
            is_fog = lvl >= 5
            bg_col = (40, 24, 32) if is_extreme else config.COLOR_UI_PANEL
            border_col = (255, 60, 60) if is_extreme else (config.COLOR_UI_ACCENT if not is_fog else (255, 140, 0))

            pygame.draw.rect(canvas, bg_col, card_rect, border_radius=8)
            pygame.draw.rect(canvas, border_col, card_rect, 1, border_radius=8)

            header_txt = f"IA NIVEAU {lvl}"
            if is_extreme:
                header_txt += " [CAPACITÉ SPÉCIALE ACTIVE]"
            elif is_fog:
                header_txt += " [BROUILLARD DE GUERRE ACTIF]"

            t_head = self.btn_font.render(header_txt, True, (255, 215, 0) if not is_extreme else (255, 100, 100))
            canvas.blit(t_head, (card_rect.x + 15, card_y + 8))

            text_y = card_y + 36
            for line in c["l1_lines"]:
                t_l = self.small_font.render(line, True, (230, 240, 255))
                canvas.blit(t_l, (card_rect.x + 15, text_y))
                text_y += 20

            for line in c["l2_lines"]:
                t_l = self.small_font.render(line, True, (170, 190, 210))
                canvas.blit(t_l, (card_rect.x + 15, text_y))
                text_y += 20

            card_y += card_h + 10

        # Blit scrolled portion onto main screen
        clamp_scroll = max(0, min(scroll_y, content_h - viewport_h))
        surface.blit(canvas, (viewport_x, viewport_y), pygame.Rect(0, clamp_scroll, viewport_w, viewport_h))

        # Visual Scrollbar Track & Thumb
        if content_h > viewport_h:
            bar_w = 10
            bar_x = viewport_x + viewport_w + 8
            pygame.draw.rect(surface, (30, 36, 50), (bar_x, viewport_y, bar_w, viewport_h), border_radius=5)

            thumb_h = max(30, int((viewport_h / content_h) * viewport_h))
            thumb_y = viewport_y + int((clamp_scroll / (content_h - viewport_h)) * (viewport_h - thumb_h))
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, (bar_x, thumb_y, bar_w, thumb_h), border_radius=5)

        # Fixed Footer Panel & Back Button
        footer_rect = pygame.Rect(0, self.screen_height - 70, self.screen_width, 70)
        pygame.draw.rect(surface, (22, 27, 38), footer_rect)
        pygame.draw.line(surface, (50, 60, 80), (0, self.screen_height - 70), (self.screen_width, self.screen_height - 70), 1)

        back_btn = pygame.Rect(self.screen_width // 2 - 140, self.screen_height - 58, 280, 46)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=8)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=8)
        back_txt = self.btn_font.render("RETOUR AU MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 8))

        return {
            "back": back_btn,
            "max_scroll": content_h - viewport_h,
            "current_scroll": clamp_scroll
        }
