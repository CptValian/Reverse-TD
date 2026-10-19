import unittest
from src.engine.camera import Camera
import config

class TestCamera(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(screen_width=1000, screen_height=800, map_width=3000, map_height=3000)

    def test_camera_movement(self):
        initial_x, initial_y = self.camera.x, self.camera.y
        # Simuler un mouvement vers la droite et le bas
        keys = {config.pygame.K_d: True, config.pygame.K_s: True, config.pygame.K_z: False, config.pygame.K_q: False, config.pygame.K_UP: False, config.pygame.K_DOWN: False, config.pygame.K_LEFT: False, config.pygame.K_RIGHT: False} if hasattr(config, 'pygame') else {}
        # On va tester directement update sans le dictionnaire complet de keys de Pygame s'il n'est pas initialisé
        self.camera.update(dt=1.0, keys=None, mouse_pos=(1000, 800)) # edge scrolling
        self.assertGreater(self.camera.x, initial_x)
        self.assertGreater(self.camera.y, initial_y)

    def test_screen_to_world_conversion(self):
        self.camera.x = 100
        self.camera.y = 200
        self.camera.zoom = 2.0
        world_pos = self.camera.screen_to_world((100, 100))
        self.assertEqual(world_pos, (150.0, 250.0))

    def test_clamp(self):
        self.camera.x = -500
        self.camera.y = 5000
        self.camera.clamp()
        self.assertEqual(self.camera.x, 0.0)
        self.assertLessEqual(self.camera.y + self.camera.screen_height / self.camera.zoom, self.camera.map_height)

if __name__ == '__main__':
    unittest.main()
