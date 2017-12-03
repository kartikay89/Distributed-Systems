from collections import Counter
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
        self.sent_actions = [] # The list of actions we last sent to our peers
        self.disagreeing_servers = [] # List of servers that disagreed during the last synchronization step

    def gs_print(self, s):
        if DEBUG_PRINT:
            safe_print('[GAMESYNCHRONIZER (game {:d}, server {:d})]: {:s}'.format(self.game.identifier, self.server.identifier, s))

    # Sends a list of all commands executed since the last synchronization round, to all other servers
    # Also stores this list for later use during the synchronization step
    def send_sync(self):
        with self.game.buffer_lock:
            self.sent_actions = self.game.action_buffer
            self.game.action_buffer = []
        sync_message = Message(type=MessageType.GAME_SYNC, actions=self.sent_actions, checkpoint_id=self.game.checkpoint_nr, game_id=self.game.identifier, host=self.server.host)
        for server in self.game.servers:
            if server != self.server.host:
                self.server.send_message(server, sync_message)

    # Updates our game's checkpoint, given a list of actions
    def update_checkpoint(self, action_list):
        self.game.checkpoint_nr += len(action_list)
        self.gs_print('Updating checkpoint: id now {:d}, added actions {:s}'.format(self.game.checkpoint_nr, action_list))
        for action in action_list:
            self.game.checkpoint.perform_action(action)

    # Given a list of lists of actions, decides what that majority of servers 'voted' for
    # Also updates the game's checkpoint and checkpoint_nr
    def compare_action_lists(self, action_lists, action_list_servers):
        # We will compare the STRING representations for convenience, so this mapping is convenient for later
        comparison_data = [(str(action_list), action_list, server) for action_list, server in zip(action_lists, action_list_servers)]
        comparison_counter = Counter([cd[0] for cd in comparison_data])
        # Sort counting results and store in a list
        sorted_results = sorted(comparison_counter.items(), key=lambda x: x[1], reverse=True)
        
        # If all servers agree      or if we have 1 clear winner (no tie)...
        if len(sorted_results) == 1 or sorted_results[0][1] > sorted_results[1][1]:
            # Retrieve the original list of actions corresponding to this string representation
            definitive_actions = filter(lambda cd: cd[0] == sorted_results[0][0], comparison_data)[0][1]
            # Update checkpoint
            self.update_checkpoint(definitive_actions)
            return
        else:
            # Retrieve all winning options (strings)
            possible_action_strings = filter(lambda result: result[1] == sorted_results[0][1], sorted_results)
            # Retrieve the extra data corresponding the the string representations
            possible_action_data = filter(lambda cd: cd[0] in possible_action_strings, comparison_data)
            # Look at the servers' IP addresses: the server with the lowest last part of it's IP address (127.0.0.xxx) has the casting vote
            winning_action_data = min(possible_action_data, key=lambda x: int(x[2].split('.')[-1]))
            # Extract the list of GameAction objects
            definitive_actions = winning_action_data[1]
            # Update checkpoint
            self.update_checkpoint(definitive_actions)
            # Check if our own server agreed with this verdict
            if self.server.host not in [cd[2] for cd in comparison_data if cd[0] == winning_action_data[0]]:
                # It didn't, update our current game and notify our clients
                with self.game.buffer_lock:
                    # Create copy of new checkpoint
                    new_game = copy.copy(self.game.checkpoint)
                    # Apply operations that have not been sync'ed yet
                    for action in self.game.action_buffer:
                        new_game.perform_action(action)
                    # Replace game
                    self.game = new_game
                    with self.server.games_lock:
                        self.server.games[new_game.identifier] = new_game

    # Performs a synchronizations step as follows:
    # * Retrieves all synchronization messages that we have received since the previous step
    # * Also retrieves the list of actions we sent to our peers
    # * Looking at these lists of actions, checks if they match
    #   * If they do, updates the game's checkpoint
    #   * If they don't, decides which action list was supported by the most servers
    #       * If necessary, updates the current state and notifies our clients
    def sync_state(self):
        # Retrieve sync-messages received since the last synchronization round
        with self.game.sync_msg_lock:
            # Discard messages that are not part of the current synchronization step (due to timeouts)
            sync_messages = filter(lambda sm: sm.checkpoint_id == self.game.checkpoint_nr, self.game.sync_messages)
            self.game.sync_messages = []
        #self.gs_print('Synchronizing (got the following: {:s}).'.format(sync_messages))
        # All received lists of actions + our own list of actions for this synchronization step
        action_lists = [sm.actions for sm in sync_messages] + [self.sent_actions] #     [[GameAction 1, GameAction 2, ...], [GameAction 1, GameAction 2, ...],  ..., [our own actions]]
        # The servers that correspond to these action lists
        action_list_servers = [sm.host for sm in sync_messages] + [self.server.host] #  [server of first action list,       server of second action list,       ..., this server]
        # Find the length of the shortest list
        n_actions_to_check = len(min(action_lists, key=lambda x: len(x)))
        # All actions that won't be considered during this synchronization step are placed back in the game's action buffer
        with self.game.buffer_lock:
            self.game.action_buffer = self.sent_actions[n_actions_to_check:] + self.game.action_buffer
        # Ditch all surplus actions
        action_lists = [action_list[:n_actions_to_check] for action_list in action_lists]
        self.compare_action_lists(action_lists, action_list_servers)


    def run(self):
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