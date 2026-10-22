import math
import config

class BaseEntity:
    _id_counter = 0

    def __init__(self, owner_id, faction, x, y, max_hp, radius=20):
        BaseEntity._id_counter += 1
        self.id = BaseEntity._id_counter
        self.owner_id = owner_id
        self.faction = faction
        self.x = float(x)
        self.y = float(y)
        self.max_hp = max_hp
        self.hp = max_hp
        self.radius = radius
        self.selected = False
        self.alive = True

    def take_damage(self, amount, attacker=None, game_state=None):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

        if attacker and game_state and hasattr(game_state, 'ai_controllers'):
            for ai in game_state.ai_controllers:
                if ai.owner_id == self.owner_id:
                    ai.notify_under_attack(attacker, self, game_state)

    def heal(self, amount):
        if self.alive:
            self.hp = min(self.max_hp, self.hp + amount)

    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def distance_to_point(self, px, py):
        return math.hypot(self.x - px, self.y - py)

    def is_point_inside(self, px, py):
        return self.distance_to_point(px, py) <= self.radius

    def is_in_rect(self, rx, ry, rw, rh):
        min_x, max_x = min(rx, rx + rw), max(rx, rx + rw)
        min_y, max_y = min(ry, ry + rh), max(ry, ry + rh)
        return min_x <= self.x <= max_x and min_y <= self.y <= max_y
