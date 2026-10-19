# Échelle de difficulté et bonus technologiques des IA

AI_DIFFICULTY_LEVELS = {
    "Très Facile": {
        "resource_multiplier": 1.0,
        "attack_wave_interval": 120,  # Attaque toutes les 2 minutes
        "max_army_size": 10,
        "unlocked_techs": ["Drone", "Swarmer"]
    },
    "Facile": {
        "resource_multiplier": 1.1,
        "attack_wave_interval": 90,
        "max_army_size": 15,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter"]
    },
    "Moyen": {
        "resource_multiplier": 1.3,
        "attack_wave_interval": 60,
        "max_army_size": 25,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"]
    },
    "Difficile": {
        "resource_multiplier": 1.6,
        "attack_wave_interval": 45,
        "max_army_size": 40,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"]
    },
    "Extrême": {
        "resource_multiplier": 2.0,
        "attack_wave_interval": 30,
        "max_army_size": 60,
        "unlocked_techs": ["Drone", "Swarmer", "Spitter", "SpineCrawler"]
    }
}
