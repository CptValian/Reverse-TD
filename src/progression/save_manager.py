import json
import os

DEFAULT_SAVE_DATA = {
    "points": {
        "LandShard": 0,
        "SwarmerBlood": 0,
        "Pykrite": 0
    },
    "upgrades": {
        # Skill Tree unlocks (LandShard)
        "starting_res_1": 0,
        "wood_stockpile_unlocked": 0,
        "gold_stockpile_unlocked": 0,
        "wall_unlocked": 0,
        "farm_unlocked": 0,
        "archer_unlocked": 0,
        "tower_unlocked": 0,
        "townhall_unlocked": 0,

        # SwarmerBlood (Stats Troupes / Workers)
        "worker_hp_lvl": 0,
        "worker_speed_lvl": 0,
        "infantry_hp_lvl": 0,
        "infantry_attack_lvl": 0,
        "archer_hp_lvl": 0,
        "archer_attack_lvl": 0,

        # Pykrite (Stats Bâtiments)
        "townhall_hp_lvl": 0,
        "barracks_hp_lvl": 0,
        "wall_hp_lvl": 0,
        "tower_hp_lvl": 0,
        "tower_attack_lvl": 0,
        "farm_hp_lvl": 0,
        "stockpile_hp_lvl": 0
    },
    "max_ai_defeated": 0
}

class SaveManager:
    def __init__(self, filepath="save_data.json"):
        self.filepath = filepath
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            import copy
            return copy.deepcopy(DEFAULT_SAVE_DATA)
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Backwards compatibility & migration
                if "points" in data:
                    old_p = data["points"]
                    if "Commandement" in old_p:
                        old_p["LandShard"] = old_p.pop("Commandement")
                    if "Forge" in old_p:
                        old_p["SwarmerBlood"] = old_p.pop("Forge")
                    if "Architecture" in old_p:
                        old_p["Pykrite"] = old_p.pop("Architecture")
                    for k in ["LandShard", "SwarmerBlood", "Pykrite"]:
                        if k not in old_p:
                            old_p[k] = 0
                else:
                    data["points"] = dict(DEFAULT_SAVE_DATA["points"])

                if "upgrades" in data:
                    for k, v in DEFAULT_SAVE_DATA["upgrades"].items():
                        if k not in data["upgrades"]:
                            data["upgrades"][k] = v
                else:
                    data["upgrades"] = dict(DEFAULT_SAVE_DATA["upgrades"])

                return data
        except Exception:
            import copy
            return copy.deepcopy(DEFAULT_SAVE_DATA)

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def add_points(self, command=0, forge=0, architecture=0, landshard=0, swarmerblood=0, pykrite=0):
        self.data["points"]["LandShard"] += command + landshard
        self.data["points"]["SwarmerBlood"] += forge + swarmerblood
        self.data["points"]["Pykrite"] += architecture + pykrite
        self.save()

    def get_points(self):
        return self.data["points"]

    def buy_upgrade(self, upgrade_key, point_type, cost=None, cost_base=10, is_tree_unlock=False):
        # Support aliases for point_type if old string passed
        if point_type == "Commandement":
            point_type = "LandShard"
        elif point_type == "Forge":
            point_type = "SwarmerBlood"
        elif point_type == "Architecture":
            point_type = "Pykrite"

        current_lvl = self.data["upgrades"].get(upgrade_key, 0)

        if is_tree_unlock:
            if current_lvl >= 1:
                return False  # Already unlocked
            actual_cost = cost if cost is not None else cost_base
        else:
            actual_cost = cost if cost is not None else cost_base * (current_lvl + 1)

        if self.data["points"].get(point_type, 0) >= actual_cost:
            self.data["points"][point_type] -= actual_cost
            self.data["upgrades"][upgrade_key] = current_lvl + 1
            self.save()
            return True
        return False
