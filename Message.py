class MessageRequest:
    spawnUnit, getUnit, dealDamage, removeUnit = range(4)


class Message:
    def __init__(self):
        self.d = {}

    def put(self, k, v):
        self.d[k] = v
