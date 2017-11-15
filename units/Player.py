from random import random

from units.Unit import Unit


class Player(Unit):
    MIN_HITPOINTS = 10
    MAX_HITPOINTS = 20

    MIN_ATTACKPOINTS = 1
    MAX_ATTACKPOINTS = 10

    def hi(self):
        print("player hp %s\n" % self.maxHealth)

    def __init__(self, x, y):
        super().__init__(
            random() * (self.MAX_HITPOINTS - self.MIN_HITPOINTS) + self.MIN_HITPOINTS,
            random() * (self.MAX_ATTACKPOINTS - self.MIN_ATTACKPOINTS) + self.MIN_ATTACKPOINTS
        )
        print("player: maxHealth: %d \n" % self.maxHealth)

        self.spawn(x, y)
