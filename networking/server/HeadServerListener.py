import socket
import threading
import time

from networking import TIMEOUT, DEBUG_PRINT, CLIENT_PORT, HEADSERVER_IP, SOCKET_BACKLOG_SIZE, safe_print, MessageReceiver


class HeadServerListener(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def hsl_print(self, s):
        if DEBUG_PRINT:
            safe_print('[HEADSERVERLISTENER {:d}]: {:s}'.format(self.server.identifier, s))

    def find_new_clients(self, s):
        while True:
            try:
                sock, host = s.accept()
                # MessageReceiver will put the message in msgdict['msg']
                msgdict = {}
                MessageReceiver(self.server, sock, host, TIMEOUT, msgdict).start()
                self.hsl_print('Found client at {:s}, msgdict {:s}'.format(str(host), str(msgdict)))
            except Exception, e:
                if 'Errno 11' not in str(e):
                    self.hsl_print(e)
                break

    def run(self):
        # Set up socket to receive messages from peers
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HEADSERVER_IP, CLIENT_PORT))
        s.setblocking(0)
        self.hsl_print('listening on ' + HEADSERVER_IP + ':' + str(CLIENT_PORT))

        s.listen(SOCKET_BACKLOG_SIZE)
        
        while True:
            # Check for connection attempts from clients
            self.find_new_clients(s)
            # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.server.stop_lock:
                if self.server.stop:
                    s.close()
                    self.hsl_print('Stopped.')
                    break
                else:
                    time.sleep(0)