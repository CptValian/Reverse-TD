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

        # Difficulty Selector Cycle Button
        diff_label = self.font.render("AI Difficulty:", True, config.COLOR_UI_TEXT)
        surface.blit(diff_label, (setup_rect.x + 30, setup_rect.y + 108))

        diff_btn = pygame.Rect(setup_rect.x + 260, setup_rect.y + 100, 260, 38)
        draw_button(diff_btn, f"Level {selected_difficulty}")

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

        # Section 1: Fonctionnement de la Civilisation Insecte Alien
        civ_box = pygame.Rect(self.screen_width // 2 - 500, 80, 1000, 140)
        pygame.draw.rect(surface, (28, 34, 48), civ_box, border_radius=8)
        pygame.draw.rect(surface, (216, 27, 96), civ_box, 2, border_radius=8)

        t_civ_head = self.btn_font.render("FONCTIONNEMENT DE LA CIVILISATION INSECTE ALIEN", True, (216, 27, 96))
        surface.blit(t_civ_head, (civ_box.x + 15, civ_box.y + 10))

        civ_desc_lines = [
            "• Économie de Biomasse: Les Insectes aliens récoltent de la biomasse organique pour concevoir leurs structures et muter leurs troupes.",
            "• Conscience Collective (Hive Mind): Spawneurs rapides en essaims. Les unités mutent rapidement depuis la Ruche et le Bassin de Ponte.",
            "• Troupes Alien: Drones (ouvriers polyvalents), Swarmers (combattants au corps-à-corps rapides) et Spitters (tireurs d'acide à distance).",
            "• Bâtiments Alien: Hive (Ruche centrale), Spawning Pool (Bassin de ponte des troupes) et Spine Crawler (Organisme défensif)."
        ]
        curr_y = civ_box.y + 42
        for line in civ_desc_lines:
            t_line = self.small_font.render(line, True, config.COLOR_UI_TEXT)
            surface.blit(t_line, (civ_box.x + 15, curr_y))
            curr_y += 22

        # Subtitle for Levels
        t_lvl_head = self.btn_font.render("DESCRIPTIFS DES NIVEAUX DE DIFFICULTÉ DE L'IA", True, config.COLOR_UI_ACCENT)
        surface.blit(t_lvl_head, (self.screen_width // 2 - 500, 230))

        from src.ai.ai_tech import AI_DIFFICULTY_LEVELS

        ai_descriptions = {
            1: "Niveau 1 (Pasif): Revenu x1.0, vagues d'attaque toutes les 120s (max 8 unités). Troupes: Drones & Swarmers.",
            2: "Niveau 2 (Facile): Revenu x1.2, vagues toutes les 90s (max 12 unités). Débloque les Spitters à distance. +5% HP/Atk.",
            3: "Niveau 3 (Moyen): Revenu x1.5, vagues toutes les 70s (max 18 unités). Armées combinées Swarmer/Spitter. +10% HP/Atk.",
            4: "Niveau 4 (Difficile): Revenu x1.8, vagues toutes les 50s (max 25 unités). Construit des Spine Crawlers. +20% HP, +15% Atk.",
            5: "Niveau 5 (Expert - Brouillard de Guerre): Revenu x2.2, vagues toutes les 35s (max 35 unités). Brouillard actif (Tour d'observation utile). +35% HP, +25% Atk.",
            6: "Niveau 6 (Cauchemar - Brouillard de Guerre): Revenu x2.8, vagues dévastatrices toutes les 25s (max 50 unités). Brouillard actif. +50% HP, +40% Atk."
        }

        y = 265
        for lvl, data in AI_DIFFICULTY_LEVELS.items():
            card_rect = pygame.Rect(self.screen_width // 2 - 500, y, 1000, 95)
            pygame.draw.rect(surface, config.COLOR_UI_PANEL, card_rect, border_radius=8)
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT if lvl <= 4 else (255, 100, 100), card_rect, 1, border_radius=8)

            header_txt = f"IA NIVEAU {lvl}" + (" [BROUILLARD DE GUERRE ACTIF]" if lvl > 4 else "")
            t_head = self.btn_font.render(header_txt, True, (255, 215, 0) if lvl <= 4 else (255, 120, 120))
            surface.blit(t_head, (card_rect.x + 15, y + 8))

            mult = data["resource_multiplier"]
            wave_s = data["attack_wave_interval"]
            m_army = data["max_army_size"]
            m_work = data["max_workers"]
            techs = ", ".join(data["unlocked_techs"])
            hp_b = int(data["unit_hp_bonus"] * 100)
            atk_b = int(data["unit_atk_bonus"] * 100)

            desc_text = ai_descriptions.get(lvl, "")
            line1 = f"Description: {desc_text}"
            line2 = f"Multiplicateur: x{mult} | Vague: {wave_s}s | Max Ouvriers: {m_work} | Armée Max: {m_army} | Techs: [{techs}] | Bonus: HP +{hp_b}%, Atk +{atk_b}%"

            t_l1 = self.small_font.render(line1, True, (220, 230, 242))
            t_l2 = self.small_font.render(line2, True, (160, 180, 200))

            surface.blit(t_l1, (card_rect.x + 15, y + 42))
            surface.blit(t_l2, (card_rect.x + 15, y + 66))

            y += 102

        # Back Button
        back_btn = pygame.Rect(self.screen_width // 2 - 120, self.screen_height - 60, 240, 45)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=6)
        back_txt = self.btn_font.render("RETOUR AU MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 8))

        return {"back": back_btn}
