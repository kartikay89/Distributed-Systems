import pickle
import socket
import threading

from networking import CONFIRM, DEBUG_PRINT, END_OF_MSG, \
                       Message, \
                       await_reply, safe_print

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
            safe_print('[MESSAGERECEIVER FOR {:s}]: {:s}'.format(self.owner.host, s))

    def run(self):
        self.sock.settimeout(self.timeout)
        try:
            message = await_reply(self, self.sock, self.host, MessageReceiver.mr_print)
            #self.mr_print('We got {:s}'.format(message))
            # Send confirmation
            self.sock.send(pickle.dumps(Message(CONFIRM)) + END_OF_MSG)
            # Append to message buffer
            with self.owner.message_lock:
                self.owner.messages.append(message)
        except Exception, e:
            self.mr_print('Error while trying to receive message from {:s}: {:s}'.format(str(self.host), e))