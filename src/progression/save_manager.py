import json
import os

DEFAULT_SAVE_DATA = {
    "points": {
        "Commandement": 0,
        "Forge": 0,
        "Architecture": 0
    },
    "upgrades": {
        # Forge (Stats Unités)
        "unit_hp_lvl": 0,       # +10% PV unités par niveau
        "unit_attack_lvl": 0,   # +10% Attaque par niveau
        "unit_speed_lvl": 0,    # +5% Vitesse par niveau

        # Architecture (Stats Bâtiments)
        "building_hp_lvl": 0,   # +15% PV bâtiments par niveau
        "building_armor_lvl": 0,# +1 Armure par niveau

        # Commandement (Général)
        "starting_resources_lvl": 0 # +100 Ressources au départ
    },
    "max_ai_defeated": 0
}

class SaveManager:
    def __init__(self, filepath="save_data.json"):
        self.filepath = filepath
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            return dict(DEFAULT_SAVE_DATA)
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return dict(DEFAULT_SAVE_DATA)

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def add_points(self, command=0, forge=0, architecture=0):
        self.data["points"]["Commandement"] += command
        self.data["points"]["Forge"] += forge
        self.data["points"]["Architecture"] += architecture
        self.save()

    def get_points(self):
        return self.data["points"]

    def buy_upgrade(self, upgrade_key, point_type, cost_base=10):
        current_lvl = self.data["upgrades"].get(upgrade_key, 0)
        cost = cost_base * (current_lvl + 1)
        if self.data["points"][point_type] >= cost:
            self.data["points"][point_type] -= cost
            self.data["upgrades"][upgrade_key] = current_lvl + 1
            self.save()
            return True
        return False
