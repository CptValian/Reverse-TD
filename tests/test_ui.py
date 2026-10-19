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

if __name__ == '__main__':
    unittest.main()
