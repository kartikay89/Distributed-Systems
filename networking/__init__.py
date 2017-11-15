import sys

# Set to True when the servers are run on a single machine, in threads.
# Set to False if the servers are running on actual machines
LOCAL = True
PORT = 50000
MAX_MSG_SIZE = 4096

# When multiple threads are printing at the same time, the newlines are not printed at the same moment as the string
# This function takes care of this. Alternatively just call sys.stdout.write(<...>)
def safe_print(s):
    sys.stdout.write(s + '\n')

from server.ServerListener import ServerListener
from server.ServerBroadcaster import ServerBroadcaster
from server.Server import Server
from client.Client import Client