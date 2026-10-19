# Échelle de difficulté et bonus technologiques des IA

# Difficulty Scaling & AI Technology Unlocks

AI_DIFFICULTY_LEVELS = {
    1: {
        "resource_multiplier": 0.5,
        "attack_wave_interval": 240,  # Wave every 4 minutes
        "max_army_size": 3,
        "max_workers": 3,
        "unlocked_techs": ["Drone", "Swarmer"],
        "unit_hp_bonus": 0.0,
        "unit_atk_bonus": 0.0,
        "can_build_defenses": False,
        "can_tech_ranged": False
    },
    2: {
        "resource_multiplier": 0.8,
        "attack_wave_interval": 180,  # Wave every 3 minutes
        "max_army_size": 5,
        "max_workers": 4,
        "unlocked_techs": ["Drone", "Swarmer"],
        "unit_hp_bonus": 0.0,
        "unit_atk_bonus": 0.0,
        "can_build_defenses": False,
        "can_tech_ranged": False
    },
    3: {
        "resource_multiplier": 1.0,
        "attack_wave_interval": 130,
        "max_army_size": 10,
        "max_workers": 6,
        "unlocked_techs": ["Drone", "Swarmer"],
        "unit_hp_bonus": 0.0,
        "unit_atk_bonus": 0.0,
        "can_build_defenses": False,
        "can_tech_ranged": False
    },
    4: {
        "resource_multiplier": 1.25,
        "attack_wave_interval": 90,
        "max_army_size": 18,
        "max_workers": 8,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter"],
        "unit_hp_bonus": 0.1,
        "unit_atk_bonus": 0.1,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    5: {
        "resource_multiplier": 1.6,
        "attack_wave_interval": 60,
        "max_army_size": 30,
        "max_workers": 12,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.25,
        "unit_atk_bonus": 0.2,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    6: {
        "resource_multiplier": 2.2,
        "attack_wave_interval": 40,
        "max_army_size": 45,
        "max_workers": 16,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.45,
        "unit_atk_bonus": 0.35,
        "can_build_defenses": True,
        "can_tech_ranged": True
    }
}
# Backward compatibility mapping string to int
for _k, _v in list(AI_DIFFICULTY_LEVELS.items()):
    pass
