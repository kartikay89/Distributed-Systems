# This class is used for defining the type of action (the MessageType must have been GAME_ACTION)
class GameActionType(object):
    MOVE, HEAL, ATTACK, SPAWN = range(4)
    type_as_str = {
        MOVE: 'MOVE',
        HEAL: 'HEAL',
        ATTACK: 'ATTACK',
        SPAWN: 'SPAWN'
    }

# This class is used to define a game action
class GameAction(object):
    def __init__(self, *args, **kwargs):
        self.type = None
        self.player = None
        for key, value in kwargs.items():
            self.__dict__[key] = value

    # Lovely Pythonic built-in function overrides
    def __repr__(self):
        return '[GAME_ACTION <{:s}>: {:s}]'.format(GameActionType.type_as_str[self.type], str(self.__dict__))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other