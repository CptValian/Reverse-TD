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

        # Game Setup Panel (AI, Difficulty & Map Selector)
        setup_rect = pygame.Rect(self.screen_width // 2 - 400, 580, 800, 210)
        pygame.draw.rect(surface, (24, 30, 42), setup_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 75, 100), setup_rect, 2, border_radius=10)

        setup_title = self.btn_font.render("CONFIGUATION DE LA PARTIE", True, config.COLOR_UI_ACCENT)
        surface.blit(setup_title, (self.screen_width // 2 - setup_title.get_width() // 2, setup_rect.y + 12))

        # AI Count Selector Buttons
        ai_label = self.font.render("Nombre d'IA Ennemies:", True, config.COLOR_UI_TEXT)
        surface.blit(ai_label, (setup_rect.x + 30, setup_rect.y + 55))

        ai_minus_btn = pygame.Rect(setup_rect.x + 280, setup_rect.y + 50, 40, 35)
        ai_plus_btn = pygame.Rect(setup_rect.x + 390, setup_rect.y + 50, 40, 35)

        draw_button(ai_minus_btn, "-")
        draw_button(ai_plus_btn, "+")

        ai_val_txt = self.btn_font.render(str(selected_ai_count), True, (255, 215, 0))
        surface.blit(ai_val_txt, (setup_rect.x + 342, setup_rect.y + 52))

        # Difficulty Selector Cycle Button
        diff_label = self.font.render("Niveau de l'IA:", True, config.COLOR_UI_TEXT)
        surface.blit(diff_label, (setup_rect.x + 30, setup_rect.y + 102))

        diff_btn = pygame.Rect(setup_rect.x + 280, setup_rect.y + 95, 280, 38)
        draw_button(diff_btn, f"Niveau {selected_difficulty}")

        # Map Selector Cycle Button
        map_label = self.font.render("Terrain de la Carte:", True, config.COLOR_UI_TEXT)
        surface.blit(map_label, (setup_rect.x + 30, setup_rect.y + 152))

        map_names = {1: "1: Équilibrée", 2: "2: Désavantageuse", 3: "3: Très Désavantageuse"}
        map_btn = pygame.Rect(setup_rect.x + 280, setup_rect.y + 145, 280, 38)
        draw_button(map_btn, map_names.get(selected_map_type, "1: Équilibrée"))

        # Footer info
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
            "map_type": map_btn
        }

    def draw_ai_info_screen(self, surface):
        surface.fill((18, 22, 32))

        # Title
        t_title = self.title_font.render("CIVILISATION INSECTE ALIEN & NIVEAUX IA", True, (255, 215, 0))
        surface.blit(t_title, (self.screen_width // 2 - t_title.get_width() // 2, 20))

        # Alien Civ Description Panel
        civ_rect = pygame.Rect(self.screen_width // 2 - 550, 85, 1100, 110)
        pygame.draw.rect(surface, (30, 20, 40), civ_rect, border_radius=8)
        pygame.draw.rect(surface, (216, 27, 96), civ_rect, 2, border_radius=8)

        c_title = self.btn_font.render("Fonctionnement de la Civilisation Insecte Alien", True, (216, 27, 96))
        surface.blit(c_title, (civ_rect.x + 15, civ_rect.y + 10))

        c_desc1 = self.small_font.render("Organismes prédateurs Voraces. L'économie alien repose sur la Biomasse récoltée ou générée par les organismes.", True, (240, 240, 240))
        c_desc2 = self.small_font.render("Éclosion rapide d'essaims mortels depuis la Ruche et les Bassins de Spécimens. Stratégie basée sur le nombre et l'agressivité.", True, (200, 180, 210))
        surface.blit(c_desc1, (civ_rect.x + 15, civ_rect.y + 45))
        surface.blit(c_desc2, (civ_rect.x + 15, civ_rect.y + 72))

        # Units & Buildings Descriptions Panel
        tech_rect = pygame.Rect(self.screen_width // 2 - 550, 205, 1100, 180)
        pygame.draw.rect(surface, (25, 30, 45), tech_rect, border_radius=8)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, tech_rect, 1, border_radius=8)

        t_title_sub = self.btn_font.render("Unités & Bâtiments Alien", True, config.COLOR_UI_ACCENT)
        surface.blit(t_title_sub, (tech_rect.x + 15, tech_rect.y + 10))

        lines = [
            "• Drone (Ouvrier): Insecte collecteur de biomasse et organisme bâtisseur des structures organiques.",
            "• Swarmer (Mêlée): Organisme d'attaque rapide doté de faux tranchantes pour assaillir les positions ennemies.",
            "• Spitter (Distance): Artillerie vivante propulsant des gerbes d'acide corrosif à longue portée.",
            "• Ruche (Hive): Cœur biologique de la colonie alien, produit les Drones de collecte.",
            "• Bassin de Spécimen (Spawning Pool): Bâtiment de mutation génétique entraînant Swarmers et Spitters.",
            "• Spine Crawler (Défense): Tourelle organique ancrée projetant d'épais épieux d'os acérés."
        ]
        ly = tech_rect.y + 42
        for line in lines:
            t_line = self.small_font.render(line, True, (220, 230, 240))
            surface.blit(t_line, (tech_rect.x + 15, ly))
            ly += 21

        # Difficulty Levels List
        from src.ai.ai_tech import AI_DIFFICULTY_LEVELS

        y = 398
        for lvl, data in AI_DIFFICULTY_LEVELS.items():
            card_rect = pygame.Rect(self.screen_width // 2 - 550, y, 1100, 92)
            pygame.draw.rect(surface, config.COLOR_UI_PANEL, card_rect, border_radius=8)
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, card_rect, 1, border_radius=8)

            # Lvl header
            header_txt = f"NIVEAU IA {lvl}"
            t_head = self.btn_font.render(header_txt, True, (255, 215, 0))
            surface.blit(t_head, (card_rect.x + 15, y + 8))

            # Details
            mult = data["resource_multiplier"]
            wave_s = data["attack_wave_interval"]
            m_army = data["max_army_size"]
            m_work = data["max_workers"]
            techs = ", ".join(data["unlocked_techs"])
            hp_b = int(data["unit_hp_bonus"] * 100)
            atk_b = int(data["unit_atk_bonus"] * 100)
            fow = "OUI (Brouillard activé)" if lvl > 4 else "NON"

            line1 = f"Multiplicateur Ressources: x{mult} | Intervalle Vagues: {wave_s}s | Max Ouvriers: {m_work} | Max Armée: {m_army}"
            line2 = f"Technologies: [{techs}] | Brouillard de Guerre: {fow} | Bonus PV: +{hp_b}% | Bonus ATK: +{atk_b}%"

            t_l1 = self.small_font.render(line1, True, config.COLOR_UI_TEXT)
            t_l2 = self.small_font.render(line2, True, (180, 200, 220))

            surface.blit(t_l1, (card_rect.x + 15, y + 38))
            surface.blit(t_l2, (card_rect.x + 15, y + 62))

            y += 98

        # Back Button
        back_btn = pygame.Rect(self.screen_width // 2 - 120, self.screen_height - 60, 240, 45)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=6)
        back_txt = self.btn_font.render("RETOUR MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 8))

        return {"back": back_btn}
