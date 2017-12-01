import time

from networking import PORT, \
                       Message, Server, \
                       safe_print

# This class is used for the worker servers that are used for hosting games
class GameServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)
        self.games = []
        self.clients_to_games = {}

    def s_print(self, s):
        safe_print('[GAMESERVER {:d}]: {:s}'.format(self.identifier, s))

    def handle_messages(self):
        with self.message_lock:
            for message in self.messages:
                self.s_print('Received message {:s}'.format(message))
                if message.type == 'GAME_JOIN':
                    if message.host not in self.clients:
                        self.clients.append(message.host)
                    self.clients_to_games[message.host] = 'My lovely test game'
            self.messages = []

    # Send all clients the current 'status' of their 'games'.
    # TODO: only send updates when necessary (due to a status change in the game)
    def update_clients(self):
        for client in self.clients:
            self.send_message(client, Message(type='DRAW', contents=self.clients_to_games[client]))

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
                self.s_print('Known neighbours: {:s}'.format(self.neighbours))
                # Test function to be updated
                self.update_clients()
            # Yield
            time.sleep(0)
