import pickle
import socket
import threading
import time

from networking import DEBUG_PRINT, MAX_MSG_SIZE, \
                       Message, \
                       await_confirm, connect_to_dst, safe_print

# This class is used to send a single message, and wait for a confirmation without blocking the owner
class MessageSender(threading.Thread):
    def __init__(self, owner, timeout, host, port, message):
        threading.Thread.__init__(self)
        self.owner = owner
        self.timeout = timeout
        self.host = host
        self.port = port
        self.message = Message(message)

    def ms_print(self, s):
        if DEBUG_PRINT:
            safe_print('[MESSAGESENDER FOR {:d}]: {:s}'.format(self.owner.identifier, s))

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        if not connect_to_dst(self, s, (self.host, self.port), MessageSender.ms_print):
            return
        s.setblocking(0)
        # Pickle and send
        s.send(pickle.dumps(self.message))

        # Wait for confirmation
        if not await_confirm(self, s, self.host, MessageSender.ms_print):
            return
        s.close()