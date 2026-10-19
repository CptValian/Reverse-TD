import pygame
import config

class Menu:
    def __init__(self, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.font = pygame.font.SysFont("Arial", 22)

    def draw_main_menu(self, surface, selected_ai_count=1, selected_difficulty="Très Facile"):
        surface.fill(config.COLOR_BG)

        # Titre du jeu
        title = self.title_font.render("RTS : MÉDIÉVAL VS ALIEN INSECTE", True, config.COLOR_UI_ACCENT)
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))

        # Boutons d'options
        start_btn = pygame.Rect(self.screen_width // 2 - 150, 220, 300, 50)
        skill_tree_btn = pygame.Rect(self.screen_width // 2 - 150, 300, 300, 50)
        quit_btn = pygame.Rect(self.screen_width // 2 - 150, 380, 300, 50)

        pygame.draw.rect(surface, config.COLOR_UI_PANEL, start_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, start_btn, 2, border_radius=6)
        txt1 = self.font.render("LANCER LA PARTIE", True, config.COLOR_UI_TEXT)
        surface.blit(txt1, (start_btn.x + start_btn.width // 2 - txt1.get_width() // 2, start_btn.y + 12))

        pygame.draw.rect(surface, config.COLOR_UI_PANEL, skill_tree_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, skill_tree_btn, 2, border_radius=6)
        txt2 = self.font.render("ARBRE DE COMPÉTENCES", True, config.COLOR_UI_TEXT)
        surface.blit(txt2, (skill_tree_btn.x + skill_tree_btn.width // 2 - txt2.get_width() // 2, skill_tree_btn.y + 12))

        pygame.draw.rect(surface, config.COLOR_UI_PANEL, quit_btn, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_UI_ACCENT, quit_btn, 2, border_radius=6)
        txt3 = self.font.render("QUITTER", True, config.COLOR_UI_TEXT)
        surface.blit(txt3, (quit_btn.x + quit_btn.width // 2 - txt3.get_width() // 2, quit_btn.y + 12))

        # Sélecteurs de configuration de partie (Nombre d'IA & Difficulté)
        cfg_txt = self.font.render(f"IA Adverses: {selected_ai_count}  |  Difficulté: {selected_difficulty}", True, config.COLOR_UI_TEXT)
        surface.blit(cfg_txt, (self.screen_width // 2 - cfg_txt.get_width() // 2, 480))

        return {"start": start_btn, "skill_tree": skill_tree_btn, "quit": quit_btn}
