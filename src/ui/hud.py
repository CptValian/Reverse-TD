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

        pop_curr = game_state.get_unit_count(0)
        pop_max = game_state.get_pop_max(0)
        res_text = f"Age: {game_state.player_age} | Gold: {int(player_res.get('gold', 0))} | Wood: {int(player_res.get('wood', 0))} | Food: {int(player_res.get('food', 0))} | Biomass: {int(player_res.get('biomass', 0))} | Pop: {pop_curr}/{pop_max}"
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
            # Hide enemy entities on minimap if fog of war enabled and not visible
            if entity.owner_id != 0 and game_state.is_fog_of_war_enabled():
                if not game_state.is_point_visible(entity.x, entity.y, owner_id=0):
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

        selected_entities = [e for e in game_state.units + game_state.buildings if e.selected]
        if selected_entities:
            first = selected_entities[0]
            is_enemy = (first.owner_id != 0)

            name = getattr(first, 'unit_type', getattr(first, 'building_type', 'Entité'))
            status_extra = ""
            if hasattr(first, 'is_constructed') and not first.is_constructed:
                pct = int((1.0 - first.build_timer / max(0.001, first.total_build_time)) * 100)
                status_extra = f" [Under Construction: {pct}%]"

            owner_label = " [ENEMY]" if is_enemy else ""
            info_text = f"Selected: {name}{owner_label} (HP: {int(first.hp)}/{first.max_hp}){status_extra}"
            img_info = self.font.render(info_text, True, (255, 100, 100) if is_enemy else config.COLOR_UI_TEXT)
            surface.blit(img_info, (panel_rect.x + 20, panel_rect.y + 8))

            # Display stats for player units
            if not is_enemy and hasattr(first, 'unit_type'):
                u_type = getattr(first, 'unit_type', 'Unit')
                atk = getattr(first, 'attack_power', 0)
                rng = getattr(first, 'attack_range', 0)
                spd = getattr(first, 'speed', 0)
                role = "Worker" if getattr(first, 'is_worker', False) else "Combat Unit"

                stats_txt = f"Role: {role} | Attack Power: {atk} | Attack Range: {rng} | Speed: {spd}"
                t_stats = self.font.render(stats_txt, True, (255, 215, 0))
                surface.blit(t_stats, (panel_rect.x + 350, panel_rect.y + 8))

            # Helper for enemy descriptions & stats
            if is_enemy:
                if hasattr(first, 'building_type'):
                    b_type = first.building_type
                    b_funcs = {
                        "Hive": "Main Base & Hatchery - Trains Drones and stores gathered biomass.",
                        "SpawningPool": "Spawning Structure - Trains Swarmers and Spitter ranged troops.",
                        "SpineCrawler": "Defensive Organism - Attacks ground targets entering its boundary.",
                        "TownHall": "Main Base - Trains Peasants and stores resources.",
                        "Barracks": "Military Facility - Trains Infantry and Archer units.",
                        "Tower": "Watchtower - Shoots arrows at nearby enemy targets.",
                        "Wall": "Fortification Wall - Blocks pathing and protects base.",
                        "Farm": "Agriculture - Supplies food for units.",
                        "WoodStockpile": "Resource Drop-off - Stores gathered wood.",
                        "GoldStockpile": "Resource Drop-off - Stores gathered gold.",
                        "FoodStockpile": "Grain Mill Depot - Stores gathered food."
                    }
                    func_desc = b_funcs.get(b_type, "Enemy structure.")
                    t_func = self.font.render(f"Function: {func_desc}", True, (255, 215, 0))
                    surface.blit(t_func, (panel_rect.x + 20, panel_rect.y + 45))
                else:
                    # Enemy unit stats
                    u_type = getattr(first, 'unit_type', 'Unit')
                    atk = getattr(first, 'attack_power', 0)
                    rng = getattr(first, 'attack_range', 0)
                    spd = getattr(first, 'speed', 0)
                    role = "Worker" if getattr(first, 'is_worker', False) else "Combat Unit"

                    stats_txt = f"Role: {role} | Attack Power: {atk} | Attack Range: {rng} | Speed: {spd}"
                    t_stats = self.font.render(stats_txt, True, (255, 215, 0))
                    surface.blit(t_stats, (panel_rect.x + 20, panel_rect.y + 45))
                return

            upgrades = game_state.save_manager.data.get("upgrades", {})

            def format_cost_str(cost_obj):
                if isinstance(cost_obj, dict):
                    parts = []
                    name_map = {"gold": "Gold", "wood": "Wood", "food": "Food", "biomass": "Bio"}
                    for k, v in cost_obj.items():
                        parts.append(f"{v} {name_map.get(k, k)}")
                    return ", ".join(parts)
                return str(cost_obj)

            # Si c'est un bâtiment
            if hasattr(first, 'building_type'):
                btn_x = panel_rect.x + 20
                btn_y = panel_rect.y + 35

                if first.building_type == "TownHall":
                    # Age Up Button in TownHall interface
                    next_age = game_state.player_age + 1
                    cost_wood = 200 * next_age
                    cost_gold = 200 * next_age
                    age_unlocked_in_tree = upgrades.get(f"ageing_up_{next_age}")

                    if age_unlocked_in_tree:
                        age_btn = pygame.Rect(panel_rect.x + 550, panel_rect.y + 8, 220, 32)
                        pygame.draw.rect(surface, (40, 90, 60), age_btn, border_radius=4)
                        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, age_btn, 1, border_radius=4)
                        t_age = self.font.render(f"Advance to Age {next_age} ({cost_wood}W/{cost_gold}G)", True, config.COLOR_UI_TEXT)
                        surface.blit(t_age, (age_btn.x + 8, age_btn.y + 5))

                    if upgrades.get("garrison_unlocked"):
                        num_g = len(getattr(first, 'garrisoned_units', []))
                        garr_info = f"Garrisoned Peasants: {num_g}/{first.max_garrison} (+{num_g} Arrows)"
                        img_garr = self.font.render(garr_info, True, (255, 215, 0))
                        surface.blit(img_garr, (panel_rect.x + 250, panel_rect.y + 10))

                        # Ungarrison button if garrisoned units present
                        if num_g > 0:
                            ungarr_btn = pygame.Rect(panel_rect.x + 460, panel_rect.y + 8, 80, 26)
                            pygame.draw.rect(surface, (120, 50, 50), ungarr_btn, border_radius=4)
                            pygame.draw.rect(surface, config.COLOR_UI_ACCENT, ungarr_btn, 1, border_radius=4)
                            t_ungarr = self.font.render("Eject All", True, config.COLOR_UI_TEXT)
                            surface.blit(t_ungarr, (ungarr_btn.x + 10, ungarr_btn.y + 3))

                elif first.building_type == "Farm":
                    num_g = len(getattr(first, 'garrisoned_units', []))
                    food_rate = int(num_g * config.DEFAULT_HARVEST_RATE * 0.5)
                    garr_info = f"Working Peasants Inside: {num_g}/{first.max_garrison} (+{food_rate} Food/s)"
                    img_garr = self.font.render(garr_info, True, (255, 215, 0))
                    surface.blit(img_garr, (panel_rect.x + 20, panel_rect.y + 40))

                    if num_g > 0:
                        ungarr_btn = pygame.Rect(panel_rect.x + 360, panel_rect.y + 36, 90, 26)
                        pygame.draw.rect(surface, (120, 50, 50), ungarr_btn, border_radius=4)
                        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, ungarr_btn, 1, border_radius=4)
                        t_ungarr = self.font.render("Eject All", True, config.COLOR_UI_TEXT)
                        surface.blit(t_ungarr, (ungarr_btn.x + 10, ungarr_btn.y + 3))

                # Boutons de recrutement
                if first.trainable_units and first.is_constructed:
                    # Filter trainable units by unlock status
                    trainable = []
                    for u in first.trainable_units:
                        if u == "Archer" and not upgrades.get("archer_unlocked"):
                            continue
                        if u == "Scout" and not upgrades.get("scout_unlocked"):
                            continue
                        trainable.append(u)

                    for u_type in trainable:
                        from src.entities.unit import UNIT_TYPES
                        u_data = UNIT_TYPES.get(u_type, {})
                        cost_str = format_cost_str(u_data.get("cost", 50))

                        btn_rect = pygame.Rect(btn_x, btn_y, 160, 42)
                        pygame.draw.rect(surface, (60, 64, 72), btn_rect, border_radius=4)
                        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)

                        t_name = self.font.render(f"+ {u_type}", True, config.COLOR_UI_TEXT)
                        t_cost = self.font.render(cost_str, True, config.COLOR_UI_ACCENT)
                        surface.blit(t_name, (btn_x + 6, btn_y + 3))
                        surface.blit(t_cost, (btn_x + 6, btn_y + 20))
                        btn_x += 170

                # Affichage de la file d'attente de production
                queue_x = panel_rect.x + 20
                queue_y = panel_rect.y + 85
                if first.production_queue:
                    q_title = self.font.render("Queue:", True, config.COLOR_UI_TEXT)
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
                btn_x = panel_rect.x + 10
                btn_y = panel_rect.y + 40
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
                    if upgrades.get("food_stockpile_unlocked"):
                        buildings_to_build.append("FoodStockpile")
                    if upgrades.get("house_unlocked"):
                        buildings_to_build.append("House")
                    if upgrades.get("farm_unlocked"):
                        buildings_to_build.append("Farm")
                    if upgrades.get("townhall_unlocked") and getattr(game_state, 'player_age', 1) >= 2:
                        buildings_to_build.append("TownHall")
                else:
                    buildings_to_build = ["SpawningPool", "SpineCrawler"]

                from src.entities.building import BUILDING_TYPES
                for b_type in buildings_to_build:
                    b_data = BUILDING_TYPES.get(b_type, {})
                    cost_str = format_cost_str(b_data.get("cost", {}))

                    btn_width = 125
                    btn_rect = pygame.Rect(btn_x, btn_y, btn_width, 45)
                    pygame.draw.rect(surface, (60, 64, 72), btn_rect, border_radius=4)
                    pygame.draw.rect(surface, config.COLOR_UI_ACCENT, btn_rect, 1, border_radius=4)

                    t_name = self.font.render(f"Build {b_type}", True, config.COLOR_UI_TEXT)
                    t_cost = self.font.render(cost_str, True, config.COLOR_UI_ACCENT)
                    surface.blit(t_name, (btn_x + 4, btn_y + 4))
                    surface.blit(t_cost, (btn_x + 4, btn_y + 24))
                    btn_x += btn_width + 8
