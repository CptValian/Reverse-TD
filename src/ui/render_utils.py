import pygame
import config

class RenderUtils:
    @staticmethod
    def draw_entity(surface, camera, entity):
        screen_pos = camera.world_to_screen((entity.x, entity.y))
        sx, sy = int(screen_pos[0]), int(screen_pos[1])
        scaled_radius = max(3, int(entity.radius * camera.zoom))

        # Vérifier si l'entité est visible sur l'écran
        rect = camera.get_visible_rect()
        if not (rect.x - entity.radius <= entity.x <= rect.x + rect.width + entity.radius and
                rect.y - entity.radius <= entity.y <= rect.y + rect.height + entity.radius):
            return

        # Rendu des ressources
        if hasattr(entity, 'resource_type'):
            color = config.COLOR_RESOURCE_GOLD if entity.resource_type == "gold" else config.COLOR_RESOURCE_BIOMASS
            pygame.draw.circle(surface, color, (sx, sy), scaled_radius)
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy), scaled_radius, 1)

        # Rendu des bâtiments
        elif hasattr(entity, 'building_type'):
            color = config.COLOR_HUMAN_PRIMARY if entity.faction == config.FACTION_HUMAN else config.COLOR_ALIEN_PRIMARY
            rect_shape = pygame.Rect(sx - scaled_radius, sy - scaled_radius, scaled_radius * 2, scaled_radius * 2)
            pygame.draw.rect(surface, color, rect_shape, border_radius=4)
            pygame.draw.rect(surface, (200, 200, 200), rect_shape, width=2, border_radius=4)

        # Rendu des unités
        elif hasattr(entity, 'unit_type'):
            color = config.COLOR_HUMAN_PRIMARY if entity.faction == config.FACTION_HUMAN else config.COLOR_ALIEN_PRIMARY
            if entity.faction == config.FACTION_HUMAN:
                pygame.draw.circle(surface, color, (sx, sy), scaled_radius)
            else:
                # Forme en losange pour les aliens
                points = [
                    (sx, sy - scaled_radius),
                    (sx + scaled_radius, sy),
                    (sx, sy + scaled_radius),
                    (sx - scaled_radius, sy)
                ]
                pygame.draw.polygon(surface, color, points)

        # Cercles de sélection
        if entity.selected:
            pygame.draw.circle(surface, config.COLOR_SELECTION, (sx, sy), scaled_radius + 4, 2)

        # Barre de vie
        if entity.hp < entity.max_hp and entity.max_hp > 0:
            bar_width = max(20, scaled_radius * 2)
            bar_height = 4
            bx = sx - bar_width // 2
            by = sy - scaled_radius - 8
            health_ratio = max(0.0, entity.hp / entity.max_hp)

            pygame.draw.rect(surface, config.COLOR_HEALTH_BG, (bx, by, bar_width, bar_height))
            pygame.draw.rect(surface, config.COLOR_HEALTH_BAR, (bx, by, int(bar_width * health_ratio), bar_height))
