from units.Unit import Unit


class Dragon(Unit):

    def hi(self):
        print("health is %s\n" % self.maxHealth)

    MIN_TIME_BETWEEN_TURNS = 1
    MAX_TIME_BETWEEN_TURNS = 7

    MIN_HITPOINTS = 50
    MAX_HITPOINTS = 100

    MIN_ATTACKPOINTS = 5
    MAX_ATTACKPOINTS = 10

    def __init__(self, maxHealth=250, attackPoints=50):
        print("dragon: maxHealth: %d %d\n" % (20, maxHealth))
        super().__init__(maxHealth, attackPoints)