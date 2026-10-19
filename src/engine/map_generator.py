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

    def generate_map(self, num_players=2):
        """Génère la carte, les emplacements de départ des joueurs et les ressources."""
        spawn_points = []
        resources = []

        # Calculer les zones de départ (ex: 2 joueurs aux coins opposés)
        margin = 300
        if num_players == 2:
            spawn_points.append({"id": 0, "faction": config.FACTION_HUMAN, "x": margin, "y": margin})
            spawn_points.append({"id": 1, "faction": config.FACTION_ALIEN, "x": self.width - margin, "y": self.height - margin})
        else:
            # Pour plusieurs IA plus tard
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

        # Placer des gisements de ressources autour de chaque base de départ
        for sp in spawn_points:
            import math
            if sp["faction"] == config.FACTION_HUMAN:
                res_list = ["gold", "wood", "food"]
                for idx, r_type in enumerate(res_list):
                    angle = idx * 120 + random.randint(-15, 15)
                    rad = math.radians(angle)
                    rx = sp["x"] + 220 * math.cos(rad)
                    ry = sp["y"] + 220 * math.sin(rad)
                    resources.append(ResourceNodeData(r_type, rx, ry, amount=1500))
            else:
                for offset_angle in [0, 120, 240]:
                    rad = math.radians(offset_angle + random.randint(-15, 15))
                    rx = sp["x"] + 200 * math.cos(rad)
                    ry = sp["y"] + 200 * math.sin(rad)
                    resources.append(ResourceNodeData("biomass", rx, ry, amount=1500))

        # Ajouter des gisements neutres au centre de la carte
        center_x, center_y = self.width / 2, self.height / 2
        for _ in range(12):
            rx = center_x + random.randint(-500, 500)
            ry = center_y + random.randint(-500, 500)
            res_type = random.choice(["gold", "wood", "food", "biomass"])
            resources.append(ResourceNodeData(res_type, rx, ry, amount=2500))

        return {
            "width": self.width,
            "height": self.height,
            "spawns": spawn_points,
            "resources": resources
        }
