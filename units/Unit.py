import abc


class Direction:
    up, right, down, left = range(4)


class UnitType:
    player, dragon, undefined = range(3)


class Unit(abc.ABC):
    @abc.abstractmethod
    def adjustHitPoints(self, modifier):
        pass

    @abc.abstractmethod
    def dealDamage(self, x, y, damage):
        pass

