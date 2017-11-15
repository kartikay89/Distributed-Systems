import sys

# When multiple threads are printing at the same time, the newlines are not printed at the same moment as the string
# This function takes care of this. Alternatively just call sys.stdout.write(<...>)
def safe_print(s):
    sys.stdout.write(s + '\n')


class Server(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def run(self):
        safe_print('Server {:d} running'.format(self.identifier))

    def stop(self):
        safe_print('Server {:d} stopped'.format(self.identifier))