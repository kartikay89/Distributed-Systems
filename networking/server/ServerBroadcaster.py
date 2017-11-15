import socket
import threading
import time
from networking import LOCAL, PORT, MAX_MSG_SIZE, safe_print


class ServerBroadcaster(threading.Thread):
    def __init__(self, server, interval):
        threading.Thread.__init__(self)
        self.server = server
        self.interval = interval
        # This list will be updated on ping replies, and will replace
        # the server's neighbours list every <interval> seconds
        self.neighbours = []

    def sb_print(self, s):
        safe_print('[SERVERBROADCASTER {:d}]: {:s}'.format(self.server.identifier, s))

    # Given a list of tuples (host, port), this function adds an entry to it if it is not already in it
    def add_neighbour(self, src_tuple):
        if src_tuple not in self.neighbours:
            self.neighbours.append(src_tuple)
        else:
            self.sb_print('Got reply from {:s}, which was already in our list'.format(str(src_tuple)))

    # Given a (correctly defined) socket, checks if there are any replies to process.
    def check_replies(self, s):
        try:
            # Check if there is a reply
            m, src = s.recvfrom(MAX_MSG_SIZE)
            # There was! Update our neighbours list if necessary
            # The message itself ('m') will be the IP address of the replying server
            self.sb_print('Reply from {:s}: {:s}'.format(str(src), m))
            self.add_neighbour(m)
        except:
            # Got no message, do nothing
            pass

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
                # Update the server's neighbour list with the data gathered from our previous ping
                # By replacing the list entirely, we also deal with the issue of removing outdated entries
                with self.server.server_lock:
                    self.server.neighbours = self.neighbours
                    self.sb_print('Updated neighbours to {:s}'.format(self.neighbours))
                # Start with an empty neighbours list again
                self.neighbours = []
                s.sendto('Ping from ServerBroadcaster {:d}'.format(self.server.identifier), ('<broadcast>', PORT))
                self.sb_print('Pinged.')
            else:
                self.check_replies(s)
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
     