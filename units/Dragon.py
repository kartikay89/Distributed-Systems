from random import random

from units.Unit import Unit


class Dragon(Unit):

    def hi(self):
        print("health is %s\n" % self.maxHealth)

    MIN_TIME_BETWEEN_TURNS = 1
    MAX_TIME_BETWEEN_TURNS = 7

    MIN_HITPOINTS = 50
    MAX_HITPOINTS = 100

    MIN_ATTACKPOINTS = 5
    MAX_ATTACKPOINTS = 20

    def __init__(self, x, y):
        super().__init__(
            random() * (self.MAX_HITPOINTS - self.MIN_HITPOINTS) + self.MIN_HITPOINTS,
            random() * (self.MAX_ATTACKPOINTS - self.MIN_ATTACKPOINTS) + self.MIN_ATTACKPOINTS
        )
        print("dragon: maxHealth: %d\n" % self.maxHealth)
