import pickle
import socket
import threading
import time

from networking import DEBUG_PRINT, MAX_MSG_SIZE, Message, await_confirm, safe_print

# This class is used to send a message, and wait for a confirmation without blocking the server
class MessageSender(threading.Thread):
    def __init__(self, server, timeout, host, port, message):
        threading.Thread.__init__(self)
        self.server = server
        self.timeout = timeout
        self.host = host
        self.port = port
        self.message = Message(message)

    def ms_print(self, s):
        if DEBUG_PRINT:
            safe_print('[MESSAGESENDER FOR {:d}]: {:s}'.format(self.server.identifier, s))

    # Wrapper function for connecting to our destination
    def connect_to_dst(self, s):
        try:
            s.connect((self.host, self.port))
            return True
        except Exception, e:
            self.ms_print('Failed to connect to {:s}: {:s}'.format(self.host, e))
            return False

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        if not self.connect_to_dst(s):
            return
        s.setblocking(0)
        # Pickle and send
        s.send(pickle.dumps(self.message))

        # Wait for confirmation
        if not await_confirm(self, s, self.host, MessageSender.ms_print):
            return
        s.close()