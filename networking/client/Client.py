from Queue import Queue
import pickle
import socket
import threading
import time

from networking import CLIENT_PORT, END_OF_MSG, HEADSERVER_IP, LOCAL, MAX_MSG_SIZE, TIMEOUT, \
                       ClientListener, Message, MessageSender, MessageType, \
                       await_confirm, await_reply, connect_to_dst, safe_print


class Client(threading.Thread):
    def __init__(self, identifier, queue=None):
        threading.Thread.__init__(self)
        self.identifier = identifier
        # Determine what IP to bind our sockets to
        if not LOCAL:
            self.host = socket.gethostname()
        else:
            # Client address space: 127.0.1.x
            self.host = '127.0.1.{:d}'.format(self.identifier + 3)
        self.server_hosts = None
        self.game_id = None
        self.draw_queue = queue

        # A lock-protected variable used to communicate that this thread is stopping (used by the client's listener)
        self.stop_lock = threading.RLock()
        self.stop = False

        # A lock-protected buffer for incoming messages
        self.message_lock = threading.RLock()
        self.messages = []

        self.client_listener = ClientListener(self)
        self.client_listener.start()

    def c_print(self, s):
        safe_print('[CLIENT {:d}]: {:s}'.format(self.identifier, s))

    def draw(self, units):
        if LOCAL:
            self.draw_queue.put(units)
        else:
            pass

    # Wrapper function for sending a message to a given host
    def send_message(self, host, message):
        message.host = self.host
        message.client_id = self.identifier
        message.client = True
        MessageSender(self, TIMEOUT, host, CLIENT_PORT, message).start()

    # Iterates over all messages we have received and not processed yet, and deals with them
    def handle_messages(self):
        with self.message_lock:
            for message in self.messages:
                if message.type == MessageType.GAME_UPDATE:
                    self.c_print('We got GAME_UPDATE: {:s}'.format(message.contents))
                    self.draw(message.contents)
                elif message.type == MessageType.REDIRECT:
                    self.server_hosts = message.servers
                    self.game_id = message.game_id
                    self.c_print('We got REDIRECT to: {:s}'.format(message.servers))
                    message = Message(type=MessageType.GAME_JOIN, game_id=self.game_id)
                    for host in self.server_hosts:
                        self.send_message(host, message)
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

        message = Message(type=MessageType.GAME_JOIN, game_id=None)
        self.send_message(HEADSERVER_IP, message)
        
        while True:
            self.handle_messages()
            # Run for 5 seconds
            if time.time() - start_time >= 5:
                self.prepare_stop()
                return
            time.sleep(0)