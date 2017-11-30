import threading
import time

from networking import PORT, Server, HeadServerListener

# This class is used for the worker servers that are used for hosting games
class HeadServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)

        # A lock-protected list of clients that have connected to the head server
        self.clients_lock = threading.RLock()
        self.clients = []

        self.head_server_listener = HeadServerListener(self)
        self.head_server_listener.start()

    def run(self):
        start_time = time.time()
        current_time = start_time
        
        # Stop after 5 seconds
        while True:
            current_time = time.time()
            if current_time - start_time >= 5:
                with self.clients_lock:
                    self.s_print('Clients connected: {:s}'.format(str(self.clients)))
                    self.clients = []
                with self.stop_lock:
                    self.stop = True
                # Wait for our listener and broadcaster threads to quit
                self.server_listener.join()
                self.head_server_listener.join()
                self.server_broadcaster.join()
                self.s_print('Stopped.')
                break
            else:
                time.sleep(0)
