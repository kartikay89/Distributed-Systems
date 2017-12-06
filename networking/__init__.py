import sys

# Set to True when the servers are run on a single machine, in threads.
# Set to False if the servers are running on actual machines
LOCAL               = True
PORT                = 50000 # For server-server communication
CLIENT_PORT         = 50001 # For client-server communication
MAX_MSG_SIZE        = 4096
SOCKET_BACKLOG_SIZE = 1024
TIMEOUT             = 1.0   # In seconds
HEADSERVER_IP       = '127.0.0.250'
#DEBUG_PRINT        = False
DEBUG_PRINT         = True
CONFIRM             = 'Thanks'
END_OF_MSG          = '\nEOM\n'
NSERVERS_PER_GAME   = 2
GAME_SYNC_INTERVAL  = 1.0 # Should eventually be made smaller
GRID_SIZE           = 25

# When multiple threads are printing at the same time, the newlines are not printed at the same moment as the string
# This function takes care of this. Alternatively, just call sys.stdout.write(<...>)
def safe_print(s):
    sys.stdout.write(s + '\n')
    sys.stdout.flush()

from helper_functions import await_confirm, await_reply, connect_to_dst
from Message import MessageType, Message
from MessageReceiver import MessageReceiver
from MessageSender import MessageSender
from GameAction import GameActionType, GameAction
from GameSynchronizer import GameSynchronizer
from DummyGame import DummyGame, Dragon, Player
from server.ServerListener import ServerListener
from server.HeadServerListener import HeadServerListener
from server.ServerBroadcaster import ServerBroadcaster
from server.Server import Server
from server.GameServer import GameServer
from server.HeadServer import HeadServer
from client.ClientListener import ClientListener
from client.DASBoard import DASBoard
from client.Client import Client