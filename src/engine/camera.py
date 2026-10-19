import pygame
import config

class Camera:
    def __init__(self, screen_width=config.SCREEN_WIDTH, screen_height=config.SCREEN_HEIGHT, map_width=config.MAP_WIDTH, map_height=config.MAP_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height

        # Position (coin supérieur gauche de la vue en coordonnées monde)
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0

    def update(self, dt, keys=None, mouse_pos=None):
        speed = config.CAMERA_SPEED / self.zoom
        move_x = 0
        move_y = 0

        if keys:
            if keys[pygame.K_z] or keys[pygame.K_UP] or keys[pygame.K_w]:
                move_y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y += 1
            if keys[pygame.K_q] or keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1

        # Edge scrolling
        if mouse_pos:
            mx, my = mouse_pos
            margin = config.EDGE_SCROLL_MARGIN
            if mx <= margin:
                move_x -= 1
            elif mx >= self.screen_width - margin:
                move_x += 1
            if my <= margin:
                move_y -= 1
            elif my >= self.screen_height - margin:
                move_y += 1

        # Normaliser le vecteur de mouvement
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        self.x += move_x * speed * dt
        self.y += move_y * speed * dt

        self.clamp()

    def handle_zoom(self, zoom_in, mouse_pos):
        """Ajuste le zoom centré sur la position de la souris."""
        old_zoom = self.zoom
        if zoom_in:
            self.zoom = min(config.CAMERA_ZOOM_MAX, self.zoom + config.CAMERA_ZOOM_SPEED)
        else:
            self.zoom = max(config.CAMERA_ZOOM_MIN, self.zoom - config.CAMERA_ZOOM_SPEED)

        if self.zoom != old_zoom:
            mx, my = mouse_pos
            # Re-centrer par rapport à la souris
            world_x_before = self.x + mx / old_zoom
            world_y_before = self.y + my / old_zoom

            self.x = world_x_before - mx / self.zoom
            self.y = world_y_before - my / self.zoom
            self.clamp()

    def clamp(self):
        """Restreint la caméra dans les limites de la carte."""
        view_w = self.screen_width / self.zoom
        view_h = self.screen_height / self.zoom

        max_x = max(0, self.map_width - view_w)
        max_y = max(0, self.map_height - view_h)

        self.x = max(0.0, min(self.x, max_x))
        self.y = max(0.0, min(self.y, max_y))

    def screen_to_world(self, screen_pos):
        sx, sy = screen_pos
        world_x = self.x + sx / self.zoom
        world_y = self.y + sy / self.zoom
        return (world_x, world_y)

    def world_to_screen(self, world_pos):
        wx, wy = world_pos
        screen_x = (wx - self.x) * self.zoom
        screen_y = (wy - self.y) * self.zoom
        return (screen_x, screen_y)

    def get_visible_rect(self):
        return pygame.Rect(self.x, self.y, self.screen_width / self.zoom, self.screen_height / self.zoom)
