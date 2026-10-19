import pygame
import config

class ProgressionUI:
    def __init__(self, save_manager, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT):
        self.save_manager = save_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.font = pygame.font.SysFont("Arial", 18)

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        title = self.title_font.render("ARBRE DE COMPÉTENCES & AMÉLIORATIONS", True, config.COLOR_UI_ACCENT)
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 40))

        # Affichage des points
        pts = self.save_manager.get_points()
        pts_text = f"Points de Commandement: {pts['Commandement']} | Points de Forge: {pts['Forge']} | Points d'Architecture: {pts['Architecture']}"
        pts_surf = self.font.render(pts_text, True, config.COLOR_UI_TEXT)
        surface.blit(pts_surf, (self.screen_width // 2 - pts_surf.get_width() // 2, 90))

        # Liste des améliorations disponibles
        upgrades = [
            {"key": "unit_hp_lvl", "type": "Forge", "name": "PV Unités (+10%)", "cost_base": 10},
            {"key": "unit_attack_lvl", "type": "Forge", "name": "Attaque Unités (+10%)", "cost_base": 15},
            {"key": "unit_speed_lvl", "type": "Forge", "name": "Vitesse Unités (+5%)", "cost_base": 12},
            {"key": "building_hp_lvl", "type": "Architecture", "name": "PV Bâtiments (+15%)", "cost_base": 10},
            {"key": "building_armor_lvl", "type": "Architecture", "name": "Armure Bâtiments (+1)", "cost_base": 20},
            {"key": "starting_resources_lvl", "type": "Commandement", "name": "Ressources Départ (+100)", "cost_base": 25},
        ]

        buttons = {}
        y = 160
        upg_data = self.save_manager.data["upgrades"]

        for upg in upgrades:
            key = upg["key"]
            lvl = upg_data.get(key, 0)
            cost = upg["cost_base"] * (lvl + 1)

            text_line = f"{upg['name']} - Niv. {lvl} (Coût: {cost} Pts {upg['type']})"
            line_surf = self.font.render(text_line, True, config.COLOR_UI_TEXT)
            surface.blit(line_surf, (200, y + 10))

            btn_rect = pygame.Rect(750, y, 150, 36)
            pygame.draw.rect(surface, config.COLOR_UI_PANEL, btn_rect, border_radius=4)
            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)
            btn_txt = self.font.render("AMÉLIORER", True, config.COLOR_UI_TEXT)
            surface.blit(btn_txt, (btn_rect.x + 20, btn_rect.y + 6))

            buttons[key] = {"rect": btn_rect, "type": upg["type"], "cost_base": upg["cost_base"]}
            y += 60

        # Bouton Retour
        back_btn = pygame.Rect(self.screen_width // 2 - 100, self.screen_height - 80, 200, 45)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, back_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, back_btn, 2, border_radius=6)
        back_txt = self.font.render("RETOUR", True, config.COLOR_UI_TEXT)
        surface.blit(back_txt, (back_btn.x + back_btn.width // 2 - back_txt.get_width() // 2, back_btn.y + 10))
        buttons["back"] = back_btn

        return buttons
