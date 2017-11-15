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
        s.bind(('', PORT))

        # We send our server's IP address in the reply
        if not LOCAL:
            host = socket.gethostname()
        else:
            host = '127.0.0.{:d}'.format(self.server.identifier + 2)
        
        while True:
            try:
                # Check if there is a ping to reply to
                m, src = s.recvfrom(MAX_MSG_SIZE)
                self.sl_print('Message from {:s}: {:s}'.format(str(src), m))
                # 'host' is just the message content here, 'src' defines where we send it to
                s.sendto(host, src)
            except:
                # Got no message, do nothing
                pass
            # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.server.server_lock:
                if self.server.stop:
                    s.close()
                    self.sl_print('Stopped.')
                    break
                else:
                    time.sleep(0)