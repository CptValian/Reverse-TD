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
           1: Carte standard (Équilibrée)
           2: Carte désavantageuse I (Ressources raréfiées, plus éloignées)
           3: Carte très désavantageuse II (Ressources très rares et très éloignées)
           4: Carte avantageuse I (Ressources très proches et abondantes)
           5: Carte très avantageuse II (Ressources extrêmement proches, ultra riches & multiples gisements)
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
                res_list = ["gold", "wood", "food"]
                if map_type == 1:
                    # Normal map
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-15, 15)
                        rad = math.radians(angle)
                        rx = sp["x"] + 220 * math.cos(rad)
                        ry = sp["y"] + 220 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=1500))
                elif map_type == 2:
                    # Disadvantaged I
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-15, 15)
                        rad = math.radians(angle)
                        rx = sp["x"] + 380 * math.cos(rad)
                        ry = sp["y"] + 380 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=800))
                elif map_type == 3:
                    # Very Disadvantaged II
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-15, 15)
                        rad = math.radians(angle)
                        rx = sp["x"] + 550 * math.cos(rad)
                        ry = sp["y"] + 550 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=500))
                elif map_type == 4:
                    # Advantage I: Abundant resources close to base (160px, amount 2500)
                    for idx, r_type in enumerate(res_list):
                        angle = idx * 120 + random.randint(-10, 10)
                        rad = math.radians(angle)
                        rx = sp["x"] + 160 * math.cos(rad)
                        ry = sp["y"] + 160 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=2500))
                elif map_type == 5:
                    # Advantage II: Extremely close (120px) double deposits of gold, wood, food (amount 4000)
                    for idx, r_type in enumerate(res_list * 2):
                        angle = idx * 60 + random.randint(-10, 10)
                        rad = math.radians(angle)
                        rx = sp["x"] + 120 * math.cos(rad)
                        ry = sp["y"] + 120 * math.sin(rad)
                        resources.append(ResourceNodeData(r_type, rx, ry, amount=4000))

            else:
                # Alien AI base resource generation
                if map_type == 1:
                    for offset_angle in [0, 120, 240]:
                        rad = math.radians(offset_angle + random.randint(-15, 15))
                        rx = sp["x"] + 200 * math.cos(rad)
                        ry = sp["y"] + 200 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=1500))
                elif map_type in [2, 3]:
                    # Strong AI on player disadvantage maps
                    num_dep = 5 if map_type == 2 else 6
                    amt = 2500 if map_type == 2 else 4000
                    for offset_angle in [i * (360 / num_dep) for i in range(num_dep)]:
                        rad = math.radians(offset_angle + random.randint(-10, 10))
                        rx = sp["x"] + 150 * math.cos(rad)
                        ry = sp["y"] + 150 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=amt))
                elif map_type == 4:
                    # Advantage I (Moderate AI biomass)
                    for offset_angle in [0, 120, 240]:
                        rad = math.radians(offset_angle + random.randint(-15, 15))
                        rx = sp["x"] + 220 * math.cos(rad)
                        ry = sp["y"] + 220 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=1200))
                elif map_type == 5:
                    # Advantage II (Low AI biomass)
                    for offset_angle in [0, 180]:
                        rad = math.radians(offset_angle)
                        rx = sp["x"] + 280 * math.cos(rad)
                        ry = sp["y"] + 280 * math.sin(rad)
                        resources.append(ResourceNodeData("biomass", rx, ry, amount=800))

        # Center map neutral nodes
        center_x, center_y = self.width / 2, self.height / 2
        num_center = 12 if map_type == 1 else (8 if map_type in [2, 3] else 16)
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
