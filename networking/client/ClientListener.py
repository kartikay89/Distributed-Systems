import socket
import threading
import time
from networking import DEBUG_PRINT, LOCAL, MAX_MSG_SIZE, PORT, SOCKET_BACKLOG_SIZE, TIMEOUT, \
                       Message, MessageReceiver, \
                       safe_print


class ClientListener(threading.Thread):
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
        start_time = time.time()

        # Set up socket to listen for Ping broadcasts
        ping_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ping_s.setblocking(0)
        ping_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ping_s.bind(('', PORT))

        # Set up socket to receive messages from peers
        server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_s.bind((self.server.host, PORT))
        except:
            self.sl_print('Failed to bind, self.server.host = {:s}'.format(self.server.host))
            return
        server_s.setblocking(0)
        self.sl_print('listening on ' + self.server.host + ':' + str(PORT))

        server_s.listen(SOCKET_BACKLOG_SIZE)
        
        while True:
            # Stage 1: check for Pings, and reply
            try:
                # Check if there is a ping to reply to
                m, src = ping_s.recvfrom(MAX_MSG_SIZE)
                #self.sl_print('Message from {:s}: {:s}'.format(str(src), m))
                # 'host' is just the message content here, 'src' defines where we send it to
                ping_s.sendto(self.server.host, src)
            except:
                # Got no message, do nothing
                pass

            # Stage 2: Check for normal messages from our peers
            self.fetch_messages(server_s)

            # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.server.stop_lock:
                if self.server.stop:
                    ping_s.close()
                    server_s.close()
                    self.sl_print('Stopped.')
                    break
                else:
                    time.sleep(0)