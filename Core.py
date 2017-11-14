from units import Unit
from units.Dragon import Dragon
from units.Unit import Direction

if __name__ == '__main__':
    dragon = Dragon(1, 2)
    dragon.dealDamage(1, 2, 10)

    print(Direction.down)