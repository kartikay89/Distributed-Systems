import pickle
import socket
import threading
import time

from networking import CLIENT_PORT, HEADSERVER_IP, LOCAL, MAX_MSG_SIZE, \
					   ClientListener, Message, \
					   await_confirm, await_reply, connect_to_dst, safe_print


class Client(threading.Thread):
    def __init__(self, identifier):
        threading.Thread.__init__(self)
        self.identifier = identifier
        # Determine what IP to bind our sockets to
        if not LOCAL:
            self.host = socket.gethostname()
        else:
        	# Client address space: 127.0.1.x
            self.host = '127.0.1.{:d}'.format(self.identifier + 3)
        self.server_host = None

        # A lock-protected variable used to communicate that this thread is stopping (used by the client's listener)
        self.stop_lock = threading.RLock()
        self.stop = False

        # A lock-protected buffer for incoming messages
        self.message_lock = threading.RLock()
        self.messages = []

        self.client_listener = ClientListener(self)
        self.client_listener.start()

    def c_print(self, s):
        safe_print('[CLIENT {:d}]: {:s}'.format(self.identifier, s))

    def handle_messages(self):
    	with self.message_lock:
    		for message in self.messages:
    			if message.type == 'DRAW':
    				pass
    			else:
    				self.c_print('Got message: {:s}'.format(message))
    		self.messages = []

    # Sends a message through socket s, indicating the client wishes to join a game
    def request_join(self, s):
        message = Message(type='GAME_JOIN', client=True, host=self.host)
        s.send(pickle.dumps(message))
        if not await_confirm(self, s, HEADSERVER_IP, Client.c_print):
            return False
        reply = await_reply(self, s, HEADSERVER_IP, Client.c_print)
        if reply == None:
            return False
        if reply.type == 'REDIRECT':
        	self.server_host = reply.host
        else:
        	self.c_print('Got reply that was not a redirect! ({:s})'.format(reply))
        	return False
        return True

    def run(self):
    	start_time = time.time()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not connect_to_dst(self, s, (HEADSERVER_IP, CLIENT_PORT), Client.c_print):
            return
        s.setblocking(0)
        if not self.request_join(s):
            return
        self.c_print('We can join server {:s}'.format(self.server_host))
        while True:
        	self.handle_messages()
        	# Run for 5 seconds
        	if time.time() - start_time >= 5:
        		with self.stop_lock:
        			self.stop = True
	        		s.close()
	        		self.c_print('Stopped.')
	        		return
	        time.sleep(0)