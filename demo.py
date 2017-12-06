import csv

from time import sleep

input_name ="/home/thomas/Documents/vu/distributed_systems/Distributed-Systems/output.csv"
limit = 10
tickrate = 1

if __name__ == '__main__':
    index = 0
    currenttime = 0
    with open(input_name) as f:
        reader = csv.reader(f)

        sortedlist = sorted(reader, key=lambda x: int(x[1]))

        for row in sortedlist:
            clientid = int(row[0])
            starttime = int(row[1])
            lifetime = int(row[2])

            ### We can sleep and then spawn clients, or...
            # while(currenttime < starttime):
            #     sleep(tickrate)
            #     currenttime += tickrate

            # print("starting clientid %2d at time %2d" % (clientid, currenttime))


            ### ... We can create client in one go and pass the sleeping time to them
            client = Client(clientid, starttime, lifetime)