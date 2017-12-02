import socket
import socket
import threading
import time

from networking import CLIENT_PORT, HEADSERVER_IP, LOCAL, TIMEOUT, \
    ClientListener, Message, MessageSender, \
    safe_print
from units.Player import Player


class Client(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier
        # Determine what IP to bind our sockets to
        if not LOCAL:
            self.host = socket.gethostname()
        else:
            # Client address space: 127.0.1.x
            self.host = '127.0.1.{:d}'.format(self.identifier + 3)
        self.server_host = None

        # A lock-protected variable used to communicate that this thread is stopping (used by the client's listener)
        self.stop_lock = threading.RLock()
        self.stop = False

        # A lock-protected buffer for incoming messages
        self.message_lock = threading.RLock()
        self.messages = []

        self.client_listener = ClientListener(self)
        self.client_listener.start()

        # Add player instance
        self.player = Player()

    def c_print(self, s):
        safe_print('[CLIENT {:d}]: {:s}'.format(self.identifier, s))

    # Iterates over all messages we have received and not processed yet, and deals with them
    def handle_messages(self):
        with self.message_lock:
            for message in self.messages:
                if message.type == 'DRAW':
                    self.c_print('We will DRAW this message: {:s}'.format(message.contents))
                    pass
                elif message.type == 'REDIRECT':
                    self.server_host = message.host
                    self.c_print("Redirecting to game server")
                    message = Message(type='GAME_JOIN', client=True, host=self.host)
                    MessageSender(self, TIMEOUT, self.server_host, CLIENT_PORT, message).start()

                    # Debug
                    time.sleep(1)
                    move_message = Message(type='UNIT_MOVE', host="garbage", client=True, direction='LEFT')
                    MessageSender(self, TIMEOUT, self.server_host, CLIENT_PORT, move_message).start()

                else:
                    self.c_print('Got message of unknown type: {:s}'.format(message))
            self.messages = []

    # Prepares this client for closing, by instructing and waiting for our listener to stop
    def prepare_stop(self):
        with self.stop_lock:
            self.stop = True
        self.client_listener.join()
        self.c_print('Stopped.')

    def run(self):
        start_time = time.time()

        message = Message(type='GAME_JOIN', client=True, host=self.host)
        MessageSender(self, TIMEOUT, HEADSERVER_IP, CLIENT_PORT, message).start()

        # move_message = Message(type='UNIT_MOVE', client=True, host=self.host, direction='LEFT')
        # MessageSender(self, TIMEOUT, HEADSERVER_IP, CLIENT_PORT, move_message).start()
        
        while True:
            self.handle_messages()
            # Run for 5 seconds
            if time.time() - start_time >= 5:
                self.prepare_stop()
                return
            time.sleep(0)
