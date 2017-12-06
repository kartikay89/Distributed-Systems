from Queue import Queue
import os
import sys
import Tkinter as tk

# Append current working directory to the paths in which Python looks for modules
sys.path.insert(0, os.path.abspath('..'))

import argparse

from networking import GRID_SIZE, \
                       Client, DASBoard, GameServer, HeadServer, Server, \
                       safe_print


# Use argparse to parse args (useful when we start having many of them)
def get_args():
    parser = argparse.ArgumentParser(description='Start a number of servers in an equal number of threads.')
    parser.add_argument('-n', '--number_servers', type=int, default=4, help='Number of servers to start')
    parser.add_argument('-c', '--number_clients', type=int, default=4, help='Number of clients to start')
    parser.add_argument('-v', '--verbose', action='store_true', help='Generate verbose output') # Not used yet, but can come in handy later
    return parser.parse_args()


def do_nothing(a):
    print a
    return a


if __name__ == '__main__':
    args = get_args()
    nservers = args.number_servers
    nclients = args.number_clients

    servers = []
    clients = []
    queues = []
    boards = []
    head_server = None

    root = tk.Tk()

    for i in range(nservers):
        if i == 0:
            head_server = HeadServer(i)
            head_server.start()
        else:
            servers.append(GameServer(i))
            servers[-1].start()

    for i in range(nclients):
        queues.append(Queue())
        clients.append(Client(i, queue=queues[-1]))
        clients[-1].start()
        if i == 0:
            board = DASBoard(root, 32, "Superman.png", "Dragon.png", board_size=(GRID_SIZE,GRID_SIZE))
        else:
            top_level = tk.Toplevel(root)
            board = DASBoard(top_level, 32, "Superman.png", "Dragon.png", board_size=(GRID_SIZE,GRID_SIZE))
        board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
        boards.append(board)

    while True:
        for i in range(len(boards)):
            units = None
            while not queues[i].empty():
                units = queues[i].get()
            if units:
                safe_print('Units: {:s}'.format(units))
                boards[i].update_units(units)
            boards[i].canvas.update_idletasks()
            boards[i].canvas.update()
