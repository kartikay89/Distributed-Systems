# This class is used for defining the type of a Message
class MessageType(object):
    # REDIRECT: Sent by the HeadServer to a client, telling him which GameServers host a game
    # GAME_JOIN: Sent by a client, first to the HeadServer and later (when it knows which GameServers to connect to) to the GameServers
    # GAME_UPDATE: Sent by GameServers to client, telling them to update their GUI
    # GAME_SYNC: Sent by GameServers to each other, to decide on the latest state of a given game
    # GAME_START: Sent by HeadServers to GameServers, instructing them to start a certain game (with properties defined in the Game-object in the message)
    REDIRECT, GAME_JOIN, GAME_UPDATE, GAME_SYNC, GAME_START, GAME_ACTION = range(6)


class Message(object):
    def __init__(self, *args, **kwargs):
        # Standard type that all messages should have, with their standard values
        self.client = False
        self.type = None
        # Make the Message look like a string if we supply a string as its first and only non-keyword arg
        if len(args) == 1:
            self.__dict__['__stringdata'] = args[0];
        elif len(args) > 1:
            raise Exception('Message constructor takes at most 1 positional parameter')
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __repr__(self):
        if '__stringdata' in self.__dict__:
            return self.__dict__['__stringdata']
        else:
            return '[MESSAGE: {:s}]'.format(str(self.__dict__))
