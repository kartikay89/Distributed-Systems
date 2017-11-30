import socket
import threading
import time
from networking import LOCAL, PORT, MAX_MSG_SIZE, DEBUG_PRINT, TIMEOUT, safe_print, ServerListener, ServerBroadcaster, MessageSender


class Server(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier

        # Determine what IP to bind our sockets to
        if not LOCAL:
            self.host = socket.gethostname()
        else:
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

    # This function assumes that there will be 1 Client connecting to our hostname
    # As I'm writing this, THIS IS CURRENTLY NOT THE CASE (anymore).
    # ONLY USE THIS FUNCTION AS INSPIRATION FOR OTHER FUNCTIONS
    '''def test_interact_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allows sockets to bind to addresses that are already in use (useful if we kill the program, or if we used this address shortly before)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, PORT))
        
        self.s_print('listening on ' + self.host + ':' + str(PORT))
        
        # Listen with a backlog of max-size 1
        s.listen(1)

        client_socket, (client_host, client_port) = s.accept()
        self.s_print('Incoming connection from {:s}:{:d}'.format(client_host, client_port))
        
        msg = client_socket.recv(MAX_MSG_SIZE)
        self.s_print('Got msg: {:s}'.format(msg))
        client_socket.send('<< Greetings from SERVER {:d} >>'.format(self.identifier))
        
        client_socket.close()
        self.s_print('Stopped.')'''
