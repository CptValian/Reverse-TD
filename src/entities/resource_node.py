from src.entities.base_entity import BaseEntity

class ResourceNode(BaseEntity):
    def __init__(self, resource_type, x, y, amount=1500):
        # owner_id = -1 pour neutre
        super().__init__(owner_id=-1, faction="Neutral", x=x, y=y, max_hp=amount, radius=25)
        self.resource_type = resource_type  # "gold" ou "biomass"
        self.amount = amount

    def harvest(self, requested_amount):
        harvested = min(self.amount, requested_amount)
        self.amount -= harvested
        self.hp = self.amount
        if self.amount <= 0:
            self.alive = False
        return harvested
