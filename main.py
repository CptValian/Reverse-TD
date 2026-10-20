import sys
import math
import pygame
import config
from src.engine.camera import Camera
from src.engine.game_state import GameState
from src.progression.save_manager import SaveManager
from src.progression.progression_tree import ProgressionUI
from src.ui.hud import HUD
from src.ui.menu import Menu
from src.ui.render_utils import RenderUtils
from src.entities.building import Building

def main():
    pygame.init()
    info = pygame.display.Info()
    if info.current_w > 0 and info.current_h > 0:
        config.SCREEN_WIDTH = info.current_w
        config.SCREEN_HEIGHT = info.current_h

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("RTS: Médiéval vs Alien Insecte")
    clock = pygame.time.Clock()

    save_manager = SaveManager()
    game_state = GameState(save_manager)
    camera = Camera(screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT)
    hud = HUD(screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT)
    menu = Menu(screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT)
    progression_ui = ProgressionUI(save_manager, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT)

    is_selecting_box = False
    box_start_pos = (0, 0)
    is_attack_move_pending = False

    # Placement de bâtiment & Murs
    placement_building_type = None
    wall_start_node = None  # (wx, wy) world coords if wall placement started

    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0  # Temps en secondes
        mouse_pos = pygame.mouse.get_pos()

        # -------------------------------------------------------------
        # 1. GESTION DES ÉVÉNEMENTS
        # -------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif game_state.state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = menu.draw_main_menu(screen, game_state.num_ais, game_state.ai_difficulty, game_state.map_type)
                    if buttons["start"].collidepoint(event.pos):
                        game_state.start_new_game()
                        # Positionner la caméra sur le spawn du joueur humanoïde
                        player_base = next((b for b in game_state.buildings if b.owner_id == 0), None)
                        if player_base:
                            camera.x = player_base.x - config.SCREEN_WIDTH / 2
                            camera.y = player_base.y - config.SCREEN_HEIGHT / 2
                            camera.clamp()

                    elif buttons["skill_tree"].collidepoint(event.pos):
                        game_state.state = "SKILL_TREE"

                    elif buttons.get("ai_info") and buttons["ai_info"].collidepoint(event.pos):
                        game_state.state = "AI_INFO"

                    elif buttons.get("ai_minus") and buttons["ai_minus"].collidepoint(event.pos):
                        game_state.num_ais = max(1, game_state.num_ais - 1)

                    elif buttons.get("ai_plus") and buttons["ai_plus"].collidepoint(event.pos):
                        game_state.num_ais = min(4, game_state.num_ais + 1)

                    elif buttons.get("difficulty") and buttons["difficulty"].collidepoint(event.pos):
                        diffs = list(range(1, 11))
                        curr_idx = diffs.index(game_state.ai_difficulty) if game_state.ai_difficulty in diffs else 0
                        game_state.ai_difficulty = diffs[(curr_idx + 1) % len(diffs)]

                    elif buttons.get("map_type") and buttons["map_type"].collidepoint(event.pos):
                        m_types = [1, 2, 3]
                        curr_m_idx = m_types.index(game_state.map_type) if game_state.map_type in m_types else 0
                        game_state.map_type = m_types[(curr_m_idx + 1) % len(m_types)]

                    elif buttons["quit"].collidepoint(event.pos):
                        running = False

            elif game_state.state == "AI_INFO":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        buttons = menu.draw_ai_info_screen(screen, getattr(menu, 'ai_info_scroll_y', 0))
                        if buttons.get("back") and buttons["back"].collidepoint(event.pos):
                            game_state.state = "MENU"
                            menu.ai_info_scroll_y = 0
                    elif event.button == 4:  # Scroll Up
                        menu.ai_info_scroll_y = max(0, getattr(menu, 'ai_info_scroll_y', 0) - 40)
                    elif event.button == 5:  # Scroll Down
                        buttons = menu.draw_ai_info_screen(screen, getattr(menu, 'ai_info_scroll_y', 0))
                        max_s = buttons.get("max_scroll", 1000)
                        menu.ai_info_scroll_y = min(max_s, getattr(menu, 'ai_info_scroll_y', 0) + 40)

            elif game_state.state == "SKILL_TREE":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [1, 2, 3]:
                        buttons = progression_ui.draw(screen)
                        clicked_button = False

                        if event.button == 1:
                            if buttons.get("back") and buttons["back"].collidepoint(event.pos):
                                game_state.state = "MENU"
                                clicked_button = True
                            elif buttons.get("tab_tree") and buttons["tab_tree"].collidepoint(event.pos):
                                progression_ui.active_tab = "skill_tree"
                                clicked_button = True
                            elif buttons.get("tab_troops") and buttons["tab_troops"].collidepoint(event.pos):
                                progression_ui.active_tab = "troops"
                                clicked_button = True
                            elif buttons.get("tab_buildings") and buttons["tab_buildings"].collidepoint(event.pos):
                                progression_ui.active_tab = "buildings"
                                clicked_button = True
                            else:
                                for key, info in buttons.items():
                                    if key not in ["back", "tab_tree", "tab_troops", "tab_buildings"] and isinstance(info, dict) and info.get("rect") and info["rect"].collidepoint(event.pos):
                                        save_manager.buy_upgrade(
                                            key,
                                            info["type"],
                                            cost=info.get("cost"),
                                            cost_base=info.get("cost_base", 10),
                                            is_tree_unlock=info.get("is_tree_unlock", False)
                                        )
                                        clicked_button = True
                                        break

                        # Panning drag start if not clicking UI buttons
                        if not clicked_button:
                            progression_ui.is_dragging = True
                            progression_ui.drag_start_pos = event.pos

                    elif event.button == 4:  # Scroll UP
                        progression_ui.camera_offset_y += 30
                    elif event.button == 5:  # Scroll DOWN
                        progression_ui.camera_offset_y -= 30

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button in [1, 2, 3]:
                        progression_ui.is_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if progression_ui.is_dragging:
                        dx = event.pos[0] - progression_ui.drag_start_pos[0]
                        dy = event.pos[1] - progression_ui.drag_start_pos[1]
                        progression_ui.camera_offset_x += dx
                        progression_ui.camera_offset_y += dy
                        progression_ui.drag_start_pos = event.pos

            elif game_state.state in ["VICTORY", "DEFEAT"]:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    game_state.state = "MENU"

            elif game_state.state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        # Activer le mode attente "A + Click"
                        is_attack_move_pending = True
                    elif event.key == pygame.K_ESCAPE:
                        placement_building_type = None
                        wall_start_node = None
                        is_attack_move_pending = False

                # Zoom molette
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Molette haut
                        camera.handle_zoom(True, mouse_pos)
                    elif event.button == 5:  # Molette bas
                        camera.handle_zoom(False, mouse_pos)

                    elif event.button == 3:  # Clic droit : Annuler mode placement ou donner ordres
                        if placement_building_type:
                            placement_building_type = None
                            wall_start_node = None
                        else:
                            world_click = camera.screen_to_world(mouse_pos)
                            selected_units = [u for u in game_state.units if u.selected and u.owner_id == 0]
                            selected_buildings = [b for b in game_state.buildings if b.selected and b.owner_id == 0 and b.trainable_units]

                            target_enemy = next((e for e in game_state.units + game_state.buildings if e.alive and e.owner_id != 0 and e.is_point_inside(world_click[0], world_click[1])), None)
                            target_res = next((r for r in game_state.resources if r.alive and r.is_point_inside(world_click[0], world_click[1])), None)
                            target_farm = next((b for b in game_state.buildings if b.alive and getattr(b, 'building_type', None) == "Farm" and b.is_point_inside(world_click[0], world_click[1])), None)
                            target_th = next((b for b in game_state.buildings if b.alive and getattr(b, 'building_type', None) == "TownHall" and b.owner_id == 0 and b.is_point_inside(world_click[0], world_click[1])), None)

                            if selected_units:
                                upgrades = game_state.save_manager.data.get("upgrades", {})
                                for unit in selected_units:
                                    if target_enemy:
                                        unit.attack_target(target_enemy)
                                    elif target_res and unit.is_worker:
                                        unit.harvest_node(target_res)
                                    elif target_farm and unit.is_worker:
                                        unit.harvest_node(target_farm)
                                    elif target_th and unit.is_worker and upgrades.get("garrison_unlocked"):
                                        if target_th.garrison_unit(unit):
                                            pass
                                    else:
                                        unit.move_to(world_click[0], world_click[1])

                            elif selected_buildings:
                                # Définir le point de ralliement (Rally Point) pour les bâtiments de production
                                target_obj = target_res or target_farm or target_enemy
                                for bld in selected_buildings:
                                    bld.rally_point = (world_click[0], world_click[1])
                                    bld.rally_target = target_obj

                    elif event.button == 1:  # Clic gauche (Sélection / Interaction UI)
                        minimap_size = 150
                        minimap_rect = pygame.Rect(10, config.SCREEN_HEIGHT - minimap_size - 10, minimap_size, minimap_size)

                        if placement_building_type:
                            world_click = camera.screen_to_world(mouse_pos)
                            from src.entities.building import BUILDING_TYPES
                            b_data = BUILDING_TYPES.get(placement_building_type, {})
                            cost = b_data.get("cost", {})
                            upgrades = game_state.save_manager.data.get("upgrades", {})

                            if placement_building_type == "Wall":
                                # Snap check to existing wall building
                                snap_node = None
                                for b in game_state.buildings:
                                    if b.alive and b.building_type == "Wall":
                                        if math.hypot(b.x - world_click[0], b.y - world_click[1]) < 35:
                                            snap_node = (b.x, b.y)
                                            break

                                if wall_start_node is None:
                                    wall_start_node = snap_node if snap_node else world_click
                                else:
                                    # P2 point selected
                                    p1 = wall_start_node
                                    p2 = snap_node if snap_node else world_click
                                    dx = p2[0] - p1[0]
                                    dy = p2[1] - p1[1]
                                    length = math.hypot(dx, dy)

                                    if length >= 15:
                                        seg_spacing = 40.0
                                        num_segs = max(1, int(round(length / seg_spacing)))
                                        unit_cost_wood = cost.get("wood", 30)
                                        total_wall_cost = {"wood": unit_cost_wood * num_segs}
                                        wall_angle = math.atan2(dy, dx)

                                        if game_state.deduct_resources(0, total_wall_cost):
                                            for step_i in range(num_segs):
                                                r1 = step_i / float(num_segs)
                                                r2 = (step_i + 1) / float(num_segs)
                                                x1 = p1[0] + dx * r1
                                                y1 = p1[1] + dy * r1
                                                x2 = p1[0] + dx * r2
                                                y2 = p1[1] + dy * r2

                                                cx = (x1 + x2) / 2.0
                                                cy = (y1 + y2) / 2.0
                                                seg_len = math.hypot(x2 - x1, y2 - y1)

                                                if game_state.can_place_building("Wall", cx, cy):
                                                    nb = Building(
                                                        0, config.FACTION_HUMAN, "Wall", cx, cy,
                                                        is_constructed=False,
                                                        wall_length=seg_len + 6.0,
                                                        wall_width=18,
                                                        wall_angle=wall_angle
                                                    )
                                                    game_state.buildings.append(nb)

                                    placement_building_type = None
                                    wall_start_node = None

                            else:
                                # Regular building placement
                                if game_state.can_place_building(placement_building_type, world_click[0], world_click[1]):
                                    if game_state.deduct_resources(0, cost):
                                        range_bonus = 20 if (placement_building_type == "Tower" and upgrades.get("tower_range_unlocked")) else 0
                                        nb = Building(0, config.FACTION_HUMAN, placement_building_type, world_click[0], world_click[1], is_constructed=False, range_bonus=range_bonus)
                                        game_state.buildings.append(nb)
                                        placement_building_type = None

                        elif minimap_rect.collidepoint(mouse_pos):
                            # Clic sur la mini-carte : Déplacer la vision de la caméra
                            rel_x = (mouse_pos[0] - minimap_rect.x) / minimap_size
                            rel_y = (mouse_pos[1] - minimap_rect.y) / minimap_size
                            world_x = rel_x * config.MAP_WIDTH
                            world_y = rel_y * config.MAP_HEIGHT

                            camera.x = world_x - (config.SCREEN_WIDTH / (2 * camera.zoom))
                            camera.y = world_y - (config.SCREEN_HEIGHT / (2 * camera.zoom))
                            camera.clamp()

                        # Vérifier clic sur l'UI (Zone HUD)
                        elif mouse_pos[1] > config.SCREEN_HEIGHT - 150:
                            # Clic dans le panneau HUD pour lancer un entraînement/construction/age up
                            selected_entities = [e for e in game_state.units + game_state.buildings if e.selected and e.owner_id == 0]
                            if selected_entities:
                                first = selected_entities[0]
                                upgrades = game_state.save_manager.data.get("upgrades", {})

                                if getattr(first, 'building_type', None) == "TownHall":
                                    minimap_size = 150
                                    panel_x = minimap_size + 30
                                    panel_y = config.SCREEN_HEIGHT - 150

                                    if upgrades.get("garrison_unlocked"):
                                        ungarr_btn = pygame.Rect(panel_x + 460, panel_y + 8, 80, 26)
                                        if ungarr_btn.collidepoint(event.pos):
                                            first.ungarrison_all(game_state)

                                    next_age = game_state.player_age + 1
                                    if upgrades.get(f"ageing_up_{next_age}"):
                                        age_btn = pygame.Rect(panel_x + 550, panel_y + 8, 220, 32)
                                        if age_btn.collidepoint(event.pos):
                                            cost_wood = 200 * next_age
                                            cost_gold = 200 * next_age
                                            req = {"wood": cost_wood, "gold": cost_gold}
                                            if game_state.deduct_resources(0, req):
                                                game_state.age_up(0)

                                if hasattr(first, 'building_type') and first.trainable_units:
                                    trainable = []
                                    for u in first.trainable_units:
                                        if u == "Archer" and not upgrades.get("archer_unlocked"):
                                            continue
                                        trainable.append(u)

                                    panel_x = 180
                                    btn_x = panel_x + 20
                                    from src.entities.unit import UNIT_TYPES
                                    for u_type in trainable:
                                        btn_rect = pygame.Rect(btn_x, config.SCREEN_HEIGHT - 100, 160, 42)
                                        if btn_rect.collidepoint(event.pos):
                                            # Check pop limit
                                            if game_state.get_queued_and_current_pop(0) < game_state.get_pop_max(0):
                                                u_data = UNIT_TYPES.get(u_type, {})
                                                cost = u_data.get("cost", {"gold": 50})
                                                if game_state.deduct_resources(0, cost):
                                                    first.queue_unit(u_type, train_time=u_data.get("train_time", 5))
                                        btn_x += 170

                                elif getattr(first, 'is_worker', False):
                                    panel_x = 180
                                    btn_x = panel_x + 10
                                    if first.faction == config.FACTION_HUMAN:
                                        buildings_to_build = ["Barracks"]
                                        if upgrades.get("wall_unlocked"):
                                            buildings_to_build.append("Wall")
                                        if upgrades.get("tower_unlocked"):
                                            buildings_to_build.append("Tower")
                                        if upgrades.get("wood_stockpile_unlocked"):
                                            buildings_to_build.append("WoodStockpile")
                                        if upgrades.get("gold_stockpile_unlocked"):
                                            buildings_to_build.append("GoldStockpile")
                                        if upgrades.get("house_unlocked"):
                                            buildings_to_build.append("House")
                                        if upgrades.get("farm_unlocked"):
                                            buildings_to_build.append("Farm")
                                        if upgrades.get("townhall_unlocked") and getattr(game_state, 'player_age', 1) >= 2:
                                            buildings_to_build.append("TownHall")
                                    else:
                                        buildings_to_build = ["SpawningPool", "SpineCrawler"]

                                    for b_type in buildings_to_build:
                                        btn_width = 125
                                        btn_rect = pygame.Rect(btn_x, config.SCREEN_HEIGHT - 110, btn_width, 45)
                                        if btn_rect.collidepoint(event.pos):
                                            placement_building_type = b_type
                                            wall_start_node = None
                                        btn_x += btn_width + 8

                        else:
                            # Clic dans la zone de jeu
                            world_click = camera.screen_to_world(mouse_pos)

                            if is_attack_move_pending:
                                is_attack_move_pending = False
                                selected_units = [u for u in game_state.units if u.selected and u.owner_id == 0]
                                for unit in selected_units:
                                    unit.attack_move_to(world_click[0], world_click[1])
                            else:
                                is_selecting_box = True
                                box_start_pos = mouse_pos

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_selecting_box:
                    is_selecting_box = False
                    box_end_pos = mouse_pos

                    # Réaliser la sélection (rectangle ou simple clic)
                    x1, y1 = camera.screen_to_world(box_start_pos)
                    x2, y2 = camera.screen_to_world(box_end_pos)

                    rect_w = abs(x2 - x1)
                    rect_h = abs(y2 - y1)

                    # Désélectionner toutes les entités
                    for e in game_state.units + game_state.buildings:
                        e.selected = False

                    if rect_w < 10 and rect_h < 10:
                        # Simple clic (Allows clicking player or enemy entities)
                        clicked_entity = next((e for e in game_state.units + game_state.buildings if e.alive and e.is_point_inside(x2, y2)), None)
                        if clicked_entity:
                            clicked_entity.selected = True
                    else:
                        # Sélection par cadre (Box select selects player units only)
                        rx = min(x1, x2)
                        ry = min(y1, y2)
                        for u in game_state.units:
                            if u.alive and u.owner_id == 0 and u.is_in_rect(rx, ry, rect_w, rect_h):
                                u.selected = True

        # -------------------------------------------------------------
        # 2. MISE À JOUR ET RENDU DU JEU
        # -------------------------------------------------------------
        if game_state.state == "MENU":
            menu.draw_main_menu(screen, game_state.num_ais, game_state.ai_difficulty, game_state.map_type)

        elif game_state.state == "AI_INFO":
            menu.draw_ai_info_screen(screen, menu.ai_info_scroll_y)

        elif game_state.state == "SKILL_TREE":
            progression_ui.draw(screen)

        elif game_state.state == "PLAYING":
            # Déplacement caméra
            keys = pygame.key.get_pressed()
            camera.update(dt, keys, mouse_pos)

            # Mise à jour du monde
            game_state.update(dt)

            # Rendu du terrain
            screen.fill(config.COLOR_BG)

            # Dessiner le fond de carte (Grille simple)
            visible_rect = camera.get_visible_rect()
            grid_size = 200
            start_x = int((visible_rect.x // grid_size) * grid_size)
            end_x = int(visible_rect.x + visible_rect.width)
            start_y = int((visible_rect.y // grid_size) * grid_size)
            end_y = int(visible_rect.y + visible_rect.height)

            for gx in range(start_x, end_x, grid_size):
                for gy in range(start_y, end_y, grid_size):
                    sp = camera.world_to_screen((gx, gy))
                    pygame.draw.rect(screen, (40, 48, 58), (sp[0], sp[1], grid_size * camera.zoom, grid_size * camera.zoom), 1)

            # Attacher temporairement game_state à camera pour les vérifications de visibilité Fog of War
            camera.game_state = game_state

            # Dessiner les ressources, bâtiments et unités
            for res in game_state.resources:
                RenderUtils.draw_entity(screen, camera, res)
            for building in game_state.buildings:
                RenderUtils.draw_entity(screen, camera, building)
            for unit in game_state.units:
                RenderUtils.draw_entity(screen, camera, unit)

            # Dessiner le calque de brouillard de guerre si actif
            if game_state.is_fog_of_war_enabled():
                fog_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
                fog_surface.fill((10, 12, 18, 180))  # Voile sombre semi-transparent

                # Découper des cercles de vision autour des entités du joueur
                player_entities = [e for e in game_state.units + game_state.buildings if e.alive and e.owner_id == 0]
                for pe in player_entities:
                    sp = camera.world_to_screen((pe.x, pe.y))
                    vis_r = int(getattr(pe, 'vision_radius', 220) * camera.zoom)
                    pygame.draw.circle(fog_surface, (0, 0, 0, 0), (int(sp[0]), int(sp[1])), vis_r)

                screen.blit(fog_surface, (0, 0))

            # Preview placement ghost cursor
            if placement_building_type:
                world_cur = camera.screen_to_world(mouse_pos)
                if placement_building_type == "Wall":
                    if wall_start_node is not None:
                        sp1 = camera.world_to_screen(wall_start_node)
                        sp2 = mouse_pos
                        pygame.draw.line(screen, (255, 215, 0), sp1, sp2, 4)
                        pygame.draw.circle(screen, (0, 255, 255), sp1, 8, 2)
                        pygame.draw.circle(screen, (0, 255, 255), sp2, 8, 2)
                    else:
                        # Draw snap node highlight if hovering near existing wall
                        snap_node = None
                        for b in game_state.buildings:
                            if b.alive and b.building_type == "Wall":
                                if math.hypot(b.x - world_cur[0], b.y - world_cur[1]) < 35:
                                    snap_node = (b.x, b.y)
                                    break
                        if snap_node:
                            snp_sp = camera.world_to_screen(snap_node)
                            pygame.draw.circle(screen, (0, 255, 0), snp_sp, 12, 3)
                        else:
                            pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 8, 2)
                else:
                    can_place = game_state.can_place_building(placement_building_type, world_cur[0], world_cur[1])
                    color = (0, 255, 0) if can_place else (255, 0, 0)
                    from src.entities.building import BUILDING_TYPES
                    bradius = int(BUILDING_TYPES.get(placement_building_type, {}).get("radius", 30) * camera.zoom)
                    pygame.draw.circle(screen, color, mouse_pos, bradius, 2)

            # Dessiner le cadre de sélection en cours
            if is_selecting_box:
                x1, y1 = box_start_pos
                x2, y2 = mouse_pos
                pygame.draw.rect(screen, config.COLOR_SELECTION, (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)), 1)

            # HUD
            hud.draw(screen, game_state, camera)

        elif game_state.state == "VICTORY":
            screen.fill((20, 60, 20))
            txt = menu.title_font.render("GLORIOUS VICTORY!", True, (100, 255, 100))
            screen.blit(txt, (config.SCREEN_WIDTH // 2 - txt.get_width() // 2, 300))

            p_res = game_state.resources_gathered_player.get(0, {})
            res_str = f"Ressources obtenues - Or: {int(p_res.get('gold', 0))} | Bois: {int(p_res.get('wood', 0))} | Nourriture: {int(p_res.get('food', 0))} | Biomasse: {int(p_res.get('biomass', 0))}"
            res_txt = menu.font.render(res_str, True, (255, 215, 0))
            screen.blit(res_txt, (config.SCREEN_WIDTH // 2 - res_txt.get_width() // 2, 400))

            sub = menu.font.render("Progression reward points earned. Click to return to Menu.", True, (255, 255, 255))
            screen.blit(sub, (config.SCREEN_WIDTH // 2 - sub.get_width() // 2, 480))

        elif game_state.state == "DEFEAT":
            screen.fill((60, 20, 20))
            txt = menu.title_font.render("DEFEAT...", True, (255, 100, 100))
            screen.blit(txt, (config.SCREEN_WIDTH // 2 - txt.get_width() // 2, 300))

            p_res = game_state.resources_gathered_player.get(0, {})
            res_str = f"Ressources obtenues - Or: {int(p_res.get('gold', 0))} | Bois: {int(p_res.get('wood', 0))} | Nourriture: {int(p_res.get('food', 0))} | Biomasse: {int(p_res.get('biomass', 0))}"
            res_txt = menu.font.render(res_str, True, (255, 215, 0))
            screen.blit(res_txt, (config.SCREEN_WIDTH // 2 - res_txt.get_width() // 2, 400))

            sub = menu.font.render("Your defenses have fallen. Click to return to Menu.", True, (255, 255, 255))
            screen.blit(sub, (config.SCREEN_WIDTH // 2 - sub.get_width() // 2, 480))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
