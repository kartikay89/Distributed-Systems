from Queue import Queue
import time
import sys
sys.path.append("/home/abel/Studie/Master/Distributed_Systems/Distributed-Systems/")

from tkintertinkering import Test


if __name__ == '__main__':
    t = []
    q = []
    for i in range(int(sys.argv[1])):
        q.append(Queue())
        t.append(Test(i, q[-1]))
        t[-1].start()

    time.sleep(1)
    for q_ in q:
        q_.put([("player1", "player", (1, 0))])
    time.sleep(1)
    for q_ in q:
        q_.put([("player1", "player", (1, 0)), ("player2", "player", (2, 0))])