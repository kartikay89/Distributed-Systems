import pickle
import socket
import threading

from networking import MAX_MSG_SIZE, DEBUG_PRINT, CONFIRM, safe_print, Message

# This class is used to receive messages from sockets without blocking the ServerListener
class MessageReceiver(threading.Thread):
    def __init__(self, server, sock, host, timeout):
        threading.Thread.__init__(self)
        self.server = server
        self.sock = sock
        self.host = host
        self.timeout = timeout

    def mr_print(self, s):
        if DEBUG_PRINT:
            safe_print('[MESSAGERECEIVER FOR {:d}]: {:s}'.format(self.server.identifier, s))

    def run(self):
        self.sock.settimeout(self.timeout)
        try:
            pickled_message = self.sock.recv(MAX_MSG_SIZE)
            message = pickle.loads(pickled_message)
            message._reply_socket = self.sock
            # Append to message buffer
            with self.server.message_lock:
                self.server.messages.append(message)
            # Update client list if necessary
            if message.client:
                with self.server.clients_lock:
                    if self.host not in self.server.clients:
                        self.server.clients.append(self.host)
            # Send confirmation
            self.sock.send(pickle.dumps(Message(CONFIRM)))
            self.mr_print('Got message {:s}'.format(message))
        except Exception, e:
            self.mr_print('Error while trying to receive message from {:s}: {:s}'.format(str(self.host), e))