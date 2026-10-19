import config

class Rewards:
    DIFFICULTY_MULTIPLIER = {
        1: 0.6,
        2: 0.8,
        3: 1.0,
        4: 1.5,
        5: 2.2,
        6: 3.5,
        7: 4.8,
        8: 6.5,
        9: 8.5,
        10: 12.0,
        "Very Easy": 0.8,
        "Easy": 1.0,
        "Medium": 1.5,
        "Hard": 2.2,
        "Extreme": 3.5
    }

    @staticmethod
    def calculate_rewards(victory, num_ais, difficulty, survival_time=0.0):
        try:
            diff_key = int(difficulty)
        except (ValueError, TypeError):
            diff_key = difficulty

        mult = Rewards.DIFFICULTY_MULTIPLIER.get(diff_key, 1.0)

        # Base victory calculations
        victory_command = 20 * num_ais * mult
        victory_forge = 25 * num_ais * mult
        victory_architecture = 15 * num_ais * mult

        if victory:
            base_command = victory_command
            base_forge = victory_forge
            base_architecture = victory_architecture
        else:
            # Défaite : Le gain en cas de perte ne peut excéder 1/3 de la victoire.
            # Il est proportionnel au temps survécu (ex. max atteint à 300s = 5 minutes).
            target_time = 300.0
            time_ratio = min(1.0, max(0.0, survival_time / target_time))
            max_defeat_ratio = 1.0 / 3.0

            base_command = victory_command * max_defeat_ratio * time_ratio
            base_forge = victory_forge * max_defeat_ratio * time_ratio
            base_architecture = victory_architecture * max_defeat_ratio * time_ratio

        return {
            config.POINT_TYPE_COMMAND: int(base_command),
            config.POINT_TYPE_FORGE: int(base_forge),
            config.POINT_TYPE_ARCHITECTURE: int(base_architecture)
        }
