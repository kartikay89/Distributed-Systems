import threading
import time

from networking import DEBUG_PRINT, GAME_SYNC_INTERVAL, \
                       Message, MessageType, \
                       safe_print

class GameSynchronizer(threading.Thread):
    def __init__(self, server, game, interval):
        threading.Thread.__init__(self)
        self.server = server
        self.game = game
        self.interval = interval

    def gs_print(self, s):
        if DEBUG_PRINT:
            safe_print('[GAMESYNCHRONIZER (game {:d}, server {:d})]: {:s}'.format(self.game.identifier, self.server.identifier, s))

    # Sends a list of all commands executed since the last synchronization round, to all other servers
    def send_sync(self):
        with self.game.buffer_lock:
            executed_commands = self.game.command_buffer
            self.game.command_buffer = []
        sync_message = Message(type=MessageType.GAME_SYNC, actions=executed_commands, game_id=self.game.identifier, host=self.server.host)
        for server in self.game.servers:
            if server != self.server.host:
                self.server.send_message(server, sync_message)

    def sync_state(self):
        # Retrieve sync messages received since the last synchronization round
        with self.game.sync_msg_lock:
            sync_messages = self.game.sync_messages
            self.game.sync_messages = []
        self.gs_print('Synchronizing (got the following: {:s}).'.format(sync_messages))

    def run(self):
        self.gs_print('Started.')
        sync_time = time.time() # This timestamp is used to determine when to sync
        send_time = sync_time + self.interval * 0.5 # This timestamp is used to determine when to send our own sync message

        while True:
            current_time = time.time()
            if current_time - send_time > self.interval:
                # Time to send our own synchronization message
                send_time = current_time
                self.send_sync()
            elif current_time - sync_time > self.interval:
                # Time to synchronize
                sync_time = current_time
                self.sync_state()
            # If our Client thread has told us to stop, we stop; otherwise, we yield to another thread
            with self.server.stop_lock:
                if self.server.stop:
                    self.gs_print('Stopped.')
                    return
            # Yield
            time.sleep(0)