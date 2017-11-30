import time

from networking import PORT, Server, safe_print

# This class is used for the worker servers that are used for hosting games
class GameServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)

    def s_print(self, s):
        safe_print('[GAMESERVER {:d}]: {:s}'.format(self.identifier, s))

    def handle_messages(self):
        with self.message_lock:
            for message in self.messages:
                self.s_print('Received message {:s}'.format(message))
                message._reply_socket.close()
            self.messages = []

    def run(self):
        start_time = time.time()
        print_time = start_time
        current_time = print_time
        
        # Stop after 5 seconds
        while True:
            current_time = time.time()
            self.handle_messages()
            if current_time - start_time >= 5:
                with self.stop_lock:
                    self.stop = True
                # Wait for our listener and broadcaster threads to quit
                self.server_listener.join()
                self.server_broadcaster.join()
                self.s_print('Stopped.')
                return
            elif current_time - print_time >= 1:
                print_time = current_time
                self.s_print(str(self.neighbours))
            else:
                time.sleep(0)
