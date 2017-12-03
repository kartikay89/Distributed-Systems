import threading

from networking import GAME_SYNC_INTERVAL, \
                       GameAction, GameActionType, GameSynchronizer, Message


class DummyGame(object):
    def __init__(self, identifier, server):
        self.identifier = identifier # Should be unique
        self.server = server
        self.servers = [] # List of ips belonging to the servers that host this game
        self.clients_to_update_servers = {} # Maps participating clients to the servers that send them updates
        self.dummy_contents = '<<DummyGame contents of DummyGame {:d}>>'.format(self.identifier)

        self.synchronizer = GameSynchronizer(self.server, self, GAME_SYNC_INTERVAL)
        self.synchronizer.start()
        self.checkpoint = None # Set to a copy of the last gamestate that all servers agreed on

        self.sync_msg_lock = threading.RLock()
        self.sync_messages = [] # Will contain messages sent by the other servers that host this game, used to sync our states

        self.buffer_lock = threading.RLock()
        self.command_buffer = [] # Will contain all commands that the servers have not yet agreed on
    
    def __repr__(self):
        return '[GAME: {:s}]'.format(str(self.__dict__))

    def perform_action(self, action):
        performed = True # Should actually be false here, but for now I want to store all actions

        if action.type == GameActionType.SPAWN:
            pass
        elif action.type == GameActionType.MOVE:
            pass
        # etc.
        # Store action, if it was actually performed (and not illegal)
        if performed:
            with self.buffer_lock:
                self.command_buffer.append(action)
