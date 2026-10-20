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

        surface.fill((15, 18, 26))

        left_glow = pygame.Surface((self.screen_width // 2, self.screen_height), pygame.SRCALPHA)
        right_glow = pygame.Surface((self.screen_width // 2, self.screen_height), pygame.SRCALPHA)

        for r in range(300, 0, -30):
            alpha = int(18 * (r / 300))
            pygame.draw.circle(left_glow, (30, 136, 229, alpha), (200, self.screen_height // 2), r)
            pygame.draw.circle(right_glow, (216, 27, 96, alpha), (self.screen_width // 2 - 200, self.screen_height // 2), r)

        surface.blit(left_glow, (0, 0))
        surface.blit(right_glow, (self.screen_width // 2, 0))

        for x in range(0, self.screen_width, 80):
            pygame.draw.line(surface, (25, 30, 42), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 80):
            pygame.draw.line(surface, (25, 30, 42), (0, y), (self.screen_width, y), 1)

        banner_rect = pygame.Rect(self.screen_width // 2 - 450, 80, 900, 140)
        pygame.draw.rect(surface, (22, 27, 38, 220), banner_rect, border_radius=12)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, banner_rect, 2, border_radius=12)

        title = self.title_font.render("MEDIEVAL VS ALIEN INSECT", True, (255, 215, 0))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        subtitle = self.subtitle_font.render("Real-Time Strategy Warfare", True, (180, 200, 220))
        surface.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 168))

        btn_width = 380
        btn_height = 55
        start_y = 280
        gap = 20

        start_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y, btn_width, btn_height)
        skill_tree_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + btn_height + gap, btn_width, btn_height)
        ai_info_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 2, btn_width, btn_height)
        quit_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 3, btn_width, btn_height)

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
        draw_button(quit_btn, "QUIT")

        setup_rect = pygame.Rect(self.screen_width // 2 - 420, 580, 840, 210)
        pygame.draw.rect(surface, (24, 30, 42), setup_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 75, 100), setup_rect, 2, border_radius=10)

        setup_title = self.btn_font.render("GAME SETUP & MAP CONFIGURATION", True, config.COLOR_UI_ACCENT)
        surface.blit(setup_title, (self.screen_width // 2 - setup_title.get_width() // 2, setup_rect.y + 12))

        ai_label = self.font.render("Enemy AI Opponents:", True, config.COLOR_UI_TEXT)
        surface.blit(ai_label, (setup_rect.x + 30, setup_rect.y + 58))

        ai_minus_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 52, 40, 35)
        ai_plus_btn = pygame.Rect(setup_rect.x + 370, setup_rect.y + 52, 40, 35)

        draw_button(ai_minus_btn, "-")
        draw_button(ai_plus_btn, "+")

        ai_val_txt = self.btn_font.render(str(selected_ai_count), True, (255, 215, 0))
        surface.blit(ai_val_txt, (setup_rect.x + 322, setup_rect.y + 54))

        diff_label = self.font.render("AI Difficulty:", True, config.COLOR_UI_TEXT)
        surface.blit(diff_label, (setup_rect.x + 30, setup_rect.y + 108))

        diff_minus_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 100, 40, 38)
        diff_plus_btn = pygame.Rect(setup_rect.x + 480, setup_rect.y + 100, 40, 38)
        diff_btn = pygame.Rect(setup_rect.x + 310, setup_rect.y + 100, 160, 38)

        draw_button(diff_minus_btn, "<")
        draw_button(diff_plus_btn, ">")

        diff_val_txt = self.btn_font.render(f"Niveau {selected_difficulty}", True, (255, 215, 0))
        surface.blit(diff_val_txt, (diff_btn.x + diff_btn.width // 2 - diff_val_txt.get_width() // 2, diff_btn.y + 5))

        map_label = self.font.render("Map Advantage:", True, config.COLOR_UI_TEXT)
        surface.blit(map_label, (setup_rect.x + 30, setup_rect.y + 158))

        map_names = {
            1: "Standard (Equilibrée)",
            2: "Désavantageuse (Ressources raréfiées)",
            3: "Très Désavantageuse (Ressources éloignées)"
        }
        map_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 150, 520, 38)
        draw_button(map_btn, f"{map_names.get(selected_map_type, 'Standard')}")

        footer = self.small_font.render("Resolution: 1920x1080 | Alt+Tab Friendly Borderless Fullscreen Mode", True, (120, 140, 160))
        surface.blit(footer, (self.screen_width // 2 - footer.get_width() // 2, self.screen_height - 35))

        return {
            "start": start_btn,
            "skill_tree": skill_tree_btn,
            "ai_info": ai_info_btn,
            "quit": quit_btn,
            "ai_minus": ai_minus_btn,
            "ai_plus": ai_plus_btn,
            "difficulty": diff_btn,
            "diff_minus": diff_minus_btn,
            "diff_plus": diff_plus_btn,
            "map_type": map_btn
        }

    def draw_ai_info_screen(self, surface, scroll_y=0):
        self.ai_info_scroll_y = scroll_y
        surface.fill((15, 18, 26))

        header_rect = pygame.Rect(0, 0, self.screen_width, 70)
        pygame.draw.rect(surface, (22, 27, 38), header_rect)
        pygame.draw.line(surface, config.COLOR_UI_ACCENT, (0, 70), (self.screen_width, 70), 2)

        t_title = self.title_font.render("CIVILISATION INSECTE ALIEN & NIVEAUX D'IA", True, (255, 215, 0))
        surface.blit(t_title, (self.screen_width // 2 - t_title.get_width() // 2, 10))

        viewport_y = 75
        viewport_h = self.screen_height - 150
        viewport_w = min(1100, self.screen_width - 40)
        viewport_x = (self.screen_width - viewport_w) // 2

        from src.ai.ai_tech import AI_DIFFICULTY_LEVELS

        num_lvls = len(AI_DIFFICULTY_LEVELS)

        civ_box = pygame.Rect(10, 10, viewport_w - 20, 150)

        t_civ_head = self.btn_font.render("FONCTIONNEMENT DE LA CIVILISATION INSECTE ALIEN", True, (216, 27, 96))

        civ_desc_lines = [
            "• Économie de Biomasse: Les Insectes aliens récoltent de la biomasse organique pour concevoir leurs structures et muter leurs troupes.",
            "• Conscience Collective (Hive Mind): Spawneurs rapides en essaims. Les unités mutent rapidement depuis la Ruche et le Bassin de Ponte.",
            "• Troupes Alien: Drones (ouvriers polyvalents), Swarmers (combattants au corps-à-corps), Spitters (tireurs d'acide) et Reine (unités offensives).",
            "• Bâtiments Alien: Hive (Ruche centrale), Spawning Pool (Bassin de ponte des troupes) et Spine Crawler (Organisme défensif)."
        ]

        t_lvl_head = self.btn_font.render("DESCRIPTIFS DES NIVEAUX DE DIFFICULTÉ DE L'IA (1 à 15)", True, config.COLOR_UI_ACCENT)

        ai_descriptions = {
            1: "Niveau 1: Revenu x1.1, vagues/80s. Troupes: Drones & Swarmers.",
            2: "Niveau 2: Revenu x1.2, vagues/70s. +5% HP, +5% Atk.",
            3: "Niveau 3: Revenu x1.3, vagues/60s. +10% HP, +10% Atk.",
            4: "Niveau 4: Revenu x1.4, vagues/50s. Débloque Spine Crawler défensifs. +15% HP/Atk.",
            5: "Niveau 5 (Brouillard): Revenu x1.5, vagues/40s. Brouillard actif. +20% HP/Atk.",
            6: "Niveau 6 (Spitters): Revenu x1.6, vagues/32s. Débloque Spitters à distance. +25% HP/Atk.",
            7: "Niveau 7 (Raids Ouvriers): Revenu x1.7, vagues/25s. Raids ciblés sur paysans. +30% HP/Atk.",
            8: "Niveau 8 (Mucus Creep): Revenu x1.8, vagues/20s. Mucus autour des Ruches (+25% Vit/Atk sur Mucus).",
            9: "Niveau 9 (Flanquement): Revenu x2.0, vagues/16s. Attaques multi-angles et replis tactiques.",
            10: "Niveau 10 (Générateurs Biomasse): Revenu x2.2, vagues/13s. Bâtit des Générateurs de Biomasse. +40% HP, +50% Atk.",
            11: "Niveau 11 (Frenzy): Revenu x2.4, vagues/10s. Swarm Frenzy (+25% Vitesse). +45% HP, +60% Atk.",
            12: "Niveau 12 (Moisson Suprême): Revenu x2.6, vagues/8s. Tuer un ennemi donne de la Biomasse. +50% HP, +70% Atk.",
            13: "Niveau 13 (Assaut Ininterrompu): Revenu x2.8, vagues/6s. Agressivité continue massive. +55% HP, +80% Atk.",
            14: "Niveau 14 (La Reine): Revenu x3.0, vagues/5s. Débloque la Reine (transforme toutes ses victimes en Swarmers).",
            15: "Niveau 15 (La Ruche Mère): Revenu x3.5, vagues/4s. Construit une 2nde Hive et débute avec +2 Drones supplémentaires."
        }

        y = 210
        card_h = 120
        content_h = 220 + num_lvls * (card_h + 10) + 40
        canvas = pygame.Surface((viewport_w, content_h))
        canvas.fill((15, 18, 26))

        pygame.draw.rect(canvas, (28, 34, 48), civ_box, border_radius=10)
        pygame.draw.rect(canvas, (216, 27, 96), civ_box, 2, border_radius=10)
        canvas.blit(t_civ_head, (civ_box.x + 20, civ_box.y + 12))
        curr_y = civ_box.y + 45
        for line in civ_desc_lines:
            t_line = self.font.render(line, True, config.COLOR_UI_TEXT)
            canvas.blit(t_line, (civ_box.x + 20, curr_y))
            curr_y += 24
        canvas.blit(t_lvl_head, (15, 175))

        for lvl in range(1, num_lvls + 1):
            data = AI_DIFFICULTY_LEVELS.get(lvl, {})
            card_rect = pygame.Rect(10, y, viewport_w - 20, card_h)

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
            canvas.blit(t_head, (card_rect.x + 15, y + 8))

            mult = data.get("resource_multiplier", 1.0)
            wave_s = data.get("attack_wave_interval", 60)
            m_army = data.get("max_army_size", 10)
            m_work = data.get("max_workers", 5)
            techs = ", ".join(data.get("unlocked_techs", []))
            hp_b = int(data.get("unit_hp_bonus", 0.0) * 100)
            atk_b = int(data.get("unit_atk_bonus", 0.0) * 100)

            desc_text = ai_descriptions.get(lvl, "")
            line1 = f"Description: {desc_text}"
            line2 = f"Revenu: x{mult} | Vagues: {wave_s}s | Max Ouvriers: {m_work} | Armée Max: {m_army} | Techs: [{techs}] | Bonus: HP +{hp_b}%, Atk +{atk_b}%"

            t_l1 = self.small_font.render(line1, True, (230, 240, 255))
            t_l2 = self.small_font.render(line2, True, (170, 190, 210))

            canvas.blit(t_l1, (card_rect.x + 15, y + 42))
            canvas.blit(t_l2, (card_rect.x + 15, y + 74))

            y += card_h + 10

        clamp_scroll = max(0, min(scroll_y, content_h - viewport_h))
        surface.blit(canvas, (viewport_x, viewport_y), pygame.Rect(0, clamp_scroll, viewport_w, viewport_h))

        if content_h > viewport_h:
            bar_w = 10
            bar_x = viewport_x + viewport_w + 8
            pygame.draw.rect(surface, (30, 36, 50), (bar_x, viewport_y, bar_w, viewport_h), border_radius=5)

            thumb_h = max(30, int((viewport_h / content_h) * viewport_h))
            thumb_y = viewport_y + int((clamp_scroll / (content_h - viewport_h)) * (viewport_h - thumb_h))
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, (bar_x, thumb_y, bar_w, thumb_h), border_radius=5)

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
