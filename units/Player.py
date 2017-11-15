from units.Unit import Unit


class Player(Unit):


    def hi(self):
        print("player hp %s\n" % self.maxHealth)

    def dealDamage(self, x, y, damage):
        pass

    def adjustHitPoints(self, modifier):
        pass