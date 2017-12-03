import copy
import threading
import time
from md5 import md5

# sudo pip install python-levenshtein
from Levenshtein import distance

from networking import PORT, \
                       DummyGame, GameAction, GameActionType, Message, MessageType, Server, \
                       safe_print

# This class is used for the worker servers that are used for hosting games
class GameServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)

        self.games_lock = threading.RLock()
        self.games = {} # Maps ids to game objects
        self.clients_to_games = {} # Maps clients to game ids

    def __repr__(self):
        return '[GAMESERVER {:d} at {:s}]'.format(self.identifier, self.host)

    def s_print(self, s):
        safe_print('[GAMESERVER {:d} @ {:s}]: {:s}'.format(self.identifier, self.host, s))

    # Determines which server should send game updates to this client
    # Uses the Levenshtein distance between the hashes of the IP addresses
    def determine_update_server(self, game, client):
        client_hash = md5(client).digest()
        result = None
        current_shortest = 0
        for server in game.servers:
            # Calculate the Levenshtein distance between the client's IP's hash and this server's IP's hash
            dist = distance(client_hash, md5(server).digest())
            if result == None or dist < current_shortest:
                # Find out which distance is the shortest: the corresponding server will serve this client
                result = server
                current_shortest = dist
        # Store the result.
        # Each server will calculate and store this data separately, thereby reaching consensus as to who is served by whom
        game.clients_to_update_servers[client] = result
        #self.s_print('We think client {:s} should be served by {:s} for game {:d}'.format(client, result, game.identifier))

    # Attempt to join a client to a game
    def game_join(self, message):
        if message.host not in self.clients:
            self.clients.append(message.host)

        # check if we host this game
        with self.games_lock:
            game = self.games.get(message.game_id)
        if not game:
            # We don't serve this game
            #self.s_print('Client {:d} can\'t join game {:d} (we don\'t serve it)'.format(message.client_id, message.game_id))
            return False
        else:
            self.s_print('Client {:d} at {:s} joined game {:d}'.format(message.client_id, message.host, message.game_id))
            # Perform_action should cancel this action if the player is already in the game
            game.perform_action(GameAction(type=GameActionType.SPAWN, player=message.host))
            self.clients_to_games[message.host] = message.game_id
            self.determine_update_server(game, message.host)
            return True

    # Start up a game, given an id and its hosts
    def start_game(self, game_id, servers):
        game = DummyGame(game_id, self)
        game.servers = servers
        game.checkpoint = copy.copy(game)
        with self.games_lock:
            self.games[game.identifier] = game
        self.s_print('Started up game {:s}'.format(game))

    # Read messages from our message buffer and deal with them
    def handle_messages(self):
        with self.message_lock:
            remaining_messages = []
            for message in self.messages:
                #self.s_print('Received message {:s}'.format(message))
                if message.type == MessageType.GAME_JOIN:
                    # Check if this client can join this game; if not, keep the message
                    if self.game_join(message):
                        continue
                elif message.type == MessageType.GAME_START:
                    # A HeadServer has told us to start a new game
                    self.start_game(message.game_id, message.servers)
                    continue
                elif message.type == MessageType.GAME_ACTION:
                    # Currently doesn't do much because we only work with dummy games
                    with self.games_lock:
                        self.games[messages.game_id].perform_action(message)
                    continue
                elif message.type == MessageType.GAME_SYNC:
                    # This is a synchronization message sent by another server, related to a specific game
                    # It will be dealt by by the game's GameSynchronizer
                    with self.games_lock:
                        game = self.games[message.game_id]
                        with game.sync_msg_lock:
                            game.sync_messages.append(message)
                    continue
                else:
                    self.s_print('Received message of unknown type: {:s}'.format(message))
                    continue
                # If we reach this point, the message hasn't been dealt with so we keep it
                remaining_messages.append(message)
            self.messages = remaining_messages

    # Send all clients the current 'status' of their 'games', if we serve them.
    # TODO: only send updates when necessary (due to a status change in the game)
    def update_clients(self):
        for client in self.clients:
            # Find game
            game_id = self.clients_to_games.get(client)
            with self.games_lock:
                game = self.games.get(game_id)
            if game:
                # Check if we are the server that should be sending updates to this client
                if game.clients_to_update_servers[client] == self.host:
                    self.send_message(client, Message(type=MessageType.GAME_UPDATE, contents=game.dummy_contents))

    def run(self):
        start_time = time.time()
        print_time = start_time
        current_time = print_time
        
        while True:
            current_time = time.time()
            self.handle_messages()
            # Stop after 5 seconds
            if current_time - start_time >= 5:
                with self.stop_lock:
                    self.stop = True
                # Wait for our listener and broadcaster threads to quit
                self.server_listener.join()
                self.server_broadcaster.join()
                self.s_print('Stopped.')
                return
            elif current_time - print_time >= 1:
                print_time = current_time
                #with self.peer_lock:
                #    self.s_print('Known neighbours: {:s}'.format(self.neighbours))
                #self.s_print('Current games: {:s}'.format(self.games))
                # Test function to be updated
                self.update_clients()
            # Yield
            time.sleep(0)
