import pygame
import config

class HUD:
    def __init__(self, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Arial", 16)
        self.title_font = pygame.font.SysFont("Arial", 20, bold=True)

    def draw(self, surface, game_state, camera):
        # 1. Barre supérieure (Ressources du Joueur Humain)
        player_res = game_state.resources_player.get(0, {"gold": 0, "biomass": 0})
        top_bar = pygame.Rect(0, 0, self.screen_width, 40)
        pygame.draw.rect(surface, config.COLOR_UI_BG, top_bar)
        pygame.draw.line(surface, config.COLOR_UI_ACCENT, (0, 40), (self.screen_width, 40), 2)

        res_text = f"Or: {int(player_res.get('gold', 0))} | Biomasse: {int(player_res.get('biomass', 0))} | Unités: {game_state.get_unit_count(0)}"
        img_res = self.title_font.render(res_text, True, config.COLOR_UI_TEXT)
        surface.blit(img_res, (20, 8))

        # 2. Mini-Carte (en bas à gauche)
        minimap_size = 150
        minimap_rect = pygame.Rect(10, self.screen_height - minimap_size - 10, minimap_size, minimap_size)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, minimap_rect)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, minimap_rect, 2)

        # Dessiner les entités sur la mini-carte
        scale_x = minimap_size / config.MAP_WIDTH
        scale_y = minimap_size / config.MAP_HEIGHT

        for entity in game_state.units + game_state.buildings:
            if not entity.alive:
                continue
            mx = minimap_rect.x + int(entity.x * scale_x)
            my = minimap_rect.y + int(entity.y * scale_y)
            color = (0, 255, 0) if entity.owner_id == 0 else (255, 0, 0)
            pygame.draw.circle(surface, color, (mx, my), 2)

        # Rectangle de vue caméra sur la mini-carte
        cam_rect = camera.get_visible_rect()
        cx = minimap_rect.x + int(cam_rect.x * scale_x)
        cy = minimap_rect.y + int(cam_rect.y * scale_y)
        cw = int(cam_rect.width * scale_x)
        ch = int(cam_rect.height * scale_y)
        pygame.draw.rect(surface, (255, 255, 255), (cx, cy, cw, ch), 1)

        # 3. Panneau de Sélection & Bâtiment (en bas au centre)
        panel_rect = pygame.Rect(minimap_size + 30, self.screen_height - 150, self.screen_width - minimap_size - 40, 140)
        pygame.draw.rect(surface, config.COLOR_UI_PANEL, panel_rect)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, panel_rect, 2)

        selected_entities = [e for e in game_state.units + game_state.buildings if e.selected and e.owner_id == 0]
        if selected_entities:
            first = selected_entities[0]
            info_text = f"Sélection: {getattr(first, 'unit_type', getattr(first, 'building_type', 'Entité'))} (PV: {int(first.hp)}/{first.max_hp})"
            img_info = self.font.render(info_text, True, config.COLOR_UI_TEXT)
            surface.blit(img_info, (panel_rect.x + 20, panel_rect.y + 15))

            # Si c'est un bâtiment de production
            if hasattr(first, 'building_type') and first.trainable_units:
                btn_x = panel_rect.x + 20
                btn_y = panel_rect.y + 50
                for u_type in first.trainable_units:
                    btn_rect = pygame.Rect(btn_x, btn_y, 140, 40)
                    pygame.draw.rect(surface, (60, 64, 72), btn_rect, border_radius=4)
                    pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)
                    t_surf = self.font.render(f"Recruter {u_type}", True, config.COLOR_UI_TEXT)
                    surface.blit(t_surf, (btn_x + 10, btn_y + 10))
                    btn_x += 150

            # Si un ouvrier est sélectionné (boutons de construction)
            elif getattr(first, 'is_worker', False):
                btn_x = panel_rect.x + 20
                btn_y = panel_rect.y + 50
                buildings_to_build = ["Barracks", "Tower"] if first.faction == config.FACTION_HUMAN else ["SpawningPool", "SpineCrawler"]
                for b_type in buildings_to_build:
                    btn_rect = pygame.Rect(btn_x, btn_y, 160, 40)
                    pygame.draw.rect(surface, (60, 64, 72), btn_rect, border_radius=4)
                    pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)
                    t_surf = self.font.render(f"Construire {b_type}", True, config.COLOR_UI_TEXT)
                    surface.blit(t_surf, (btn_x + 10, btn_y + 10))
                    btn_x += 170
