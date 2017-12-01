import socket
import threading
import time

from networking import CLIENT_PORT, DEBUG_PRINT, LOCAL, MAX_MSG_SIZE, PORT, SOCKET_BACKLOG_SIZE, TIMEOUT, \
                       Message, MessageReceiver, \
                       safe_print


class ServerListener(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def sl_print(self, s):
        if DEBUG_PRINT:
            safe_print('[SERVERLISTENER {:d}]: {:s}'.format(self.server.identifier, s))

    # Fetch all messages that have been sent to the server since the last time we checked
    def fetch_messages(self, s):
        while True:
            try:
                sock, host = s.accept()
                MessageReceiver(self.server, sock, host, TIMEOUT).start()
            except:
                break

    def run(self):
        # Set up socket to listen for Ping broadcasts
        ping_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ping_s.setblocking(0)
        ping_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ping_s.bind(('', PORT))

        # Set up socket to receive messages from peers
        peer_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            peer_s.bind((self.server.host, PORT))
            client_s.bind((self.server.host, CLIENT_PORT))
        except Exception, e:
            self.sl_print('failed to bind ({:s})'.format(e))
            return
        peer_s.setblocking(0)
        client_s.setblocking(0)
        self.sl_print('listening on {:s}:{:d} and {:s}:{:d}'.format(self.server.host, PORT, self.server.host, CLIENT_PORT))
        peer_s.listen(SOCKET_BACKLOG_SIZE)
        client_s.listen(SOCKET_BACKLOG_SIZE)
        
        while True:
            # Stage 1: check for pings, and reply
            try:
                # Check if there is a ping to reply to
                m, src = ping_s.recvfrom(MAX_MSG_SIZE)
                # 'self.server.host' is just the message content here, 'src' defines where we send it to
                ping_s.sendto(self.server.host, src)
            except:
                # Got no message, do nothing
                pass

            # Stage 2: Check for normal messages
            self.fetch_messages(peer_s)
            self.fetch_messages(client_s)

            # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.server.stop_lock:
                if self.server.stop:
                    ping_s.close()
                    peer_s.close()
                    client_s.close()
                    self.sl_print('Stopped.')
                    return
            time.sleep(0)