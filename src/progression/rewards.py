import config

class Rewards:
    DIFFICULTY_MULTIPLIER = {
        "Très Facile": 1.0,
        "Facile": 1.25,
        "Moyen": 1.75,
        "Difficile": 2.5,
        "Extrême": 4.0
    }

    @staticmethod
    def calculate_rewards(victory, num_ais, difficulty):
        mult = Rewards.DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)

        if victory:
            # Victoire : Points multipliés par la difficulté et le nombre d'IA battues
            base_command = 20 * num_ais * mult
            base_forge = 25 * num_ais * mult
            base_architecture = 15 * num_ais * mult
        else:
            # Défaite : Récompense de consolation (20%)
            base_command = 5 * mult
            base_forge = 5 * mult
            base_architecture = 5 * mult

        return {
            config.POINT_TYPE_COMMAND: int(base_command),
            config.POINT_TYPE_FORGE: int(base_forge),
            config.POINT_TYPE_ARCHITECTURE: int(base_architecture)
        }
