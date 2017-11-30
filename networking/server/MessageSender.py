import socket
import threading

from networking import MAX_MSG_SIZE, DEBUG_PRINT, safe_print

# This class is used to send a message, and wait for a confirmation without blocking the server
class MessageSender(threading.Thread):
    def __init__(self, server, timeout, host, port, message):
        threading.Thread.__init__(self)
        self.server = server
        self.timeout = timeout
        self.host = host
        self.port = port
        self.message = message

    def ms_print(self, s):
        if DEBUG_PRINT:
            safe_print('[MESSAGESENDER FOR {:d}]: {:s}'.format(self.server.identifier, s))

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        # Connect
        try:
            s.connect((self.host, self.port))
        except:
            self.ms_print('Failed to connect to {:s}'.format(self.host))
            return
        # Send
        s.send(self.message)
        # Wait for confirmation
        try:
            reply = s.recv(MAX_MSG_SIZE)
            if reply == '':
                raise Exception('Did not receive confirmation')
            elif reply != 'Thanks':
                raise Exception('Did not receive correct confirmation ("{:s}")'.format(reply))
        except Exception, e:
            self.ms_print('Error receiving confirmation from {:s}:'.format(self.host))
            self.ms_print(e)
        s.close()