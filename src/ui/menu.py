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
        self.bold_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
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
        btn_height = 46
        start_y = 250
        gap = 12

        h_v_a_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y, btn_width, btn_height)
        a_v_h_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap), btn_width, btn_height)
        iacia_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 2, btn_width, btn_height)
        ai_info_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 3, btn_width, btn_height)
        options_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 4, btn_width, btn_height)
        quit_btn = pygame.Rect(self.screen_width // 2 - btn_width // 2, start_y + (btn_height + gap) * 5, btn_width, btn_height)

        def draw_button(rect, text, is_primary=False, is_alien=False):
            mouse_p = pygame.mouse.get_pos()
            hovered = rect.collidepoint(mouse_p)
            bg_col = (45, 55, 75) if hovered else ((32, 40, 56) if not is_primary else ((120, 30, 70) if is_alien else (40, 80, 120)))
            border_col = (255, 215, 0) if hovered else ((216, 27, 96) if is_alien else (config.COLOR_UI_ACCENT if is_primary else (90, 110, 140)))

            pygame.draw.rect(surface, bg_col, rect, border_radius=8)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)

            t_surf = self.btn_font.render(text, True, (255, 255, 255) if hovered else config.COLOR_UI_TEXT)
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + rect.height // 2 - t_surf.get_height() // 2))

        draw_button(h_v_a_btn, "Human vs Alien", is_primary=True)
        draw_button(a_v_h_btn, "Alien vs Human", is_primary=True, is_alien=True)
        draw_button(iacia_btn, "SPECTATOR MODE (AI vs AI)")
        draw_button(ai_info_btn, "AI TECHS & INFO")
        draw_button(options_btn, "OPTIONS")
        draw_button(quit_btn, "QUIT GAME")

        # Footer info
        footer = self.small_font.render("Resolution: 1920x1080 | Alt+Tab Friendly Borderless Fullscreen Mode", True, (120, 140, 160))
        surface.blit(footer, (self.screen_width // 2 - footer.get_width() // 2, self.screen_height - 35))

        return {
            "h_v_a": h_v_a_btn,
            "a_v_h": a_v_h_btn,
            "iacia": iacia_btn,
            "ai_info": ai_info_btn,
            "options": options_btn,
            "quit": quit_btn
        }

    def draw_game_setup_menu(self, surface, selected_ai_count=1, selected_difficulty=1, selected_map_type=1):
        surface.fill((15, 18, 26))

        # Title Card Banner
        banner_rect = pygame.Rect(self.screen_width // 2 - 450, 60, 900, 100)
        pygame.draw.rect(surface, (22, 27, 38, 220), banner_rect, border_radius=12)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, banner_rect, 2, border_radius=12)

        title = self.title_font.render("GAME SETUP & MATCH CONFIGURATION", True, (255, 215, 0))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 85))

        def draw_button(rect, text, is_primary=False):
            mouse_p = pygame.mouse.get_pos()
            hovered = rect.collidepoint(mouse_p)
            bg_col = (45, 55, 75) if hovered else ((32, 40, 56) if not is_primary else (40, 120, 60))
            border_col = (255, 215, 0) if hovered else ((0, 255, 128) if is_primary else (90, 110, 140))

            pygame.draw.rect(surface, bg_col, rect, border_radius=8)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)

            t_surf = self.btn_font.render(text, True, (255, 255, 255) if hovered else config.COLOR_UI_TEXT)
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + rect.height // 2 - t_surf.get_height() // 2))

        # Game Setup Panel Box
        setup_rect = pygame.Rect(self.screen_width // 2 - 420, 200, 840, 320)
        pygame.draw.rect(surface, (24, 30, 42), setup_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 75, 100), setup_rect, 2, border_radius=12)

        # AI Count Selector Buttons
        ai_label = self.font.render("Enemy AI Opponents:", True, config.COLOR_UI_TEXT)
        surface.blit(ai_label, (setup_rect.x + 50, setup_rect.y + 60))

        ai_minus_btn = pygame.Rect(setup_rect.x + 300, setup_rect.y + 52, 45, 40)
        ai_plus_btn = pygame.Rect(setup_rect.x + 420, setup_rect.y + 52, 45, 40)

        draw_button(ai_minus_btn, "-")
        draw_button(ai_plus_btn, "+")

        ai_val_txt = self.btn_font.render(str(selected_ai_count), True, (255, 215, 0))
        surface.blit(ai_val_txt, (setup_rect.x + 368, setup_rect.y + 56))

        # Difficulty Selector Buttons (Left < and Right > arrows)
        diff_label = self.font.render("AI Difficulty Level:", True, config.COLOR_UI_TEXT)
        surface.blit(diff_label, (setup_rect.x + 50, setup_rect.y + 140))

        diff_minus_btn = pygame.Rect(setup_rect.x + 300, setup_rect.y + 132, 45, 40)
        diff_plus_btn = pygame.Rect(setup_rect.x + 520, setup_rect.y + 132, 45, 40)
        diff_btn = pygame.Rect(setup_rect.x + 355, setup_rect.y + 132, 155, 40)

        draw_button(diff_minus_btn, "<")
        draw_button(diff_plus_btn, ">")

        diff_val_txt = self.btn_font.render(f"Level {selected_difficulty}", True, (255, 215, 0))
        surface.blit(diff_val_txt, (diff_btn.x + diff_btn.width // 2 - diff_val_txt.get_width() // 2, diff_btn.y + 5))

        # Map Selector Cycle Button
        map_label = self.font.render("Map Type / Advantage:", True, config.COLOR_UI_TEXT)
        surface.blit(map_label, (setup_rect.x + 50, setup_rect.y + 220))

        map_names = {
            1: "Standard (Balanced)",
            2: "Disadvantage I (Scarce Resources)",
            3: "Disadvantage II (Distant & Very Scarce)",
            4: "Advantage I (Abundant Resources)",
            5: "Advantage II (Rich & Close Deposits)"
        }
        map_btn = pygame.Rect(setup_rect.x + 300, setup_rect.y + 212, 480, 42)
        draw_button(map_btn, f"{map_names.get(selected_map_type, 'Standard')}")

        # Action Buttons: Launch Match and Back
        start_match_btn = pygame.Rect(self.screen_width // 2 - 260, 560, 240, 52)
        draw_button(start_match_btn, "START MATCH", is_primary=True)

        back_btn = pygame.Rect(self.screen_width // 2 + 20, 560, 240, 52)
        draw_button(back_btn, "BACK TO MENU")

        return {
            "start_match": start_match_btn,
            "back": back_btn,
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

        t_title = self.title_font.render("GAME OPTIONS", True, (255, 215, 0))
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

        t_cb_label = self.btn_font.render("Disable Fog of War globally for all matches", True, config.COLOR_UI_TEXT)
        surface.blit(t_cb_label, (cb_rect.x + box_size + 20, cb_rect.y + 2))

        t_cb_desc = self.font.render("(Reveals the entire map and removes vision fog on the battlefield)", True, (160, 180, 200))
        surface.blit(t_cb_desc, (cb_rect.x + box_size + 20, cb_rect.y + 38))

        # Back Button
        back_btn = pygame.Rect(self.screen_width // 2 - 140, self.screen_height - 120, 280, 50)
        mouse_p = pygame.mouse.get_pos()
        hovered = back_btn.collidepoint(mouse_p)
        pygame.draw.rect(surface, (45, 55, 75) if hovered else config.COLOR_UI_PANEL, back_btn, border_radius=8)
        pygame.draw.rect(surface, (255, 215, 0) if hovered else config.COLOR_UI_ACCENT, back_btn, 2, border_radius=8)

        back_txt = self.btn_font.render("BACK TO MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 10))

        return {
            "back": back_btn,
            "fog_checkbox": cb_rect
        }

    def draw_pause_menu(self, surface):
        # Draw semi-transparent dark backdrop overlay over current gameplay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((10, 14, 20, 190))
        surface.blit(overlay, (0, 0))

        # Pause Panel Box
        panel_w, panel_h = 420, 360
        panel_rect = pygame.Rect((self.screen_width - panel_w) // 2, (self.screen_height - panel_h) // 2, panel_w, panel_h)
        pygame.draw.rect(surface, (24, 30, 42), panel_rect, border_radius=12)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, panel_rect, 2, border_radius=12)

        title = self.title_font.render("GAME PAUSED", True, (255, 215, 0))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, panel_rect.y + 25))

        btn_w, btn_h = 320, 48
        b_x = self.screen_width // 2 - btn_w // 2
        start_y = panel_rect.y + 100
        gap = 20

        resume_btn = pygame.Rect(b_x, start_y, btn_w, btn_h)
        main_menu_btn = pygame.Rect(b_x, start_y + btn_h + gap, btn_w, btn_h)
        quit_desktop_btn = pygame.Rect(b_x, start_y + (btn_h + gap) * 2, btn_w, btn_h)

        def draw_btn(rect, text, is_primary=False):
            mouse_p = pygame.mouse.get_pos()
            hovered = rect.collidepoint(mouse_p)
            bg_col = (45, 55, 75) if hovered else ((32, 40, 56) if not is_primary else (40, 120, 60))
            border_col = (255, 215, 0) if hovered else ((0, 255, 128) if is_primary else (90, 110, 140))

            pygame.draw.rect(surface, bg_col, rect, border_radius=8)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)

            t_surf = self.btn_font.render(text, True, (255, 255, 255) if hovered else config.COLOR_UI_TEXT)
            surface.blit(t_surf, (rect.x + rect.width // 2 - t_surf.get_width() // 2, rect.y + rect.height // 2 - t_surf.get_height() // 2))

        draw_btn(resume_btn, "RESUME GAME", is_primary=True)
        draw_btn(main_menu_btn, "QUIT TO MAIN MENU")
        draw_btn(quit_desktop_btn, "QUIT TO DESKTOP")

        return {
            "resume": resume_btn,
            "main_menu": main_menu_btn,
            "quit_desktop": quit_desktop_btn
        }

    def draw_iacia_menu(self, surface, game_state):
        surface.fill((15, 18, 26))

        # Header Title
        header_rect = pygame.Rect(0, 0, self.screen_width, 80)
        pygame.draw.rect(surface, (22, 27, 38), header_rect)
        pygame.draw.line(surface, config.COLOR_UI_ACCENT, (0, 80), (self.screen_width, 80), 2)

        t_title = self.title_font.render("SPECTATOR MODE TEAM CONFIGURATION (AI VS AI)", True, (255, 215, 0))
        surface.blit(t_title, (self.screen_width // 2 - t_title.get_width() // 2, 12))

        buttons = {}

        # Add AI & Remove AI Top Control Buttons
        ai_list = game_state.iacia_config.get("ai_players", [])

        top_btn_y = 100
        add_ai_btn = pygame.Rect(self.screen_width // 2 - 220, top_btn_y, 200, 38)
        remove_ai_btn = pygame.Rect(self.screen_width // 2 + 20, top_btn_y, 200, 38)

        mouse_p = pygame.mouse.get_pos()
        pygame.draw.rect(surface, (40, 100, 60) if add_ai_btn.collidepoint(mouse_p) else (30, 70, 45), add_ai_btn, border_radius=6)
        pygame.draw.rect(surface, (0, 255, 128), add_ai_btn, 2, border_radius=6)
        t_add = self.btn_font.render("+ Add AI Player", True, (255, 255, 255))
        surface.blit(t_add, (add_ai_btn.x + add_ai_btn.width // 2 - t_add.get_width() // 2, add_ai_btn.y + 5))
        buttons["add_ai"] = add_ai_btn

        pygame.draw.rect(surface, (120, 40, 40) if remove_ai_btn.collidepoint(mouse_p) else (80, 30, 30), remove_ai_btn, border_radius=6)
        pygame.draw.rect(surface, (255, 100, 100), remove_ai_btn, 2, border_radius=6)
        t_rem = self.btn_font.render("- Remove AI Player", True, (255, 255, 255))
        surface.blit(t_rem, (remove_ai_btn.x + remove_ai_btn.width // 2 - t_rem.get_width() // 2, remove_ai_btn.y + 5))
        buttons["remove_ai"] = remove_ai_btn

        # Map Selection Cycle
        m_type = game_state.iacia_config.get("map_type", 1)
        map_names = {
            1: "Standard (Balanced)",
            2: "Disadvantage I (Scarce Resources)",
            3: "Disadvantage II (Distant & Very Scarce)",
            4: "Advantage I (Abundant Resources)",
            5: "Advantage II (Rich & Close Deposits)"
        }
        map_btn = pygame.Rect(self.screen_width // 2 - 250, 150, 500, 38)
        hovered = map_btn.collidepoint(mouse_p)
        pygame.draw.rect(surface, (45, 55, 75) if hovered else (32, 40, 56), map_btn, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 0) if hovered else config.COLOR_UI_ACCENT, map_btn, 2, border_radius=6)
        t_m = self.font.render(f"Map: {map_names.get(m_type, 'Standard')}", True, (255, 255, 255))
        surface.blit(t_m, (map_btn.x + map_btn.width // 2 - t_m.get_width() // 2, map_btn.y + 6))
        buttons["map_type"] = map_btn

        # AI Table Container
        tbl_w = 1100
        tbl_h = max(200, min(520, len(ai_list) * 58 + 60))
        tbl_rect = pygame.Rect((self.screen_width - tbl_w) // 2, 200, tbl_w, tbl_h)
        pygame.draw.rect(surface, (22, 28, 40), tbl_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 75, 100), tbl_rect, 2, border_radius=10)

        # Header row
        pygame.draw.rect(surface, (30, 38, 54), (tbl_rect.x, tbl_rect.y, tbl_w, 40), border_top_left_radius=10, border_top_right_radius=10)
        t_h1 = self.bold_font
        surface.blit(t_h1.render("AI Player", True, config.COLOR_UI_ACCENT), (tbl_rect.x + 30, tbl_rect.y + 10))
        surface.blit(t_h1.render("Team Assignment", True, config.COLOR_UI_ACCENT), (tbl_rect.x + 200, tbl_rect.y + 10))
        surface.blit(t_h1.render("Faction Civilization", True, config.COLOR_UI_ACCENT), (tbl_rect.x + 420, tbl_rect.y + 10))
        surface.blit(t_h1.render("AI Difficulty (Level 1 to 18)", True, config.COLOR_UI_ACCENT), (tbl_rect.x + 680, tbl_rect.y + 10))

        row_y = tbl_rect.y + 48

        for idx, p in enumerate(ai_list):
            pid = p["id"]
            # Row background
            r_bg = (28, 35, 50) if idx % 2 == 0 else (24, 30, 42)
            r_rect = pygame.Rect(tbl_rect.x + 10, row_y, tbl_w - 20, 52)
            pygame.draw.rect(surface, r_bg, r_rect, border_radius=6)

            # Player ID label
            t_id = self.font.render(f"AI #{pid}", True, (255, 255, 255))
            surface.blit(t_id, (r_rect.x + 20, row_y + 12))

            # Team Selector (- and +)
            tm_minus = pygame.Rect(r_rect.x + 180, row_y + 8, 32, 34)
            tm_plus = pygame.Rect(r_rect.x + 280, row_y + 8, 32, 34)
            pygame.draw.rect(surface, (45, 55, 75), tm_minus, border_radius=4)
            pygame.draw.rect(surface, (45, 55, 75), tm_plus, border_radius=4)
            surface.blit(self.font.render("-", True, (255, 255, 255)), (tm_minus.x + 10, tm_minus.y + 4))
            surface.blit(self.font.render("+", True, (255, 255, 255)), (tm_plus.x + 8, tm_plus.y + 4))

            from src.ui.render_utils import get_team_color
            t_col = get_team_color(pid, game_state)
            t_tm = self.font.render(f"Team {p['team']}", True, t_col)
            surface.blit(t_tm, (r_rect.x + 218, row_y + 12))

            buttons[f"team_minus_{pid}"] = tm_minus
            buttons[f"team_plus_{pid}"] = tm_plus

            # Faction Toggle Button
            fac_btn = pygame.Rect(r_rect.x + 400, row_y + 8, 160, 34)
            f_label = "Medieval" if p.get("faction") == config.FACTION_HUMAN else "Alien Insect"
            f_col = (30, 136, 229) if p.get("faction") == config.FACTION_HUMAN else (216, 27, 96)
            pygame.draw.rect(surface, f_col, fac_btn, border_radius=4)
            t_fac = self.small_font.render(f_label, True, (255, 255, 255))
            surface.blit(t_fac, (fac_btn.x + fac_btn.width // 2 - t_fac.get_width() // 2, fac_btn.y + 8))
            buttons[f"faction_{pid}"] = fac_btn

            # Difficulty Selector (- and +)
            diff_minus = pygame.Rect(r_rect.x + 660, row_y + 8, 32, 34)
            diff_plus = pygame.Rect(r_rect.x + 820, row_y + 8, 32, 34)
            pygame.draw.rect(surface, (45, 55, 75), diff_minus, border_radius=4)
            pygame.draw.rect(surface, (45, 55, 75), diff_plus, border_radius=4)
            surface.blit(self.font.render("-", True, (255, 255, 255)), (diff_minus.x + 10, diff_minus.y + 4))
            surface.blit(self.font.render("+", True, (255, 255, 255)), (diff_plus.x + 8, diff_plus.y + 4))

            t_df = self.font.render(f"Level {p['difficulty']}", True, (255, 215, 0))
            surface.blit(t_df, (r_rect.x + 705, row_y + 12))

            buttons[f"diff_minus_{pid}"] = diff_minus
            buttons[f"diff_plus_{pid}"] = diff_plus

            row_y += 58

        # Start Spectate & Back Buttons
        launch_btn = pygame.Rect(self.screen_width // 2 - 260, self.screen_height - 90, 240, 50)
        pygame.draw.rect(surface, (40, 120, 60), launch_btn, border_radius=8)
        pygame.draw.rect(surface, (0, 255, 128), launch_btn, 2, border_radius=8)
        t_l = self.btn_font.render("LAUNCH MATCH", True, (255, 255, 255))
        surface.blit(t_l, (launch_btn.x + launch_btn.width // 2 - t_l.get_width() // 2, launch_btn.y + 10))
        buttons["launch"] = launch_btn

        back_btn = pygame.Rect(self.screen_width // 2 + 20, self.screen_height - 90, 240, 50)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=8)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=8)
        t_b = self.btn_font.render("BACK TO MENU", True, config.COLOR_UI_TEXT)
        surface.blit(t_b, (back_btn.x + back_btn.width // 2 - t_b.get_width() // 2, back_btn.y + 10))
        buttons["back"] = back_btn

        return buttons

    def draw_ai_info_screen(self, surface, scroll_y=0):
        self.ai_info_scroll_y = scroll_y
        surface.fill((15, 18, 26))

        # Title (Fixed Header)
        header_rect = pygame.Rect(0, 0, self.screen_width, 70)
        pygame.draw.rect(surface, (22, 27, 38), header_rect)
        pygame.draw.line(surface, config.COLOR_UI_ACCENT, (0, 70), (self.screen_width, 70), 2)

        t_title = self.title_font.render("ALIEN INSECT CIVILIZATION & AI LEVELS", True, (255, 215, 0))
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
            "• Biomass Economy: Alien insects harvest organic biomass to evolve structures and spawn army strains.",
            "• Hive Mind Intelligence: Real-time strategic decision engine with dynamic target selection and flanking.",
            "• Alien Strains: Drones (workers), Swarmers (fast melee combatants), Spitters (acid ranged), and Queen (spore launcher mutating victims into Swarmers).",
            "• Structures & Tech: Hive (Main base), Spawning Pool (Troop hatchery), Spine Crawler (Defense), Biomass Generator (Passive income) & Evolution Chamber (Upgrades)."
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
        t_lvl_head = self.btn_font.render("AI DIFFICULTY LEVEL DESCRIPTIONS (1 TO 18)", True, config.COLOR_UI_ACCENT)

        ai_descriptions = {
            1: "Level 1: Income x1.0. Units: Drones & Swarmers. Full real-time strategic decision engine.",
            2: "Level 2: Income x1.1. Unlocks +1 extra starting Swarmer.",
            3: "Level 3: Income x1.2. Unlocks +1 extra starting Drone.",
            4: "Level 4: Income x1.3. Unlocks defensive Spine Crawlers. +15% HP/Atk.",
            5: "Level 5 (Biomass Depot): Income x1.4. Builds Biomass Stockpiles.",
            6: "Level 6 (Spitters): Income x1.5. Unlocks ranged acid Spitters.",
            7: "Level 7 (Hive Enrage): Income x1.6. Hive ability (60s CD): +10% Speed/Atk for 5s.",
            8: "Level 8 (Creep Spread): Income x1.7. Creep around Hives (+25% Speed/Atk on Creep).",
            9: "Level 9 (Double Swarmer): Income x1.85. Swarmer training spawns 2 Swarmers per egg.",
            10: "Level 10 (Biomass Generators): Income x2.0. Builds Biomass Generators.",
            11: "Level 11 (Swarm Frenzy): Income x2.2. Swarm Frenzy (+25% Speed). +45% HP, +60% Atk.",
            12: "Level 12 (Supreme Harvest): Income x2.5. Enemy kills award Biomass.",
            13: "Level 13 (Enhanced Enrage): Income x2.8. Boosts Hive ability to +20% Speed/Atk.",
            14: "Level 14 (Alien Queen): Income x3.2. Unlocks Queen (mutates killed targets into Swarmers).",
            15: "Level 15 (Second Hive & Drones): Income x3.6. Expands with 2nd Hive & +2 starting Drones.",
            16: "Level 16 (Double Deposits): Income x4.0. Biomass nodes on map generated with 2x capacity.",
            17: "Level 17 (Drone Swarm): Income x4.5. +4 additional starting Drones.",
            18: "Level 18 (Evolution Chamber): Income x5.0. Evolution Chamber (+10% HP, -10% Swarmer cost, +5% biomass gen)."
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
            l2_wrapped = wrap_text(f"Income: x{mult} | Max Workers: {m_work} | Max Army: {m_army} | Techs: [{techs}] | Bonus: HP +{hp_b}%, Atk +{atk_b}%", self.small_font, text_max_w)

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
        t_civ_head = self.btn_font.render("ALIEN INSECT CIVILIZATION MECHANICS", True, (216, 27, 96))
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

            header_txt = f"AI LEVEL {lvl}"
            if is_extreme:
                header_txt += " [SPECIAL ABILITY ACTIVE]"
            elif is_fog:
                header_txt += " [FOG OF WAR ACTIVE]"

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
        back_txt = self.btn_font.render("BACK TO MENU", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 8))

        return {
            "back": back_btn,
            "max_scroll": content_h - viewport_h,
            "current_scroll": clamp_scroll
        }
