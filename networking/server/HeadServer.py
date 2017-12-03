import random
import threading
import time

from networking import NSERVERS_PER_GAME, PORT, \
                       DummyGame, HeadServerListener, Message, MessageType, Server, \
                       safe_print

# This class is used for the worker servers that are used for hosting games
class HeadServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)

        self.head_server_listener = HeadServerListener(self)
        self.head_server_listener.start()

        # A mapping of game ids to the servers that host these games
        self.games_to_servers = {}
        self.game_counter = 0

    def s_print(self, s):
        safe_print('[HEADSERVER {:d} at {:s}]: {:s}'.format(self.identifier, self.host, s))

    # Find a number of game servers (currently done randomly)
    def find_gameservers(self, nservers):
        with self.peer_lock:
            shuffled = self.neighbours[:]
            random.shuffle(shuffled)
            return shuffled[0:nservers]

    # Starts a game by determining an id and which servers to use for this game
    # Also instructs those servers to start hosting this game
    def start_game(self):
        # We assign a new game id based on our local game_counter variable
        game_id = self.game_counter
        self.game_counter += 1
        # Find some servers to start hosting this game
        servers = self.find_gameservers(NSERVERS_PER_GAME)
        # Instruct the game servers to start hosting this game
        start_message = Message(type=MessageType.GAME_START, game_id=game_id, servers=servers)
        for gameserver in servers:
            self.send_message(gameserver, start_message)
        # Update our local data
        self.games_to_servers[game_id] = servers
        return game_id, servers
        
    # Checks if a game with game_id exists
    # If so, returns the game_id and the servers hosting it
    # If not, starts a new game and returns corresponding game_id and servers
    def get_gamedata(self, game_id):
        if game_id != None:
            if game_id in self.games_to_servers.keys():
                return game_id, self.games_to_servers[game_id]
        # We don't have a game with id game_id, so we create a new one
        game_id, servers = self.start_game()
        # TODO: instead of creating a new game, use an existing one
        return game_id, servers

    # We have a new client! :)
    def handle_new_client(self, message):
        # First, add this client to our client list if it isn't in there already
        if message.host not in self.clients:
            self.clients.append(message.host)

        with self.peer_lock:
            # If we don't have enough GameServers, we can't process this request yet
            if len(self.neighbours) < NSERVERS_PER_GAME:
                #self.s_print('Not enough neighbours ({:d})'.format(len(self.neighbours)))
                return False
        game_id, game_servers = self.get_gamedata(message.game_id)
        self.s_print('Telling client {:d} at {:s} to connect to {:s}'.format(message.client_id, message.host, game_servers))
        reply = Message(type=MessageType.REDIRECT, game_id=game_id, servers=game_servers)
        self.send_message(message.host, reply)
        return True

    # Read messages from our message buffer and deal with them
    def handle_messages(self):
        # Messages that can't be handled immediately need to be saved
        remaining_messages = []
        with self.message_lock:
            for message in self.messages:
                # A client wishes to join a game
                if message.type == MessageType.GAME_JOIN:
                    # Try to find him a game, and if we fail we'll try again later
                    if self.handle_new_client(message):
                        # Our client finally got closure, so we can close the socket
                        continue
                else:
                    self.s_print('Received message of unknown type: {:s}'.format(message))
                    continue
                # If we reach this point, the message hasn't been dealt with so we keep it
                remaining_messages.append(message)
            self.messages = remaining_messages

    def run(self):
        start_time = time.time()
        iter_time = start_time
        current_time = start_time
        
        # Stop after 5 seconds
        while True:
            current_time = time.time()
            self.handle_messages()
            if current_time - start_time >= 5:
                with self.clients_lock:
                    self.s_print('Clients connected: {:s}'.format(str(self.clients)))
                with self.stop_lock:
                    self.stop = True
                # Wait for our listener and broadcaster threads to quit
                self.server_listener.join()
                self.head_server_listener.join()
                self.server_broadcaster.join()
                self.s_print('Stopped.')
                break
            elif current_time - iter_time >= 1:
                iter_time = current_time
                with self.peer_lock:
                    self.s_print('Known neighbours: {:s}'.format(self.neighbours))
                #self.send_to_all(Message('Greetings from {:s}'.format(self.host)))
            time.sleep(0)
