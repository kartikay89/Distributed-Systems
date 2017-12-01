import pickle
import socket
import threading

from networking import CONFIRM, DEBUG_PRINT, MAX_MSG_SIZE, \
                       Message, \
                       safe_print

# This class is used to receive messages from sockets without blocking the ServerListener
class MessageReceiver(threading.Thread):
    def __init__(self, owner, sock, host, timeout):
        threading.Thread.__init__(self)
        self.owner = owner
        self.sock = sock
        self.host = host
        self.timeout = timeout

    def mr_print(self, s):
        if DEBUG_PRINT:
            safe_print('[MESSAGERECEIVER FOR {:d}]: {:s}'.format(self.owner.identifier, s))

    def run(self):
        self.sock.settimeout(self.timeout)
        try:
            pickled_message = self.sock.recv(MAX_MSG_SIZE)
            message = pickle.loads(pickled_message)
            message._reply_socket = self.sock
            # Send confirmation
            self.sock.send(pickle.dumps(Message(CONFIRM)))
            # Append to message buffer
            with self.owner.message_lock:
                self.owner.messages.append(message)
            # If the message was sent by a client, update client
            if message.client:
                with self.owner.clients_lock:
                    if message.host not in self.owner.clients:
                        self.owner.clients.append(message.host)
        except Exception, e:
            self.mr_print('Error while trying to receive message from {:s}: {:s}'.format(str(self.host), e))