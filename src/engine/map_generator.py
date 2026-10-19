import random
import config

class ResourceNodeData:
    def __init__(self, resource_type, x, y, amount=1000):
        self.type = resource_type  # "gold" ou "biomass"
        self.x = x
        self.y = y
        self.amount = amount

class MapGenerator:
    def __init__(self, width=config.MAP_WIDTH, height=config.MAP_HEIGHT):
        self.width = width
        self.height = height

    def generate_map(self, num_players=2, map_type=1):
        """Génère la carte, les emplacements de départ des joueurs et les ressources selon le type de carte."""
        spawn_points = []
        resources = []

        margin = 300
        if num_players == 2:
            spawn_points.append({"id": 0, "faction": config.FACTION_HUMAN, "x": margin, "y": margin})
            spawn_points.append({"id": 1, "faction": config.FACTION_ALIEN, "x": self.width - margin, "y": self.height - margin})
        else:
            angles = [i * (360 / num_players) for i in range(num_players)]
            center_x, center_y = self.width / 2, self.height / 2
            radius = min(self.width, self.height) / 2 - margin
            import math
            for i in range(num_players):
                rad = math.radians(angles[i])
                sx = center_x + radius * math.cos(rad)
                sy = center_y + radius * math.sin(rad)
                faction = config.FACTION_HUMAN if i == 0 else config.FACTION_ALIEN
                spawn_points.append({"id": i, "faction": faction, "x": sx, "y": sy})

        # Placer des gisements de ressources selon l'avantage / désavantage de la carte
        import math
        for sp in spawn_points:
            if sp["faction"] == config.FACTION_HUMAN:
                res_list = ["gold", "wood", "food"]
                p_dist = 220 if map_type == 1 else (350 if map_type == 2 else 450)
                p_amount = 1500 if map_type == 1 else (800 if map_type == 2 else 500)
                for idx, r_type in enumerate(res_list):
                    angle = idx * 120 + random.randint(-15, 15)
                    rad = math.radians(angle)
                    rx = sp["x"] + p_dist * math.cos(rad)
                    ry = sp["y"] + p_dist * math.sin(rad)
                    resources.append(ResourceNodeData(r_type, rx, ry, amount=p_amount))
            else:
                ai_dist = 200 if map_type == 1 else (150 if map_type == 2 else 120)
                ai_amount = 1500 if map_type == 1 else (3000 if map_type == 2 else 5000)
                ai_nodes = [0, 120, 240]
                if map_type == 2:
                    ai_nodes = [0, 60, 120, 180, 240]
                elif map_type == 3:
                    ai_nodes = [0, 45, 90, 135, 180, 225, 270, 315]

                for offset_angle in ai_nodes:
                    rad = math.radians(offset_angle + random.randint(-15, 15))
                    rx = sp["x"] + ai_dist * math.cos(rad)
                    ry = sp["y"] + ai_dist * math.sin(rad)
                    resources.append(ResourceNodeData("biomass", rx, ry, amount=ai_amount))

        # Ajouter des gisements neutres au centre de la carte (orientés vers l'IA pour cartes désavantageuses)
        center_x, center_y = self.width / 2, self.height / 2
        for _ in range(12):
            bias_x = 0 if map_type == 1 else (200 if map_type == 2 else 400)
            bias_y = 0 if map_type == 1 else (200 if map_type == 2 else 400)
            rx = center_x + bias_x + random.randint(-400, 400)
            ry = center_y + bias_y + random.randint(-400, 400)
            res_type = random.choice(["gold", "wood", "food", "biomass"])
            resources.append(ResourceNodeData(res_type, rx, ry, amount=2500))

        return {
            "width": self.width,
            "height": self.height,
            "spawns": spawn_points,
            "resources": resources
        }
