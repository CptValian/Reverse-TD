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
        """Génère la carte selon le type de carte sélectionné:
           1: Carte standard
           2: Carte désavantageuse (Ressources du joueur limitées et éloignées, IA favorisée)
           3: Carte très désavantageuse (Ressources du joueur très rares et très éloignées, IA surarmée/suréquipée en biomasse)
        """
        spawn_points = []
        resources = []
        import math

        margin = 300
        if num_players == 2:
            spawn_points.append({"id": 0, "faction": config.FACTION_HUMAN, "x": margin, "y": margin})
            spawn_points.append({"id": 1, "faction": config.FACTION_ALIEN, "x": self.width - margin, "y": self.height - margin})
        else:
            angles = [i * (360 / num_players) for i in range(num_players)]
            center_x, center_y = self.width / 2, self.height / 2
            radius = min(self.width, self.height) / 2 - margin
            for i in range(num_players):
                rad = math.radians(angles[i])
                sx = center_x + radius * math.cos(rad)
                sy = center_y + radius * math.sin(rad)
                faction = config.FACTION_HUMAN if i == 0 else config.FACTION_ALIEN
                spawn_points.append({"id": i, "faction": faction, "x": sx, "y": sy})

        for sp in spawn_points:
            if sp["faction"] == config.FACTION_HUMAN:
                if map_type == 1:
                    # Normal map
                    res_list = ["gold", "wood", "food"]
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-15, 15)
                        rad = math.radians(angle)
                        rx = sp["x"] + 220 * math.cos(rad)
                        ry = sp["y"] + 220 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=1500))
                elif map_type == 2:
                    # Disadvantaged map: Player resources are farther away and reduced
                    res_list = ["gold", "wood", "food"]
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-15, 15)
                        rad = math.radians(angle)
                        # Farther from base (380px) and lower amount (800)
                        rx = sp["x"] + 380 * math.cos(rad)
                        ry = sp["y"] + 380 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=800))
                else:
                    # Very Disadvantaged map: Player resources are extremely far away (550px) and scarce (500)
                    res_list = ["gold", "wood", "food"]
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-15, 15)
                        rad = math.radians(angle)
                        rx = sp["x"] + 550 * math.cos(rad)
                        ry = sp["y"] + 550 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=500))

            else:
                # Alien AI base resource generation
                if map_type == 1:
                    for offset_angle in [0, 120, 240]:
                        rad = math.radians(offset_angle + random.randint(-15, 15))
                        rx = sp["x"] + 200 * math.cos(rad)
                        ry = sp["y"] + 200 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=1500))
                elif map_type == 2:
                    # Advantageous AI: Rich biomass right next to spawn (150px, 2500 amount)
                    for offset_angle in [0, 72, 144, 216, 288]:
                        rad = math.radians(offset_angle + random.randint(-10, 10))
                        rx = sp["x"] + 150 * math.cos(rad)
                        ry = sp["y"] + 150 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=2500))
                else:
                    # Extremely Advantageous AI: Massive biomass deposits right at spawn (120px, 4000 amount)
                    for offset_angle in [0, 60, 120, 180, 240, 300]:
                        rad = math.radians(offset_angle + random.randint(-10, 10))
                        rx = sp["x"] + 120 * math.cos(rad)
                        ry = sp["y"] + 120 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=4000))

        # Center map neutral nodes
        center_x, center_y = self.width / 2, self.height / 2
        num_center = 12 if map_type == 1 else (8 if map_type == 2 else 5)
        for _ in range(num_center):
            rx = center_x + random.randint(-500, 500)
            ry = center_y + random.randint(-500, 500)
            res_type = random.choice(["gold", "wood", "food", "biomass"])
            resources.append(ResourceNodeData(res_type, rx, ry, amount=2000))

        return {
            "width": self.width,
            "height": self.height,
            "spawns": spawn_points,
            "resources": resources
        }
