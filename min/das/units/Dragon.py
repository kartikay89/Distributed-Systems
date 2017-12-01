from Unit import *
from random import randint

class Dragon(Unit):
    maxHp = 100
    minHp = 50
    maxAp = 20
    minAp = 5

    Hp = randint(minHp, maxHp)
    Ap = randint(minAp, maxAp)

    def __init__(self):

        #to make each dragon possess one square only
        self.width = 1 #is it a right way?
        self.height = 1

    #initial Dragon's location on the map
    def locateDragon(self):
        self.dragon_location = [randint(map_width), randint(map_height)]
