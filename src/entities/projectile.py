import math

class Projectile:
    def __init__(self, x, y, target_entity, damage, speed=450, owner_id=0, projectile_type="arrow", on_hit_callback=None, delay=0.0):
        self.x = x
        self.y = y
        self.target_entity = target_entity
        self.target_pos = (target_entity.x, target_entity.y) if target_entity else (x, y)
        self.damage = damage
        self.speed = speed
        self.owner_id = owner_id
        self.projectile_type = projectile_type
        self.on_hit_callback = on_hit_callback
        self.delay = delay
        self.radius = 4
        self.alive = True
        self.selected = False
        self.hp = 1
        self.max_hp = 1

    def is_point_inside(self, px, py):
        return False

    def take_damage(self, amount):
        pass

    def update(self, dt, game_state):
        if not self.alive:
            return

        if self.delay > 0:
            self.delay -= dt
            return

        if self.target_entity and getattr(self.target_entity, 'alive', True):
            self.target_pos = (self.target_entity.x, self.target_entity.y)

        tx, ty = self.target_pos
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        step = self.speed * dt
        if dist <= step or dist < 5:
            self.x = tx
            self.y = ty
            self.alive = False
            # Apply damage to target if alive
            if self.target_entity and getattr(self.target_entity, 'alive', True):
                prev_hp = self.target_entity.hp
                self.target_entity.take_damage(self.damage)
                if self.on_hit_callback:
                    self.on_hit_callback(self.target_entity, prev_hp, game_state)
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
