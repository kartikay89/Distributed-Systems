import socket
import threading
import time

from networking import safe_print, PORT, MAX_MSG_SIZE


class Client(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier

    def c_print(self, s):
        safe_print('[CLIENT {:d}]: {:s}'.format(self.identifier, s))

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Prevent using 127.0.0.0 and 127.0.0.1 - I think those may be reserved
        host = '127.0.0.{:d}'.format(self.identifier + 2)
        while True:
            try:
                s.connect((host, PORT))
                break
            except:
                # Yield to whatever other thread is ready to run ('our' server isn't ready yet)
                time.sleep(0)
        
        s.send('<< Greetings from CLIENT {:d} >>'.format(self.identifier))
        reply = s.recv(MAX_MSG_SIZE)
        self.c_print('Got msg: {:s}'.format(reply))
        
        s.close()
        self.c_print('Stopped.')