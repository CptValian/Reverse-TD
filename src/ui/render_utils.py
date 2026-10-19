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
            RenderUtils._draw_resource(surface, entity, sx, sy, scaled_radius)

        # Rendu des bâtiments
        elif hasattr(entity, 'building_type'):
            RenderUtils._draw_building(surface, camera, entity, sx, sy, scaled_radius)

        # Rendu des unités
        elif hasattr(entity, 'unit_type'):
            RenderUtils._draw_unit(surface, camera, entity, sx, sy, scaled_radius)

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

    @staticmethod
    def _draw_resource(surface, res, sx, sy, radius):
        if res.resource_type == "gold":
            pygame.draw.circle(surface, (218, 165, 32), (sx, sy), radius)
            pygame.draw.circle(surface, (255, 215, 0), (sx, sy), int(radius * 0.7))
            pygame.draw.circle(surface, (255, 250, 205), (sx - radius//3, sy - radius//3), int(radius * 0.3))
        elif res.resource_type == "wood":
            # Arbre / Forêt (Tronc marron + feuillage vert)
            pygame.draw.rect(surface, (101, 67, 33), (sx - radius//4, sy, radius//2, radius))
            pygame.draw.circle(surface, (34, 139, 34), (sx, sy - radius//3), int(radius * 0.8))
            pygame.draw.circle(surface, (50, 205, 50), (sx - radius//3, sy - radius//2), int(radius * 0.5))
        elif res.resource_type == "food":
            # Baies / Cultures (Fond vert + petits fruits oranges)
            pygame.draw.circle(surface, (46, 125, 50), (sx, sy), radius)
            pygame.draw.circle(surface, (255, 140, 0), (sx - radius//3, sy - radius//3), max(2, radius//4))
            pygame.draw.circle(surface, (255, 140, 0), (sx + radius//3, sy + radius//4), max(2, radius//4))
            pygame.draw.circle(surface, (255, 165, 0), (sx, sy + radius//3), max(2, radius//4))
        else:
            # Biomasse Alien
            pygame.draw.circle(surface, (106, 27, 154), (sx, sy), radius)
            pygame.draw.circle(surface, (156, 39, 176), (sx, sy), int(radius * 0.7))
            pygame.draw.circle(surface, (76, 175, 80), (sx, sy), int(radius * 0.3))

    @staticmethod
    def _draw_building(surface, camera, building, sx, sy, radius):
        b_type = building.building_type
        faction = building.faction

        # Alpha / Transparence si en construction
        color_main = config.COLOR_HUMAN_PRIMARY if faction == config.FACTION_HUMAN else config.COLOR_ALIEN_PRIMARY
        if not building.is_constructed:
            color_main = (120, 120, 120)

        rect = pygame.Rect(sx - radius, sy - radius, radius * 2, radius * 2)

        if faction == config.FACTION_HUMAN:
            # --- MÉDIÉVAL ---
            if b_type == "TownHall":
                # Château fort / Donjon
                pygame.draw.rect(surface, (100, 100, 105), rect, border_radius=6)
                pygame.draw.rect(surface, (180, 180, 190), rect, width=3, border_radius=6)
                # Crenellations
                cw = max(4, radius // 3)
                for i in range(3):
                    pygame.draw.rect(surface, (70, 70, 75), (sx - radius + i * cw * 2, sy - radius - 4, cw, 6))
                # Porte du château
                pygame.draw.rect(surface, (101, 67, 33), (sx - cw//2, sy + radius//3, cw + 4, radius * 2 // 3))

            elif b_type == "Barracks":
                # Caserne (Toit en bois / Enceinte d'entraînement)
                pygame.draw.rect(surface, (120, 80, 40), rect, border_radius=4)
                pygame.draw.rect(surface, (200, 150, 80), rect, width=2, border_radius=4)
                # Épées croisées au centre
                pygame.draw.line(surface, (220, 220, 220), (sx - radius//2, sy - radius//2), (sx + radius//2, sy + radius//2), 3)
                pygame.draw.line(surface, (220, 220, 220), (sx + radius//2, sy - radius//2), (sx - radius//2, sy + radius//2), 3)

            elif b_type == "Tower":
                # Tour de défense circulaire en pierre
                pygame.draw.circle(surface, (110, 110, 120), (sx, sy), radius)
                pygame.draw.circle(surface, (220, 220, 230), (sx, sy), radius, width=3)
                pygame.draw.circle(surface, (180, 50, 50), (sx, sy), max(2, radius // 2))

            elif b_type == "Wall":
                # Palisade en bois
                pygame.draw.rect(surface, (139, 69, 19), rect, border_radius=3)
                pygame.draw.rect(surface, (205, 133, 63), rect, width=2, border_radius=3)

            elif b_type == "WoodStockpile":
                # Stock de bois
                pygame.draw.rect(surface, (110, 70, 35), rect, border_radius=4)
                pygame.draw.line(surface, (180, 120, 60), (sx - radius + 4, sy - radius//2), (sx + radius - 4, sy - radius//2), 4)
                pygame.draw.line(surface, (180, 120, 60), (sx - radius + 4, sy), (sx + radius - 4, sy), 4)
                pygame.draw.line(surface, (180, 120, 60), (sx - radius + 4, sy + radius//2), (sx + radius - 4, sy + radius//2), 4)

            elif b_type == "GoldStockpile":
                # Stock d'or
                pygame.draw.rect(surface, (80, 80, 90), rect, border_radius=4)
                pygame.draw.circle(surface, (255, 215, 0), (sx, sy), max(3, radius//2))

            elif b_type == "Farm":
                # Ferme
                pygame.draw.rect(surface, (160, 120, 60), rect, border_radius=4)
                pygame.draw.rect(surface, (218, 165, 32), (sx - radius + 4, sy - radius + 4, radius - 2, radius - 2))
                pygame.draw.rect(surface, (34, 139, 34), (sx + 2, sy + 2, radius - 4, radius - 4))

        else:
            # --- ALIEN INSECT ---
            if b_type == "Hive":
                # Ruche alien organic / Œuf géant
                pygame.draw.ellipse(surface, (123, 31, 162), rect)
                pygame.draw.ellipse(surface, (216, 27, 96), rect, width=3)
                pygame.draw.circle(surface, (76, 175, 80), (sx, sy), max(3, radius // 3))

            elif b_type == "SpawningPool":
                # Bassin de ponte organique
                pygame.draw.circle(surface, (74, 20, 140), (sx, sy), radius)
                pygame.draw.circle(surface, (0, 230, 118), (sx, sy), int(radius * 0.75))
                pygame.draw.circle(surface, (200, 230, 0), (sx, sy), int(radius * 0.3))

            elif b_type == "SpineCrawler":
                # Aiguillon vivant défense
                pygame.draw.polygon(surface, (180, 20, 80), [
                    (sx, sy - radius),
                    (sx + radius, sy + radius),
                    (sx - radius, sy + radius)
                ])
                pygame.draw.circle(surface, (255, 235, 59), (sx, sy), max(2, radius // 3))

        # Barre de progression de construction si sous construction
        if not building.is_constructed:
            ratio = 1.0 - (building.build_timer / max(0.001, building.total_build_time))
            bw = radius * 2
            bh = 6
            pygame.draw.rect(surface, (40, 40, 40), (sx - radius, sy + radius + 4, bw, bh))
            pygame.draw.rect(surface, (255, 179, 0), (sx - radius, sy + radius + 4, int(bw * ratio), bh))

    @staticmethod
    def _draw_unit(surface, camera, unit, sx, sy, radius):
        u_type = unit.unit_type
        faction = unit.faction

        if faction == config.FACTION_HUMAN:
            # --- FACTION MÉDIÉVALE ---
            if u_type == "Worker":
                # Ouvrier avec un pic / marteau
                pygame.draw.circle(surface, (210, 180, 140), (sx, sy), radius)
                pygame.draw.circle(surface, (139, 69, 19), (sx, sy), radius, width=2)
            elif u_type == "Infantry":
                # Chevalier avec bouclier
                pygame.draw.circle(surface, (30, 136, 229), (sx, sy), radius)
                pygame.draw.circle(surface, (220, 220, 220), (sx, sy), radius, width=2)
                # Épée
                pygame.draw.line(surface, (255, 255, 255), (sx, sy), (sx + radius + 2, sy), 2)
            elif u_type == "Archer":
                # Archer avec arc
                pygame.draw.circle(surface, (46, 125, 50), (sx, sy), radius)
                pygame.draw.circle(surface, (200, 230, 0), (sx, sy), radius, width=2)
                # Arc
                pygame.draw.arc(surface, (139, 69, 19), (sx - radius, sy - radius, radius*2, radius*2), -1.0, 1.0, 2)
        else:
            # --- FACTION ALIEN INSECTE ---
            if u_type == "Drone":
                # Petit ouvrier insectoïde à pattes
                pygame.draw.circle(surface, (142, 36, 170), (sx, sy), radius)
                pygame.draw.circle(surface, (216, 27, 96), (sx, sy), radius, width=2)
            elif u_type == "Swarmer":
                # Losange rapide type Zergling
                pts = [
                    (sx, sy - radius - 2),
                    (sx + radius + 2, sy),
                    (sx, sy + radius + 2),
                    (sx - radius - 2, sy)
                ]
                pygame.draw.polygon(surface, (216, 27, 96), pts)
                pygame.draw.polygon(surface, (255, 235, 59), pts, width=1)
            elif u_type == "Spitter":
                # Insecte cracheur (Triangle vert)
                pts = [
                    (sx, sy - radius - 3),
                    (sx + radius + 1, sy + radius),
                    (sx - radius - 1, sy + radius)
                ]
                pygame.draw.polygon(surface, (76, 175, 80), pts)
                pygame.draw.polygon(surface, (216, 27, 96), pts, width=2)

        # Effet visuel d'attaque (Flash / Projectile)
        if unit.is_attacking_anim > 0 and unit.target_entity:
            t_pos = camera.world_to_screen((unit.target_entity.x, unit.target_entity.y))
            if unit.unit_type in ["Archer", "Spitter"]:
                # Tir de projectile (Flèche ou Spore)
                p_color = (255, 235, 59) if unit.unit_type == "Archer" else (0, 255, 128)
                pygame.draw.line(surface, p_color, (sx, sy), (int(t_pos[0]), int(t_pos[1])), 3)
            else:
                # Flash de coup au CàC
                pygame.draw.circle(surface, (255, 50, 50), (int(t_pos[0]), int(t_pos[1])), radius + 4, 2)

        # Effet visuel de récolte
        if unit.is_harvesting_anim > 0 and unit.target_entity:
            t_pos = camera.world_to_screen((unit.target_entity.x, unit.target_entity.y))
            pygame.draw.line(surface, (255, 215, 0), (sx, sy), (int(t_pos[0]), int(t_pos[1])), 1)

        # Afficher la ressource transportée par un ouvrier
        if unit.carried_resource > 0:
            c_color = (255, 215, 0) if unit.resource_type == "gold" else (76, 175, 80)
            pygame.draw.circle(surface, c_color, (sx, sy - radius - 4), max(2, radius // 3))
