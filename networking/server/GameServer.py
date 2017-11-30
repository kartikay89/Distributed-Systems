import time

from networking import PORT, Server

# This class is used for the worker servers that are used for hosting games
class GameServer(Server):
    def __init__(self, identifier):
        Server.__init__(self, identifier)

    def run(self):
        start_time = time.time()
        print_time = start_time
        current_time = print_time
        i = 0
        
        # Stop after 5 seconds
        while True:
            current_time = time.time()
            if current_time - start_time >= 5:
                with self.message_lock:
                    self.s_print(str(self.messages))
                    self.messages = []
                with self.stop_lock:
                    self.stop = True
                # Wait for our listener and broadcaster threads to quit
                self.server_listener.join()
                self.server_broadcaster.join()
                self.s_print('Stopped.')
                break
            elif current_time - print_time >= 1:
                print_time = current_time
                self.send_to_all('S{:d} M{:d}'.format(self.identifier, i))
                i += 1
                self.s_print(str(self.neighbours))
            else:
                time.sleep(0)
