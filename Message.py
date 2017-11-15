class MessageRequest:
    spawnUnit, getUnit, moveUnit, getType, dealDamage, removeUnit = range(6)


class Message:
    def __init__(self):
        self.d = {}

    def put(self, k, v):
        self.d[k] = v
