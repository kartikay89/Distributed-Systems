import os, sys

# Append current working directory to the paths in which Python looks for modules
sys.path.insert(0, os.path.abspath('..'))

import argparse
from multiprocessing.dummy import Pool as ThreadPool

from networking import Server


# Use argparse to parse args (useful when we start having many of them)
def get_args():
    parser = argparse.ArgumentParser(description='Start a number of servers in an equal number of threads.')
    parser.add_argument('-n', '--number', type=int, default=4, help='Number of servers to start')
    parser.add_argument('-v', '--verbose', action='store_true', help='Generate verbose output') # Not used yet, but can come in handy later
    return parser.parse_args()


def run_server(identifier):
    s = Server(identifier)
    s.run()
    s.stop()
    return s.identifier


if __name__ == '__main__':
    args = get_args()
    nservers = args.number
    pool = ThreadPool(nservers)
    ids = list(range(nservers))
    results = pool.map(run_server, ids)
    print ids
    print results