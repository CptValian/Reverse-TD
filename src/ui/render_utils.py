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

        # Verification Brouillard de Guerre pour les entités ennemies et ressources neutres
        if hasattr(camera, 'game_state') and camera.game_state:
            gs = camera.game_state
            if gs.is_fog_of_war_enabled():
                # Le joueur (owner_id == 0) voit toujours ses propres entités
                if getattr(entity, 'owner_id', None) != 0:
                    if not gs.is_point_visible(entity.x, entity.y, owner_id=0):
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

            # Draw Rally Point line and marker if building with rally point selected
            if hasattr(entity, 'building_type') and entity.owner_id == 0 and getattr(entity, 'rally_point', None):
                rx, ry = entity.rally_point
                rsp = camera.world_to_screen((rx, ry))
                rsx, rsy = int(rsp[0]), int(rsp[1])
                pygame.draw.line(surface, (0, 255, 255), (sx, sy), (rsx, rsy), 2)
                pygame.draw.circle(surface, (0, 255, 255), (rsx, rsy), 6, 2)
                pygame.draw.circle(surface, (255, 215, 0), (rsx, rsy), 3)

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

        # Under construction dimming
        rect = pygame.Rect(sx - radius, sy - radius, radius * 2, radius * 2)

        if faction == config.FACTION_HUMAN:
            # --- MEDIEVAL HUMANS ---
            if b_type == "TownHall":
                # Medieval Castle Keep / Stronghold
                # Base stone courtyard
                pygame.draw.rect(surface, (85, 90, 100), rect, border_radius=8)
                pygame.draw.rect(surface, (160, 170, 185), rect, width=3, border_radius=8)

                # Central Keep Tower
                keep_w, keep_h = int(radius * 1.1), int(radius * 1.1)
                keep_rect = pygame.Rect(sx - keep_w//2, sy - keep_h//2, keep_w, keep_h)
                pygame.draw.rect(surface, (110, 115, 128), keep_rect, border_radius=4)
                pygame.draw.rect(surface, (200, 210, 225), keep_rect, width=2, border_radius=4)

                # 4 Corner Towers
                tw_r = max(4, radius // 3)
                for tx, ty in [(sx - radius + tw_r, sy - radius + tw_r),
                               (sx + radius - tw_r, sy - radius + tw_r),
                               (sx - radius + tw_r, sy + radius - tw_r),
                               (sx + radius - tw_r, sy + radius - tw_r)]:
                    pygame.draw.circle(surface, (70, 75, 85), (tx, ty), tw_r)
                    pygame.draw.circle(surface, (220, 225, 235), (tx, ty), tw_r, width=2)
                    # Red Conical Roofs
                    pygame.draw.polygon(surface, (180, 40, 40), [(tx, ty - tw_r - 4), (tx - tw_r, ty), (tx + tw_r, ty)])

                # Castle Wooden Gate & Iron Portcullis
                gate_w, gate_h = max(6, radius // 2), max(10, radius * 3 // 4)
                pygame.draw.rect(surface, (101, 67, 33), (sx - gate_w//2, sy + radius//3 - 2, gate_w, gate_h), border_radius=3)
                pygame.draw.rect(surface, (40, 40, 45), (sx - gate_w//2, sy + radius//3 - 2, gate_w, gate_h), width=2, border_radius=3)

                # Blue Kingdom Banner
                pygame.draw.line(surface, (255, 215, 0), (sx, sy - keep_h//2 - 12), (sx, sy - keep_h//2), 2)
                pygame.draw.polygon(surface, (30, 136, 229), [(sx, sy - keep_h//2 - 12), (sx + 12, sy - keep_h//2 - 8), (sx, sy - keep_h//2 - 4)])

            elif b_type == "Barracks":
                # Military Barracks & Training Grounds
                # Wooden Timber Frame Building
                pygame.draw.rect(surface, (120, 80, 45), rect, border_radius=6)
                pygame.draw.rect(surface, (190, 140, 80), rect, width=2, border_radius=6)

                # Tiled Roof
                roof_pts = [(sx - radius - 4, sy - radius // 3), (sx, sy - radius - 8), (sx + radius + 4, sy - radius // 3)]
                pygame.draw.polygon(surface, (150, 50, 40), roof_pts)
                pygame.draw.polygon(surface, (200, 80, 70), roof_pts, width=2)

                # Crossed Swords Emblem
                pygame.draw.line(surface, (230, 230, 240), (sx - radius//2, sy + radius//4), (sx + radius//2, sy - radius//3), 3)
                pygame.draw.line(surface, (230, 230, 240), (sx + radius//2, sy + radius//4), (sx - radius//2, sy - radius//3), 3)
                # Sword Hilts
                pygame.draw.circle(surface, (255, 215, 0), (sx - radius//2, sy + radius//4), 3)
                pygame.draw.circle(surface, (255, 215, 0), (sx + radius//2, sy + radius//4), 3)

            elif b_type == "Tower":
                # Stone Defensive Watchtower
                # Octagonal Stone Base
                pygame.draw.circle(surface, (100, 105, 115), (sx, sy), radius)
                pygame.draw.circle(surface, (200, 205, 215), (sx, sy), radius, width=3)

                # Wooden Platform Top
                pygame.draw.circle(surface, (139, 69, 19), (sx, sy), int(radius * 0.7))
                pygame.draw.circle(surface, (218, 165, 32), (sx, sy), int(radius * 0.7), width=2)

                # Arrow Slit / Archer Window
                pygame.draw.rect(surface, (20, 20, 25), (sx - 3, sy - radius//2, 6, 12))
                # Red Roof Cap
                pygame.draw.polygon(surface, (180, 40, 40), [(sx, sy - radius - 8), (sx - radius//2, sy - radius//3), (sx + radius//2, sy - radius//3)])

            elif b_type == "Wall":
                # Continuous Solid Palisade Wall Segment without separation gaps
                import math
                w_len = getattr(building, 'wall_length', 40)
                w_wid = getattr(building, 'wall_width', 20)
                w_ang = getattr(building, 'wall_angle', 0.0)

                scaled_l = max(12, int(w_len * camera.zoom))
                scaled_w = max(8, int(w_wid * camera.zoom))

                cos_a = math.cos(w_ang)
                sin_a = math.sin(w_ang)

                hl = scaled_l / 2.0
                hw = scaled_w / 2.0

                local_corners = [(-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)]
                screen_pts = []
                for lx, ly in local_corners:
                    px = sx + lx * cos_a - ly * sin_a
                    py = sy + lx * sin_a + ly * cos_a
                    screen_pts.append((px, py))

                pygame.draw.polygon(surface, (120, 75, 30), screen_pts)
                pygame.draw.polygon(surface, (195, 135, 60), screen_pts, width=max(1, int(2 * camera.zoom)))

                # Inner log ridge lines for wooden palisade texture
                p1_mid = ((screen_pts[0][0] + screen_pts[3][0]) / 2.0, (screen_pts[0][1] + screen_pts[3][1]) / 2.0)
                p2_mid = ((screen_pts[1][0] + screen_pts[2][0]) / 2.0, (screen_pts[1][1] + screen_pts[2][1]) / 2.0)
                pygame.draw.line(surface, (80, 45, 20), p1_mid, p2_mid, max(1, int(2 * camera.zoom)))

            elif b_type == "WoodStockpile":
                # Lumber Storage Yard
                pygame.draw.rect(surface, (90, 55, 25), rect, border_radius=4)
                # Stacked Timber Logs
                for row in range(-1, 2):
                    ly = sy + row * (radius // 2)
                    pygame.draw.line(surface, (160, 100, 45), (sx - radius + 5, ly), (sx + radius - 5, ly), 5)
                    pygame.draw.circle(surface, (210, 150, 80), (sx - radius + 5, ly), 3)
                    pygame.draw.circle(surface, (210, 150, 80), (sx + radius - 5, ly), 3)

            elif b_type == "GoldStockpile":
                # Treasury Vault & Gold Chest
                pygame.draw.rect(surface, (60, 65, 75), rect, border_radius=4)
                pygame.draw.rect(surface, (255, 215, 0), rect, width=2, border_radius=4)
                # Open Chest full of Gold
                chest_rect = pygame.Rect(sx - radius//2, sy - radius//3, radius, radius * 2 // 3)
                pygame.draw.rect(surface, (139, 69, 19), chest_rect, border_radius=2)
                pygame.draw.circle(surface, (255, 215, 0), (sx - 4, sy - 2), 5)
                pygame.draw.circle(surface, (255, 223, 0), (sx + 4, sy - 2), 6)
                pygame.draw.circle(surface, (255, 250, 205), (sx, sy - 6), 4)

            elif b_type == "House":
                # Medieval Cottage / House (Timber wall, Thatched Roof, Window & Door)
                pygame.draw.rect(surface, (140, 100, 60), rect, border_radius=4)
                pygame.draw.rect(surface, (200, 150, 90), rect, width=2, border_radius=4)
                # Thatched Triangular Roof
                roof_pts = [(sx - radius - 4, sy - radius // 4), (sx, sy - radius - 8), (sx + radius + 4, sy - radius // 4)]
                pygame.draw.polygon(surface, (180, 140, 60), roof_pts)
                pygame.draw.polygon(surface, (220, 180, 80), roof_pts, width=2)
                # Wooden Door
                door_w, door_h = max(4, radius // 2), max(6, radius * 2 // 3)
                pygame.draw.rect(surface, (80, 50, 20), (sx - door_w//2, sy + radius - door_h, door_w, door_h))
                # Glowing Window
                pygame.draw.rect(surface, (255, 215, 0), (sx - radius//2, sy - radius//4, max(4, radius//3), max(4, radius//3)))

            elif b_type == "Farm":
                # Medieval Farmhouse & Grain Field
                pygame.draw.rect(surface, (130, 90, 45), rect, border_radius=4)
                # Crops Patch (Wheat rows)
                for i in range(-2, 3):
                    pygame.draw.line(surface, (218, 165, 32), (sx - radius + 6, sy + i * 5), (sx + radius - 6, sy + i * 5), 3)
                # Small Thatched Barn
                barn_rect = pygame.Rect(sx - radius//3, sy - radius + 4, radius * 2 // 3, radius * 2 // 3)
                pygame.draw.rect(surface, (100, 60, 30), barn_rect, border_radius=2)
                pygame.draw.polygon(surface, (200, 170, 80), [(sx - radius//3 - 2, sy - radius//3), (sx, sy - radius - 4), (sx + radius//3 + 2, sy - radius//3)])

        else:
            # --- ALIEN INSECT FACTION ---
            if b_type == "Hive":
                # Organic Pulsing Hatchery Hive
                import math
                pulse = math.sin(building.anim_time * 4) * 2 if hasattr(building, 'anim_time') else 0

                # Organic creep base
                pygame.draw.ellipse(surface, (74, 20, 140), (sx - radius - 6, sy - radius - 4, radius*2 + 12, radius*2 + 8))
                # Hive Main Egg Chamber
                pygame.draw.ellipse(surface, (142, 36, 170), (sx - radius + pulse, sy - radius, radius*2 - pulse*2, radius*2))
                pygame.draw.ellipse(surface, (216, 27, 96), (sx - radius + pulse, sy - radius, radius*2 - pulse*2, radius*2), width=3)

                # Glowing Bio Vents / Spore Sacs
                for angle in [0, 1.2, 2.4, 3.6, 4.8]:
                    vx = sx + int(math.cos(angle) * radius * 0.6)
                    vy = sy + int(math.sin(angle) * radius * 0.6)
                    pygame.draw.circle(surface, (0, 230, 118), (vx, vy), max(3, radius // 5))
                    pygame.draw.circle(surface, (255, 235, 59), (vx, vy), max(1, radius // 8))

            elif b_type == "SpawningPool":
                # Glowing Acid Spawning Pool
                # Chitin Ring
                pygame.draw.circle(surface, (60, 15, 90), (sx, sy), radius)
                pygame.draw.circle(surface, (180, 20, 80), (sx, sy), radius, width=3)
                # Corrosive Liquid Surface
                pygame.draw.circle(surface, (0, 200, 83), (sx, sy), int(radius * 0.75))
                pygame.draw.circle(surface, (178, 255, 89), (sx - radius//4, sy - radius//4), int(radius * 0.35))
                # Bubbling Alien Eggs
                pygame.draw.circle(surface, (216, 27, 96), (sx + radius//3, sy + radius//4), max(2, radius//5))
                pygame.draw.circle(surface, (216, 27, 96), (sx - radius//3, sy + radius//3), max(2, radius//6))

            elif b_type == "SpineCrawler":
                # Living Defense Needle Spine Crawler
                # Rooted Creep Pod
                pygame.draw.circle(surface, (100, 15, 60), (sx, sy), radius)
                pygame.draw.circle(surface, (216, 27, 96), (sx, sy), radius, width=2)

                # Giant Sharp Bone Spine / Spike Cannon
                spine_pts = [
                    (sx, sy - radius - 10),
                    (sx + radius // 2 + 2, sy + radius // 2),
                    (sx - radius // 2 - 2, sy + radius // 2)
                ]
                pygame.draw.polygon(surface, (240, 240, 220), spine_pts)
                pygame.draw.polygon(surface, (216, 27, 96), spine_pts, width=2)
                # Glowing Eye/Core
                pygame.draw.circle(surface, (255, 235, 59), (sx, sy - 2), max(3, radius // 4))

            elif b_type == "BiomassGenerator":
                # Bio-reactor Organic Generator
                pygame.draw.circle(surface, (40, 90, 40), (sx, sy), radius)
                pygame.draw.circle(surface, (76, 175, 80), (sx, sy), radius, width=2)
                pygame.draw.circle(surface, (0, 230, 118), (sx, sy), int(radius * 0.6))
                pygame.draw.circle(surface, (255, 255, 255), (sx - radius//3, sy - radius//3), int(radius * 0.2))

        # Visual overlay for building under construction
        if not building.is_constructed:
            # Semi-transparent scaffolding grid / outline
            scaff_surface = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.rect(scaff_surface, (255, 200, 50, 120), (4, 4, radius * 2, radius * 2), width=3)
            # Scaffolding cross-beams
            pygame.draw.line(scaff_surface, (180, 120, 40, 150), (4, 4), (radius * 2 + 4, radius * 2 + 4), 2)
            pygame.draw.line(scaff_surface, (180, 120, 40, 150), (radius * 2 + 4, 4), (4, radius * 2 + 4), 2)
            surface.blit(scaff_surface, (sx - radius - 4, sy - radius - 4))

            ratio = 1.0 - (building.build_timer / max(0.001, building.total_build_time))
            bw = radius * 2
            bh = 6
            pygame.draw.rect(surface, (30, 30, 35), (sx - radius, sy + radius + 4, bw, bh), border_radius=2)
            pygame.draw.rect(surface, (255, 179, 0), (sx - radius, sy + radius + 4, int(bw * ratio), bh), border_radius=2)

    @staticmethod
    def _draw_unit(surface, camera, unit, sx, sy, radius):
        u_type = unit.unit_type
        faction = unit.faction
        facing = getattr(unit, 'facing_angle', 0.0)

        import math

        if faction == config.FACTION_HUMAN:
            # --- MEDIEVAL HUMANS ---
            if u_type == "Worker":
                # Medieval Peasant Worker (Blue-grey tunic, Straw Hat, Hoe)
                pygame.draw.circle(surface, (40, 120, 180), (sx, sy), radius)
                pygame.draw.circle(surface, (240, 200, 110), (sx, sy), radius - 2)
                pygame.draw.circle(surface, (190, 140, 70), (sx, sy), radius - 6)
                hx = sx + int(math.cos(facing) * (radius + 4))
                hy = sy + int(math.sin(facing) * (radius + 4))
                pygame.draw.line(surface, (110, 75, 35), (sx, sy), (hx, hy), 3)
                pygame.draw.circle(surface, (200, 200, 210), (hx, hy), 3)

            elif u_type == "Scout":
                # Medieval Scout (Bright Cyan/Turquoise Tunic, Feathered Cap)
                pygame.draw.circle(surface, (0, 220, 220), (sx, sy), radius)
                pygame.draw.circle(surface, (255, 235, 59), (sx, sy), radius - 4)
                # Feather Cap & Spyglass
                pygame.draw.line(surface, (255, 80, 80), (sx, sy), (sx - 4, sy - radius - 3), 2)
                sg_x = sx + int(math.cos(facing) * (radius + 6))
                sg_y = sy + int(math.sin(facing) * (radius + 6))
                pygame.draw.line(surface, (255, 215, 0), (sx, sy), (sg_x, sg_y), 3)

            elif u_type == "Infantry":
                # Medieval Knight Infantry (Bright Royal Blue Tunic, Steel Helmet, Sword)
                pygame.draw.circle(surface, (20, 100, 230), (sx, sy), radius)
                pygame.draw.circle(surface, (210, 220, 235), (sx, sy), radius - 3)
                pygame.draw.line(surface, (40, 40, 50), (sx - radius + 4, sy), (sx + radius - 4, sy), 2)

                sw_x = sx + int(math.cos(facing) * (radius + 8))
                sw_y = sy + int(math.sin(facing) * (radius + 8))
                pygame.draw.line(surface, (250, 250, 255), (sx, sy), (sw_x, sw_y), 3)
                gx = sx + int(math.cos(facing) * radius)
                gy = sy + int(math.sin(facing) * radius)
                pygame.draw.circle(surface, (255, 215, 0), (gx, gy), 3)

            elif u_type == "Archer":
                # Medieval Archer (Forest Green Hood, Longbow)
                pygame.draw.circle(surface, (30, 160, 60), (sx, sy), radius)
                pygame.draw.circle(surface, (20, 100, 40), (sx, sy), radius - 4)
                pygame.draw.line(surface, (230, 40, 40), (sx, sy), (sx - 4, sy - radius - 3), 2)

                bx = sx + int(math.cos(facing) * radius)
                by = sy + int(math.sin(facing) * radius)
                pygame.draw.circle(surface, (139, 69, 19), (bx, by), 5, width=2)

        else:
            # --- ALIEN INSECT FACTION ---
            if u_type == "Drone":
                # Alien Insect Drone Worker (Bright Orange/Yellow Carapace)
                pygame.draw.circle(surface, (255, 110, 0), (sx, sy), radius)
                pygame.draw.circle(surface, (200, 70, 0), (sx, sy), radius - 3)

                mx = sx + int(math.cos(facing) * (radius + 5))
                my = sy + int(math.sin(facing) * (radius + 5))
                pygame.draw.line(surface, (255, 230, 0), (sx, sy), (mx, my), 2)

                for leg_a in [facing + 1.0, facing - 1.0, facing + 2.2, facing - 2.2]:
                    lx = sx + int(math.cos(leg_a) * (radius + 4))
                    ly = sy + int(math.sin(leg_a) * (radius + 4))
                    pygame.draw.line(surface, (180, 50, 0), (sx, sy), (lx, ly), 2)

            elif u_type == "Swarmer":
                # Crimson Red Swarmer Melee (Blood Red Chitin Diamond & Yellow Claws)
                cos_f = math.cos(facing)
                sin_f = math.sin(facing)

                head = (sx + int(cos_f * (radius + 6)), sy + int(sin_f * (radius + 6)))
                tail = (sx - int(cos_f * (radius + 2)), sy - int(sin_f * (radius + 2)))
                left_wing = (sx + int(math.cos(facing + 1.8) * (radius + 3)), sy + int(math.sin(facing + 1.8) * (radius + 3)))
                right_wing = (sx + int(math.cos(facing - 1.8) * (radius + 3)), sy + int(math.sin(facing - 1.8) * (radius + 3)))

                pts = [head, left_wing, tail, right_wing]
                pygame.draw.polygon(surface, (200, 15, 45), pts)
                pygame.draw.polygon(surface, (255, 220, 0), pts, width=2)

                pygame.draw.line(surface, (255, 255, 255), head, (head[0] + int(cos_f * 5), head[1] + int(sin_f * 5)), 2)

            elif u_type == "Spitter":
                # Toxic Lime Green Spitter Ranged (Bright Acid Green & Purple Sac)
                cos_f = math.cos(facing)
                sin_f = math.sin(facing)

                sac_x = sx - int(cos_f * (radius + 2))
                sac_y = sy - int(sin_f * (radius + 2))
                pygame.draw.circle(surface, (180, 30, 200), (sac_x, sac_y), max(3, radius - 2))

                p1 = (sx + int(cos_f * (radius + 6)), sy + int(sin_f * (radius + 6)))
                p2 = (sx + int(math.cos(facing + 2.2) * radius), sy + int(math.sin(facing + 2.2) * radius))
                p3 = (sx + int(math.cos(facing - 2.2) * radius), sy + int(math.sin(facing - 2.2) * radius))
                pygame.draw.polygon(surface, (50, 230, 50), [p1, p2, p3])
                pygame.draw.polygon(surface, (220, 255, 0), [p1, p2, p3], width=2)

        # Attack visual animations (Arrow / Spore Stream)
        if unit.is_attacking_anim > 0 and unit.target_entity:
            t_pos = camera.world_to_screen((unit.target_entity.x, unit.target_entity.y))
            if unit.unit_type in ["Archer", "Spitter"]:
                p_color = (255, 235, 59) if unit.unit_type == "Archer" else (0, 255, 128)
                pygame.draw.line(surface, p_color, (sx, sy), (int(t_pos[0]), int(t_pos[1])), 3)
            else:
                pygame.draw.circle(surface, (255, 50, 50), (int(t_pos[0]), int(t_pos[1])), radius + 5, 2)

        # Harvesting visual animation line
        if unit.is_harvesting_anim > 0 and unit.target_entity:
            t_pos = camera.world_to_screen((unit.target_entity.x, unit.target_entity.y))
            pygame.draw.line(surface, (255, 215, 0), (sx, sy), (int(t_pos[0]), int(t_pos[1])), 1)

        # Carried resource icon badge
        if unit.carried_resource > 0:
            c_color = (255, 215, 0) if unit.resource_type == "gold" else ((139, 69, 19) if unit.resource_type == "wood" else (76, 175, 80))
            pygame.draw.circle(surface, c_color, (sx, sy - radius - 5), max(3, radius // 3))
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy - radius - 5), max(3, radius // 3), width=1)
