from units import Unit
from units.Dragon import Dragon
from units.Unit import Direction

if __name__ == '__main__':
    dragon = Dragon()
    dragon.spawn(10, 20)
    dragon.getUnit(10, 20)
    dragon.adjustHitPoints(0)

    dragon.dealDamage(1, 2, 10)
    dragon.dealDamage(0, 0, 10)
    dragon.removeUnit(10,20)

    print(Direction.down)