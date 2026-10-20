# Échelle de difficulté et bonus technologiques des IA

# Difficulty Scaling & AI Technology Unlocks

AI_DIFFICULTY_LEVELS = {
    1: {
        "resource_multiplier": 1.0,
        "attack_wave_interval": 120,
        "max_army_size": 8,
        "max_workers": 5,
        "unlocked_techs": ["Drone", "Swarmer"],
        "unit_hp_bonus": 0.0,
        "unit_atk_bonus": 0.0,
        "can_build_defenses": True,
        "can_tech_ranged": False
    },
    2: {
        "resource_multiplier": 1.2,
        "attack_wave_interval": 90,
        "max_army_size": 12,
        "max_workers": 7,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter"],
        "unit_hp_bonus": 0.05,
        "unit_atk_bonus": 0.05,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    3: {
        "resource_multiplier": 1.5,
        "attack_wave_interval": 70,
        "max_army_size": 18,
        "max_workers": 10,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter"],
        "unit_hp_bonus": 0.1,
        "unit_atk_bonus": 0.1,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    4: {
        "resource_multiplier": 1.8,
        "attack_wave_interval": 50,
        "max_army_size": 25,
        "max_workers": 12,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.2,
        "unit_atk_bonus": 0.15,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    5: {
        "resource_multiplier": 2.2,
        "attack_wave_interval": 35,
        "max_army_size": 35,
        "max_workers": 15,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.35,
        "unit_atk_bonus": 0.25,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    6: {
        "resource_multiplier": 2.8,
        "attack_wave_interval": 25,
        "max_army_size": 50,
        "max_workers": 20,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.5,
        "unit_atk_bonus": 0.4,
        "can_build_defenses": True,
        "can_tech_ranged": True
    },
    7: {
        "resource_multiplier": 3.2,
        "attack_wave_interval": 20,
        "max_army_size": 60,
        "max_workers": 22,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.65,
        "unit_atk_bonus": 0.55,
        "can_build_defenses": True,
        "can_tech_ranged": True,
        "worker_raid_priority": True
    },
    8: {
        "resource_multiplier": 3.8,
        "attack_wave_interval": 18,
        "max_army_size": 75,
        "max_workers": 25,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 0.80,
        "unit_atk_bonus": 0.70,
        "can_build_defenses": True,
        "can_tech_ranged": True,
        "worker_raid_priority": True,
        "tactical_retreat": True
    },
    9: {
        "resource_multiplier": 4.5,
        "attack_wave_interval": 15,
        "max_army_size": 90,
        "max_workers": 28,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 1.00,
        "unit_atk_bonus": 0.85,
        "can_build_defenses": True,
        "can_tech_ranged": True,
        "worker_raid_priority": True,
        "tactical_retreat": True,
        "flanking_attacks": True
    },
    10: {
        "resource_multiplier": 5.5,
        "attack_wave_interval": 10,
        "max_army_size": 120,
        "max_workers": 30,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"],
        "unit_hp_bonus": 1.30,
        "unit_atk_bonus": 1.00,
        "can_build_defenses": True,
        "can_tech_ranged": True,
        "worker_raid_priority": True,
        "tactical_retreat": True,
        "flanking_attacks": True,
        "swarm_frenzy": True
    }
}
