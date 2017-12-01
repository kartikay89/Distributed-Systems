import socket
import threading
import time
from networking import DEBUG_PRINT, LOCAL, MAX_MSG_SIZE, PORT, SOCKET_BACKLOG_SIZE, TIMEOUT, \
                       Message, MessageReceiver, \
                       safe_print


class ClientListener(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def cl_print(self, s):
        if DEBUG_PRINT:
            safe_print('[CLIENTLISTENER {:d}]: {:s}'.format(self.client.identifier, s))

    # Fetch all messages that have been sent to the client since the last time we checked
    def fetch_messages(self, s):
        while True:
            try:
                sock, host = s.accept()
                MessageReceiver(self.client, sock, host, TIMEOUT).start()
            except:
                break

    def run(self):
        # Setup socket to listen with
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((self.client.host, PORT))
        except Exception, e:
            self.cl_print('failed to bind, self.client.host = {:s} ({:s})'.format(self.client.host, e))
            return
        s.setblocking(0)
        self.cl_print('listening on {:s}:{:d}'.format(self.client.host, PORT))

        s.listen(SOCKET_BACKLOG_SIZE)
        
        while True:
            # Check for messages from servers
            self.fetch_messages(s)

            # If our Client thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.client.stop_lock:
                if self.client.stop:
                    s.close()
                    self.cl_print('Stopped.')
                    return
            # Yield
            time.sleep(0)