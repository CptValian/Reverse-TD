import unittest
import pygame
from src.ui.render_utils import RenderUtils
from src.ui.hud import HUD
from src.ui.menu import Menu
from src.engine.camera import Camera

class TestUI(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.HIDDEN)

    def test_ui_initialization(self):
        hud = HUD()
        menu = Menu()
        camera = Camera()
        surface = pygame.Surface((1280, 720))

        # Vérifier que les méthodes de rendu s'exécutent sans exception
        menu.draw_main_menu(surface)
        self.assertIsNotNone(hud)

    def test_menu_rendering(self):
        from src.engine.game_state import GameState
        from src.progression.save_manager import SaveManager

        menu = Menu()
        surface = pygame.Surface((1280, 720))
        save_manager = SaveManager()
        game_state = GameState(save_manager)

        btn_main = menu.draw_main_menu(surface)
        self.assertIn("start", btn_main)

        btn_setup = menu.draw_game_setup_menu(surface)
        self.assertIn("start_match", btn_setup)

        btn_opts = menu.draw_options_menu(surface, save_manager)
        self.assertIn("back", btn_opts)

        btn_pause = menu.draw_pause_menu(surface)
        self.assertIn("resume", btn_pause)

        btn_iacia = menu.draw_iacia_menu(surface, game_state)
        self.assertIn("launch", btn_iacia)

        btn_ai_info = menu.draw_ai_info_screen(surface, scroll_y=0)
        self.assertIn("back", btn_ai_info)

if __name__ == '__main__':
    unittest.main()
