class MessageRequest(object):
    spawnUnit, getUnit, dealDamage, removeUnit = range(4)


class Message(object):
    def __init__(self, *args, **kwargs):
        # Make the Message look like a string if we supply a string as its first and only non-keyword arg
        if len(args) == 1:
            self.__dict__['__stringdata'] = args[0];
        elif len(args) > 1:
            raise Exception('Message constructor takes at most 1 positional parameter')
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __repr__(self):
        if '__stringdata' in self.__dict__:
            return self.__dict__['__stringdata']
        else:
            return '[MESSAGE: {:s}]'.format(str(self.__dict__))

    # Called when an attribute should be set
    #def __setattr__(self, name, value):
    #    self.__dict__[name] = value
