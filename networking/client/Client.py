import socket
import threading
import time

from networking import safe_print, CLIENT_PORT, MAX_MSG_SIZE, HEADSERVER_IP


class Client(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier

    def c_print(self, s):
        safe_print('[CLIENT {:d}]: {:s}'.format(self.identifier, s))

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                s.connect((HEADSERVER_IP, CLIENT_PORT))
                break
            except:
                # Yield to whatever other thread is ready to run ('our' server isn't ready yet)
                time.sleep(0)
        self.c_print('Connected')
        s.send('CLIENT {:d}'.format(self.identifier))
        reply = None

        try:
            reply = s.recv(MAX_MSG_SIZE)
            if reply == '':
                raise Exception('Did not receive confirmation')
            elif reply != 'Thanks':
                raise Exception('Did not receive correct confirmation ("{:s}")'.format(reply))
        except Exception, e:
            self.c_print('Error receiving confirmation from {:s}:'.format(HEADSERVER_IP))
            self.c_print(e)
        self.c_print('Got msg: {:s}'.format(reply))
        
        s.close()
        self.c_print('Stopped.')