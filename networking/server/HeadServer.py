import random
import threading
import time

from networking import PORT, \
                       HeadServerListener, Message, Server, \
                       safe_print

# This class is used for the worker servers that are used for hosting games
class HeadServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)

        self.head_server_listener = HeadServerListener(self)
        self.head_server_listener.start()

    def s_print(self, s):
        safe_print('[HEADSERVER {:d}]: {:s}'.format(self.identifier, s))

    # Tells a client which server to connect to
    def redirect_client(self, message):
        # First, add this client to our client list if it isn't in there already
        if message.host not in self.clients:
            self.clients.append(message.host)

        with self.peer_lock:
            if len(self.neighbours) == 0:
                #self.s_print('No neighbours')
                return False
            # TODO: improve
            host = random.choice(self.neighbours)
            self.s_print('Telling client to connect to {:s}'.format(host))
            reply = Message(type='REDIRECT', host=host)
            self.send_message(message.host, reply)
            return True

    # Read messages from our message buffer and deal with them
    def handle_messages(self):
        # Messages that can't be handled immediately need to be saved
        remaining_messages = []
        with self.message_lock:
            for message in self.messages:
                # A client wishes to join a game
                if message.type == 'GAME_JOIN':
                    # Try to find him a game, and if we fail we'll try again later
                    if self.redirect_client(message):
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
                #self.send_to_all(Message('Greetings from {:s}'.format(self.host)))
            time.sleep(0)
