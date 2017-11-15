import socket
import threading
import time
from networking import LOCAL, PORT, MAX_MSG_SIZE, safe_print, ServerListener, ServerBroadcaster


class Server(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier

        # Every server has its own ServerListener thread, which listens for other connecting servers
        self.neighbours = []
        self.stop = False
        self.server_lock = threading.RLock()
        self.server_listener = ServerListener(self)
        self.server_listener.start()
        self.server_broadcaster = ServerBroadcaster(self, 1) # Ping every second
        self.server_broadcaster.start()

    def s_print(self, s):
        safe_print('[SERVER {:d}]: {:s}'.format(self.identifier, s))

    '''def test(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allows sockets to bind to addresses that are already in use (useful if we kill the program, or if we used this address shortly before)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if not LOCAL:
            s.bind(socket.gethostname())
        else:
            # Prevent using 127.0.0.0 and 127.0.0.1 - I think those may be reserved
            host = '127.0.0.{:d}'.format(self.identifier + 2)
            s.bind((host, PORT))
            self.s_print('listening on ' + host + ':' + str(PORT))
        # Listen with a backlog of max-size 1
        s.listen(1)

        client_socket, (client_host, client_port) = s.accept()
        self.s_print('Incoming connection from {:s}:{:d}'.format(client_host, client_port))
        
        msg = client_socket.recv(MAX_MSG_SIZE)
        self.s_print('Got msg: {:s}'.format(msg))
        client_socket.send('<< Greetings from SERVER {:d} >>'.format(self.identifier))
        
        client_socket.close()
        self.s_print('Stopped.')'''

    def run(self):
        start_time = time.time()
        
        # Stop after 5 seconds
        while True:
            if time.time() - start_time >= 5:
                with self.server_lock:
                    self.stop = True
                # Wait for our listener and broadcaster threads to quit
                self.server_listener.join()
                self.server_broadcaster.join()
                self.s_print('Stopped.')
                break
            else:
                time.sleep(0)