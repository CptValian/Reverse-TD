import json
import os

DEFAULT_SAVE_DATA = {
    "settings": {
        "disable_fog_of_war": False
    },
    "points": {
        "LandShard": 0,
        "SwarmerBlood": 0,
        "Pykrite": 0,
        "Muculus": 0,
        "Conjulat": 0,
        "Mass": 0
    },
    "upgrades": {
        # Skill Tree unlocks (LandShard / Muculus)
        "starting_res_1": 0,
        "wood_stockpile_unlocked": 0,
        "gold_stockpile_unlocked": 0,
        "wall_unlocked": 0,
        "farm_unlocked": 0,
        "archer_unlocked": 0,
        "tower_unlocked": 0,
        "tower_range_unlocked": 0,
        "looting_unlocked": 0,
        "extra_worker_start": 0,
        "extra_melee_start": 0,
        "townhall_unlocked": 0,

        # New requested Skill Tree upgrades
        "high_starting_res": 0,        # Starting Cache II (+100)
        "starting_cache_3": 0,         # Starting Cache III (+100)
        "near_base_res_boost": 0,      # x1.5 quantity for resource piles near base
        "temple_unlocked": 0,          # Holy Temple & Monk unlock
        "tower_extra_projectile": 0,   # Defensive towers fire +1 projectile
        "forum_atk_range": 0,          # Forum attack range +10%
        "watchtower_sight": 0,         # Watchtower sight +20%
        "scout_unlocked": 0,           # Scout unit unlock
        "building_repair_unlocked": 0, # Worker building repair order
        "double_base_res_cap": 0,      # Double starting resource node capacity around base
        "forum_passive_arrow": 0,      # Forum shoots base arrow even without workers (arrows = workers + 1)

        # SwarmerBlood (Stats Troupes / Workers - Human)
        "worker_hp_lvl": 0,
        "worker_speed_lvl": 0,
        "infantry_hp_lvl": 0,
        "infantry_attack_lvl": 0,
        "archer_hp_lvl": 0,
        "archer_attack_lvl": 0,

        # Pykrite (Stats Bâtiments - Human)
        "townhall_hp_lvl": 0,
        "barracks_hp_lvl": 0,
        "wall_hp_lvl": 0,
        "tower_hp_lvl": 0,
        "tower_attack_lvl": 0,
        "farm_hp_lvl": 0,
        "stockpile_hp_lvl": 0,

        # --- ALIEN SKILL TREE UNLOCKS (Muculus) ---
        "alien_starting_res_1": 0,          # Organic Cache (+100 Biomass)
        "alien_biomass_stockpile_unlocked": 0, # Biomass Depot
        "alien_spawning_pool_unlocked": 0,  # Spawning Pool (Swarmers)
        "alien_spitter_unlocked": 0,        # Spitter Unit
        "alien_spine_crawler_unlocked": 0,  # Spine Crawler defense
        "alien_biomass_gen_unlocked": 0,     # Biomass Generator
        "alien_evolution_chamber_unlocked": 0,# Evolution Chamber
        "alien_queen_unlocked": 0,          # Queen Hero unit
        "alien_second_hive_unlocked": 0,     # Secondary Hive
        "alien_creep_spread_unlocked": 0,   # Creep Speed/Attack Buff
        "alien_hive_enrage_unlocked": 0,    # Hive Enrage Ability

        # Conjulat (Stats Troupes / Drones - Alien)
        "drone_hp_lvl": 0,
        "drone_speed_lvl": 0,
        "swarmer_hp_lvl": 0,
        "swarmer_attack_lvl": 0,
        "spitter_hp_lvl": 0,
        "spitter_attack_lvl": 0,
        "queen_hp_lvl": 0,
        "queen_attack_lvl": 0,

        # Mass (Stats Bâtiments - Alien)
        "hive_hp_lvl": 0,
        "spawning_pool_hp_lvl": 0,
        "spine_crawler_hp_lvl": 0,
        "spine_crawler_attack_lvl": 0,
        "biomass_gen_hp_lvl": 0
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

                if "settings" not in data:
                    data["settings"] = dict(DEFAULT_SAVE_DATA["settings"])

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

    def add_points(self, command=0, forge=0, architecture=0, landshard=0, swarmerblood=0, pykrite=0, muculus=0, conjulat=0, mass=0):
        if "LandShard" not in self.data["points"]: self.data["points"]["LandShard"] = 0
        if "SwarmerBlood" not in self.data["points"]: self.data["points"]["SwarmerBlood"] = 0
        if "Pykrite" not in self.data["points"]: self.data["points"]["Pykrite"] = 0
        if "Muculus" not in self.data["points"]: self.data["points"]["Muculus"] = 0
        if "Conjulat" not in self.data["points"]: self.data["points"]["Conjulat"] = 0
        if "Mass" not in self.data["points"]: self.data["points"]["Mass"] = 0

        self.data["points"]["LandShard"] += command + landshard
        self.data["points"]["SwarmerBlood"] += forge + swarmerblood
        self.data["points"]["Pykrite"] += architecture + pykrite
        self.data["points"]["Muculus"] += muculus
        self.data["points"]["Conjulat"] += conjulat
        self.data["points"]["Mass"] += mass
        self.save()

    def get_setting(self, key, default=False):
        return self.data.get("settings", {}).get(key, default)

    def set_setting(self, key, value):
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
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
