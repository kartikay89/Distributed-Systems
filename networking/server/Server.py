import socket
import threading
import time

from networking import DEBUG_PRINT, LOCAL, MAX_MSG_SIZE, PORT, TIMEOUT, \
                       ServerBroadcaster, ServerListener, MessageSender, \
                       safe_print

class Server(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier

        # Determine what IP to bind our sockets to
        if not LOCAL:
            self.host = socket.gethostname()
        else:
            # Server address space: 127.0.0.x
            # Prevent using 127.0.0.0 and 127.0.0.1 - I think those may be reserved
            self.host = '127.0.0.{:d}'.format(self.identifier + 3)

        # A lock-protected variable used to communicate that this thread is stopping (used by the server's listener/broadcaster)
        self.stop_lock = threading.RLock()
        self.stop = False
        
        # A lock-protected list of all known peer servers
        self.peer_lock = threading.RLock()
        self.neighbours = []

        # A lock-protected buffer for incoming messages
        self.message_lock = threading.RLock()
        self.messages = []

        # A lock-protected list of clients that have connected to this server
        self.clients_lock = threading.RLock()
        self.clients = []

        # This thread will listen for pinging servers, reply if necessary and update the neighbours-list
        self.server_listener = ServerListener(self)
        self.server_listener.start()
        # This thread will broadcast ping messages, listen for replies and update the neighbours-list
        self.server_broadcaster = ServerBroadcaster(self, 1)    # Ping every 1 second
        self.server_broadcaster.start()

    def s_print(self, s):
        safe_print('[SERVER {:d}]: {:s}'.format(self.identifier, s))

    # Wrapper function for sending a message to a given host
    def send_message(self, host, message):
        MessageSender(self, TIMEOUT, host, PORT, message).start()

    # Wrapper function for sending a message to all neighbours
    def send_to_all(self, msg):
        with self.peer_lock:
            for n in self.neighbours:
                if n != self.host:
                    self.send_message(n, msg)
