import abc
from _thread import RLock
import pprint
from threading import Thread

import time

from Message import Message, MessageRequest


class Direction:
    up, right, down, left = range(4)


class UnitType:
    player, dragon, undefined = range(3)


def lock_for_object(obj, locks={}):
    return locks.setdefault(id(obj), RLock())


class Unit(abc.ABC):
    def __init__(self, maxHealth, attackPoints):
        self.x = None
        self.y = None
        self.maxHealth = maxHealth
        self.hitPoints = self.maxHitPoints = maxHealth
        self.attackPoints = attackPoints

        #  Is used for mapping an unique id to a message sent by this unit
        self.localMessageCounter = 0

        # Store received messages, key: id, value: return message
        self.messageList = {}

    def sendMessage(self, message):
        # TODO implement socket etc
        # self.clientSocket.sendMessage "localsocket://" + BattleField.serverID)
        pprint.pprint(message.d, indent=4)

        return

        # TODO throw exceptions when applicable
        raise ValueError('No server found while spawning unit', x, y)

    #
    # 	 * Set the position of the unit.
    # 	 * @param x is the new x coordinate
    # 	 * @param y is the new y coordinate
    #
    def setPosition(self, x, y):
        self.x = x
        self.y = y

    #
    # 	 * Tries to make the unit spawn at a certain location on the battlefield
    # 	 * @param x x-coordinate of the spawn location
    # 	 * @param y y-coordinate of the spawn location
    # 	 * @return true iff the unit could spawn at the location on the battlefield
    #
    def spawn(self, x, y):
        #  Create a new message, notifying the board
        # 		 * the unit has actually spawned at the
        # 		 * designated position.
        #
        id = self.localMessageCounter
        self.localMessageCounter += 1
        spawnMessage = Message()
        spawnMessage.put("request", MessageRequest.spawnUnit)
        spawnMessage.put("x", x)
        spawnMessage.put("y", y)
        spawnMessage.put("unit", self)
        spawnMessage.put("id", id)
        #  Send a spawn message
        try:
            self.sendMessage(spawnMessage)
        except ValueError as e:
            print(e.args)
            return False
        # Wait for the unit to be placed
        self.getUnit(x, y)
        return True

    def getUnit(self, x, y):
        getMessage = Message()
        result = None
        id = self.localMessageCounter
        self.localMessageCounter += 1
        getMessage.put("request", MessageRequest.getUnit)
        getMessage.put("x", x)
        getMessage.put("y", y)
        getMessage.put("id", id)
        #  Send the getUnit message
        self.sendMessage(getMessage)
        #  Wait for the reply
        while id not in self.messageList:
            try:
                print("messageList:")
                pprint.pprint(self.messageList)
                print("sleep start")
                time.sleep(1)
                print("sleep end")
            # TODO was exceptionError, need to look into that if it's useful
            except ValueError as e:
                pass
            # Quit if the game window has closed
            # TODO re-enable once we have GameState
            # if not GameState.getRunningState():
            #     return None
        result = self.messageList.get(id)
        self.messageList.put(id, None)
        return result.get("unit")

    def adjustHitPoints(self, modifier):
        if self.hitPoints <= 0:
            return

        self.hitPoints += modifier
        if self.hitPoints > self.maxHitPoints:
            self.hitPoints = self.maxHitPoints
        if self.hitPoints <= 0:
            self.removeUnit(self.x, self.y)

    def dealDamage(self, x, y, damage):
        """ generated source for method dealDamage """
        #  Create a new message, notifying the board
        # 		 * that a unit has been dealt damage.
        #
        __localMessageCounter_0 = self.localMessageCounter
        self.localMessageCounter += 1
        with lock_for_object(self):
            id = __localMessageCounter_0
            damageMessage = Message()
            damageMessage.put("request", MessageRequest.dealDamage)
            damageMessage.put("x", x)
            damageMessage.put("y", y)
            damageMessage.put("damage", damage)
            damageMessage.put("id", id)
        # Send a spawn message
        self.sendMessage(damageMessage)

    def removeUnit(self, x, y):
        """ generated source for method removeUnit """
        removeMessage = Message()
        id = self.localMessageCounter
        self.localMessageCounter += 1
        removeMessage.put("request", MessageRequest.removeUnit)
        removeMessage.put("x", x)
        removeMessage.put("y", y)
        removeMessage.put("id", id)
        #  Send the removeUnit message
        self.sendMessage(removeMessage)

    @abc.abstractmethod
    def hi(self):
        pass
