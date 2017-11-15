import socket
import threading
import time
from networking import LOCAL, PORT, MAX_MSG_SIZE, safe_print


class ServerListener(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def sl_print(self, s):
        safe_print('[SERVERLISTENER {:d}]: {:s}'.format(self.server.identifier, s))

    def run(self):
        start_time = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(0)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('<broadcast>', PORT))
        
        while True:
            # If there is no message for us, do nothing
            try:
                m, src = s.recvfrom(MAX_MSG_SIZE)
                self.sl_print('Message from {:s}: {:s}'.format(str(src), m))
                s.sendto('ServerListener {:d} replying'.format(self.server.identifier), src)
            except:
                pass
            # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.server.server_lock:
                if self.server.stop:
                    s.close()
                    self.sl_print('Stopped.')
                    break
                else:
                    time.sleep(0)