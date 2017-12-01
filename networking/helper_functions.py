import pickle
import socket
import time

from networking import CONFIRM, END_OF_MSG, MAX_MSG_SIZE


# Waits for a non-blocking socket to be filled with something
# Guarantees that we return at least one complete message.
# If 'multiple_messages' is set, (always) returns a list of messages. 
# If it is False, it returns a single message (or raises an Exception if we received more than 1).
def await_reply(obj, s, host, printf, multiple_messages=False):
    result = ''
    split_messages = lambda msg: filter(None, msg.split(END_OF_MSG))
    while True:
        try:
            result += s.recv(MAX_MSG_SIZE)
            if not result.endswith(END_OF_MSG):
                continue
            split_result = split_messages(result)
            if multiple_messages:
                return [pickle.loads(message) for message in split_result]
            elif len(split_result) > 1:
                raise Exception('Got more than one message')
            return pickle.loads(split_result[0])
        except socket.error as serr:
            # This is a non-blocking socket, so errno 11 (Resource unavailable) just means we should yield
            if serr.errno != 11:
                printf(obj, 'Socket error receiving reply from {:s}: {:s}'.format(host, serr))
                return None
            time.sleep(0)


# Waits for a server to confirm our previously sent message
# Should be called with non-blocking sockets
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