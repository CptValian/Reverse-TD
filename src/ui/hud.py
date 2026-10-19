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
            name = getattr(first, 'unit_type', getattr(first, 'building_type', 'Entité'))
            status_extra = ""
            if hasattr(first, 'is_constructed') and not first.is_constructed:
                pct = int((1.0 - first.build_timer / max(0.001, first.total_build_time)) * 100)
                status_extra = f" [En construction: {pct}%]"

            info_text = f"Sélection: {name} (PV: {int(first.hp)}/{first.max_hp}){status_extra}"
            img_info = self.font.render(info_text, True, config.COLOR_UI_TEXT)
            surface.blit(img_info, (panel_rect.x + 20, panel_rect.y + 10))

            # Si c'est un bâtiment
            if hasattr(first, 'building_type'):
                btn_x = panel_rect.x + 20
                btn_y = panel_rect.y + 35

                # Boutons de recrutement
                if first.trainable_units and first.is_constructed:
                    for u_type in first.trainable_units:
                        u_data = config.UNIT_TYPES.get(u_type, {})
                        cost = u_data.get("cost", 50)
                        res_name = "Or" if u_data.get("res_type", "gold") == "gold" else "Bio"

                        btn_rect = pygame.Rect(btn_x, btn_y, 150, 40)
                        pygame.draw.rect(surface, (60, 64, 72), btn_rect, border_radius=4)
                        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)

                        t_name = self.font.render(f"+ {u_type}", True, config.COLOR_UI_TEXT)
                        t_cost = self.font.render(f"{cost} {res_name}", True, config.COLOR_UI_ACCENT)
                        surface.blit(t_name, (btn_x + 8, btn_y + 4))
                        surface.blit(t_cost, (btn_x + 8, btn_y + 20))
                        btn_x += 160

                # Affichage de la file d'attente de production
                queue_x = panel_rect.x + 20
                queue_y = panel_rect.y + 85
                if first.production_queue:
                    q_title = self.font.render("File d'attente:", True, config.COLOR_UI_TEXT)
                    surface.blit(q_title, (queue_x, queue_y))
                    qx = queue_x + 100
                    for idx, item in enumerate(first.production_queue[:5]):
                        u_name = item["unit_type"]
                        rem = max(0.0, item["time_remaining"])
                        tot = max(0.1, item["total_time"])
                        ratio = 1.0 - (rem / tot)

                        q_box = pygame.Rect(qx, queue_y - 2, 90, 26)
                        pygame.draw.rect(surface, (30, 34, 42), q_box, border_radius=3)
                        pygame.draw.rect(surface, (100, 100, 100), q_box, 1, border_radius=3)

                        if idx == 0:
                            # Barre de progression pour le premier élément
                            progress_rect = pygame.Rect(qx + 1, queue_y - 1, int(88 * ratio), 24)
                            pygame.draw.rect(surface, (46, 125, 50), progress_rect, border_radius=2)

                        item_text = f"{u_name} ({int(rem)}s)" if idx == 0 else u_name
                        t_q = self.font.render(item_text, True, config.COLOR_UI_TEXT)
                        surface.blit(t_q, (qx + 5, queue_y + 3))
                        qx += 98

            # Si un ouvrier est sélectionné (boutons de construction)
            elif getattr(first, 'is_worker', False):
                btn_x = panel_rect.x + 20
                btn_y = panel_rect.y + 40
                buildings_to_build = ["Barracks", "Tower"] if first.faction == config.FACTION_HUMAN else ["SpawningPool", "SpineCrawler"]
                for b_type in buildings_to_build:
                    b_data = config.BUILDING_TYPES.get(b_type, {})
                    cost = b_data.get("cost", 100)
                    res_name = "Or" if b_data.get("res_type", "gold") == "gold" else "Bio"

                    btn_rect = pygame.Rect(btn_x, btn_y, 170, 45)
                    pygame.draw.rect(surface, (60, 64, 72), btn_rect, border_radius=4)
                    pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)

                    t_name = self.font.render(f"Bâtir {b_type}", True, config.COLOR_UI_TEXT)
                    t_cost = self.font.render(f"{cost} {res_name} ({b_data.get('build_time', 10)}s)", True, config.COLOR_UI_ACCENT)
                    surface.blit(t_name, (btn_x + 8, btn_y + 4))
                    surface.blit(t_cost, (btn_x + 8, btn_y + 24))
                    btn_x += 180
