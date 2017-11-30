import os, sys

# Append current working directory to the paths in which Python looks for modules
sys.path.insert(0, os.path.abspath('..'))

import argparse

from networking import Server, GameServer, HeadServer, Client


# Use argparse to parse args (useful when we start having many of them)
def get_args():
    parser = argparse.ArgumentParser(description='Start a number of servers in an equal number of threads.')
    parser.add_argument('-n', '--number', type=int, default=4, help='Number of servers to start')
    parser.add_argument('-v', '--verbose', action='store_true', help='Generate verbose output') # Not used yet, but can come in handy later
    return parser.parse_args()


def do_nothing(a):
    print a
    return a


if __name__ == '__main__':
    args = get_args()
    nservers = args.number

    servers = []
    clients = []
    head_server = None

    for i in range(nservers):
        if i == 0:
            head_server = HeadServer(i)
            head_server.start()
        else:
            servers.append(GameServer(i))
            servers[-1].start()

    for i in range(1):
        clients.append(Client(i))
        clients[-1].start()
