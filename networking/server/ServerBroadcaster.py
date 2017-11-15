import socket
import threading
import time
from networking import LOCAL, PORT, MAX_MSG_SIZE, safe_print


class ServerBroadcaster(threading.Thread):
    def __init__(self, server, interval):
        threading.Thread.__init__(self)
        self.server = server
        self.interval = interval

    def sb_print(self, s):
        safe_print('[SERVERBROADCASTER {:d}]: {:s}'.format(self.server.identifier, s))

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.setblocking(0)

        # Start with a ping, then re-ping every <interval> seconds
        timestamp = time.time()
        ping = True
        while True:
            if ping:
                # We're pinging; update timestamp
                ping = False
                timestamp = time.time()
                s.sendto('Ping from ServerBroadcaster {:d}'.format(self.server.identifier), ('<broadcast>', PORT))
                self.sb_print('Pinged.')
            else:
                try:
                    # Try fetching a message
                    m, src = s.recvfrom(MAX_MSG_SIZE)
                    self.sb_print('Reply from {:s}: {:s}'.format(str(src), m))
                except:
                    # Got no message, do nothing
                    pass
                # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
                with self.server.server_lock:
                    if self.server.stop:
                        # Close socket and stop
                        s.close()
                        self.sb_print('Stopped.')
                        break
                    else:
                        # Yield
                        time.sleep(0)
                        # Check if we need to send another ping
                        if time.time() - timestamp > self.interval:
                            ping = True
     