import socket
import threading

from networking import MAX_MSG_SIZE, DEBUG_PRINT, safe_print

# This class is used to receive messages from sockets without blocking the ServerListener
class MessageReceiver(threading.Thread):
    def __init__(self, server, sock, host, timeout, msgdict=None):
        threading.Thread.__init__(self)
        self.server = server
        self.sock = sock
        self.host = host
        self.timeout = timeout
        self.msgdict = msgdict

    def mr_print(self, s):
        if DEBUG_PRINT:
            safe_print('[MESSAGERECEIVER FOR {:d}]: {:s}'.format(self.server.identifier, s))

    def run(self):
        self.sock.settimeout(self.timeout)
        try:
            message = self.sock.recv(MAX_MSG_SIZE)
            # If we did not receive a reference to put the message in, just append to our server's message list
            if not self.msgdict:
                with self.server.message_lock:
                    self.server.messages.append(message)
            else:
                self.msgdict['msg'] = message
            # Always be polite
            self.sock.send('Thanks')
            self.mr_print('Got message {:s}'.format(message))
        except socket.timeout:
            self.mr_print('Timeout while trying to receive message from {:s}'.format(str(self.host)))
        self.sock.close()