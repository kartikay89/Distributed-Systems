#!/usr/bin/env python
""" generated source for module BattleField """
from __future__ import print_function
from functools import wraps
from threading import RLock

def lock_for_object(obj, locks={}):
    return locks.setdefault(id(obj), RLock())

def synchronized(call):
    assert call.__code__.co_varnames[0] in ['self', 'cls']
    @wraps(call)
    def inner(*args, **kwds):
        with lock_for_object(args[0]):
            return call(*args, **kwds)
    return inner

# package: distributed.systems.das
# 
#  * The actual battlefield where the fighting takes place.
#  * It consists of an array of a certain width and height.
#  * 
#  * It is a singleton, which can be requested by the 
#  * getBattleField() method. A unit can be put onto the
#  * battlefield by using the putUnit() method.
#  * 
#  * @author Pieter Anemaet, Boaz Pat-El
#  
class BattleField(IMessageReceivedHandler):
    """ generated source for class BattleField """
    #  The array of units 
    map = []

    #  The static singleton 
    battlefield = None

    #  Primary socket of the battlefield 
    serverSocket = None

    #  The last id that was assigned to an unit. This variable is used to
    # 	 * enforce that each unit has its own unique id.
    # 	 
    lastUnitID = 0
    serverID = "server"
    MAP_WIDTH = 25
    MAP_HEIGHT = 25
    units = None

    # 
    # 	 * Initialize the battlefield to the specified size 
    # 	 * @param width of the battlefield
    # 	 * @param height of the battlefield
    # 	 
    def __init__(self, width, height):
        """ generated source for method __init__ """
        super(BattleField, self).__init__()
        local = LocalSocket()
        with lock_for_object(self):
            self.map = [None] * width
            local.register(BattleField.serverID)
            self.serverSocket = SynchronizedSocket(local)
            self.serverSocket.addMessageReceivedHandler(self)
            self.units = ArrayList()

    # 
    # 	 * Singleton method which returns the sole 
    # 	 * instance of the battlefield.
    # 	 * 
    # 	 * @return the battlefield.
    # 	 
    @classmethod
    def getBattleField(cls):
        """ generated source for method getBattleField """
        if cls.battlefield == None:
            cls.battlefield = BattleField(cls.MAP_WIDTH, cls.MAP_HEIGHT)
        return cls.battlefield

    # 
    # 	 * Puts a new unit at the specified position. First, it
    # 	 * checks whether the position is empty, if not, it
    # 	 * does nothing.
    # 	 * In addition, the unit is also put in the list of known units.
    # 	 * 
    # 	 * @param unit is the actual unit being spawned 
    # 	 * on the specified position.
    # 	 * @param x is the x position.
    # 	 * @param y is the y position.
    # 	 * @return true when the unit has been put on the 
    # 	 * specified position.
    # 	 
    def spawnUnit(self, unit, x, y):
        """ generated source for method spawnUnit """
        with lock_for_object(self):
            if self.map[x][y] != None:
                return False
            self.map[x][y] = unit
            unit.setPosition(x, y)
        self.units.add(unit)
        return True

    @synchronized
    def putUnit(self, unit, x, y):
        """ generated source for method putUnit """
        if self.map[x][y] != None:
            return False
        self.map[x][y] = unit
        unit.setPosition(x, y)
        return True

    def getUnit(self, x, y):
        """ generated source for method getUnit """
        assert x >= 0 and len(map)
        assert y >= 0 and len(length)
        return self.map[x][y]

    @synchronized
    def moveUnit(self, unit, newX, newY):
        """ generated source for method moveUnit """
        originalX = unit.getX()
        originalY = unit.getY()
        if unit.getHitPoints() <= 0:
            return False
        if newX >= 0 and newX < BattleField.MAP_WIDTH:
            if newY >= 0 and newY < BattleField.MAP_HEIGHT:
                if self.map[newX][newY] == None:
                    if self.putUnit(unit, newX, newY):
                        self.map[originalX][originalY] = None
                        return True
        return False

    @synchronized
    def removeUnit(self, x, y):
        """ generated source for method removeUnit """
        unitToRemove = self.getUnit(x, y)
        if unitToRemove == None:
            return
        self.map[x][y] = None
        unitToRemove.disconnect()
        self.units.remove(unitToRemove)

    @synchronized
    def getNewUnitID(self):
        """ generated source for method getNewUnitID """
        return self.lastUnitID += 1

    def onMessageReceived(self, msg):
        """ generated source for method onMessageReceived """
        reply = None
        origin = str(msg.get("origin"))
        request = msg.get("request")
        unit = None
        if request == self.spawnUnit:
            self.spawnUnit(msg.get("unit"), int(msg.get("x")), int(msg.get("y")))
        elif request == self.putUnit:
            self.putUnit(msg.get("unit"), int(msg.get("x")), int(msg.get("y")))
        elif request == self.getUnit:
            reply = Message()
            x = int(msg.get("x"))
            y = int(msg.get("y"))
            reply.put("id", msg.get("id"))
            reply.put("unit", self.getUnit(x, y))
        elif request == getType:
            reply = Message()
            x = int(msg.get("x"))
            y = int(msg.get("y"))
            reply.put("id", msg.get("id"))
            if isinstance(, (Player, )):
                reply.put("type", UnitType.player)
            elif isinstance(, (Dragon, )):
                reply.put("type", UnitType.dragon)
            else:
                reply.put("type", UnitType.undefined)
        elif request == dealDamage:
            x = int(msg.get("x"))
            y = int(msg.get("y"))
            unit = self.getUnit(x, y)
            if unit != None:
                unit.adjustHitPoints(-int(msg.get("damage")))
        elif request == healDamage:
            x = int(msg.get("x"))
            y = int(msg.get("y"))
            unit = self.getUnit(x, y)
            if unit != None:
                unit.adjustHitPoints(int(msg.get("healed")))
        elif request == self.moveUnit:
            reply = Message()
            self.moveUnit(msg.get("unit"), int(msg.get("x")), int(msg.get("y")))
            reply.put("id", msg.get("id"))
        elif request == self.removeUnit:
            self.removeUnit(int(msg.get("x")), int(msg.get("y")))
            return
        try:
            if reply != None:
                self.serverSocket.sendMessage(reply, origin)
        except IDNotAssignedException as idnae:
            pass

    @synchronized
    def shutdown(self):
        """ generated source for method shutdown """
        for unit in units:
            unit.disconnect()
            unit.stopRunnerThread()
        self.serverSocket.unRegister()

# WARNING runTransform: Generated source has invalid syntax. invalid syntax (<string>, line 144)
