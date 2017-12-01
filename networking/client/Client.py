import pickle
import socket
import threading
import time

from networking import safe_print, CLIENT_PORT, MAX_MSG_SIZE, HEADSERVER_IP, Message, await_confirm, await_reply, connect_to_dst


class Client(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier
        self.server_host = None

    def c_print(self, s):
        safe_print('[CLIENT {:d}]: {:s}'.format(self.identifier, s))

    # Sends a message through socket s, indicating the client wishes to join a game
    def request_join(self, s):
        message = Message(type='GAME_JOIN', client=True)
        s.send(pickle.dumps(message))
        if not await_confirm(self, s, HEADSERVER_IP, Client.c_print):
            return False
        reply = await_reply(self, s, HEADSERVER_IP, Client.c_print)
        if reply == None:
            return False
        self.c_print('Got second reply: {:s}'.format(reply))
        return True

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not connect_to_dst(self, s, (HEADSERVER_IP, CLIENT_PORT), Client.c_print):
            return
        s.setblocking(0)
        if not self.request_join(s):
            return
        s.close()
        self.c_print('Stopped.')