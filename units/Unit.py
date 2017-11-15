import abc


class Direction:
    up, right, down, left = range(4)


class UnitType:
    player, dragon, undefined = range(3)


class Unit(abc.ABC):
    def __init__(self, maxHealth, attackPoints):
        self.maxHealth = maxHealth
        self.attackPoints = attackPoints

    @abc.abstractmethod
    def adjustHitPoints(self, modifier):
        pass

    @abc.abstractmethod
    def dealDamage(self, x, y, damage):
        pass

    @abc.abstractmethod
    def hi(self):
        pass

