import pickle
import socket
import time

from networking import CONFIRM, MAX_MSG_SIZE


# Waits for a server to send us something
# Should be called with non-blocking socket
def await_reply(obj, s, host, printf):
    while True:
        try:
            pickled_reply = s.recv(MAX_MSG_SIZE)
            reply = pickle.loads(pickled_reply)
            return reply
        except socket.error as serr:
            # This is a non-blocking socket, so errno 11 (Resource unavailable) just means we should yield
            if serr.errno != 11:
                printf('Socket error receiving reply from {:s}: {:s}'.format(host, serr))
                return None
            time.sleep(0)
        #except Exception, e:
        #    printf(obj, 'Error receiving reply from {:s}: {:s}'.format(host, e))
        #    return None


# Waits for a server to confirm our previously sent message
# Should be called with non-blocking socket
def await_confirm(obj, s, host, printf):
    reply = str(await_reply(obj, s, host, printf))
    if reply == '':
        printf(obj, 'Error receiving confirmation from {:s}: Did not receive confirmation'.format(host))
        return False
    elif reply != CONFIRM:
        printf(obj, 'Error receiving confirmation from {:s}: Did not receive correct confirmation ("{:s}")'.format(host, reply))
        return False
    return True


# Connect to a given host; if the host is off line, yield CPU control
# Should be called with BLOCKING socket (non-blocking ones can give strange 115-errors)
def connect_to_dst(obj, s, host, printf):
    while True:
        try:
            s.connect(host)
            printf(obj, 'Connected')
            return True
        except socket.error as serr:
            if serr.errno == 111:
                # Yield to whatever other thread is ready to run (head server isn't ready yet)
                time.sleep(0)
            else:
                printf(obj, 'Error: {:s}'.format(serr))
                return False
        except Exception, e:
            printf(obj, 'Error: {:s}'.format(e))
            return False