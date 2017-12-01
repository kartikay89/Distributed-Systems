#!/usr/bin/env python
""" generated source for module Core """
from __future__ import print_function
# package: distributed.systems.das
# 
#  * Controller part of the DAS game. Initializes 
#  * the viewer, adds 20 dragons and 100 players. 
#  * Once every 5 seconds, another player is added
#  * to simulate a connecting client.
#  *  
#  * @author Pieter Anemaet, Boaz Pat-El
#  
class Core(object):
    """ generated source for class Core """
    MIN_PLAYER_COUNT = 30
    MAX_PLAYER_COUNT = 60
    DRAGON_COUNT = 20
    TIME_BETWEEN_PLAYER_LOGIN = 5000

    #  In milliseconds
    battlefield = None
    playerCount = int()

    @classmethod
    def main(cls, args):
        """ generated source for method main """
        cls.battlefield = BattleField.getBattleField()
        #  All the dragons connect 
        i = 0
        while i < cls.DRAGON_COUNT:
            #  Try picking a random spot 
            x = int()
            y = int()
            attempt = 0
            while True:
                x = int((random() * BattleField.MAP_WIDTH))
                y = int((random() * BattleField.MAP_HEIGHT))
                attempt += 1
                if not ((cls.battlefield.getUnit(x, y) != None and attempt < 10)):
                    break
            #  If we didn't find an empty spot, we won't add a new dragon
            if cls.battlefield.getUnit(x, y) != None:
                break
            finalX = x
            finalY = y
            #  Create the new dragon in a separate
            # 			 * thread, making sure it does not 
            # 			 * block the system.
            # 			 
            Thread(Runnable()).start()
            i += 1
        #  Initialize a random number of players (between [MIN_PLAYER_COUNT..MAX_PLAYER_COUNT] 
        cls.playerCount = int(((cls.MAX_PLAYER_COUNT - cls.MIN_PLAYER_COUNT) * random() + cls.MIN_PLAYER_COUNT))
        i = 0
        while i < cls.playerCount:
            #  Once again, pick a random spot 
            x = int()
            y = int()
            attempt = 0
            while True:
                x = int((random() * BattleField.MAP_WIDTH))
                y = int((random() * BattleField.MAP_HEIGHT))
                attempt += 1
                if not ((cls.battlefield.getUnit(x, y) != None and attempt < 10)):
                    break
            #  If we didn't find an empty spot, we won't add a new player
            if cls.battlefield.getUnit(x, y) != None:
                break
            finalX = x
            finalY = y
            #  Create the new player in a separate
            # 			 * thread, making sure it does not 
            # 			 * block the system.
            # 			 
            Thread(Runnable()).start()
            i += 1
        #  Spawn a new battlefield viewer 
        Thread(Runnable()).start()
        #  Add a random player every (5 seconds x GAME_SPEED) so long as the
        # 		 * maximum number of players to enter the battlefield has not been exceeded. 
        # 		 
        while GameState.getRunningState():
            try:
                Thread.sleep(int((5000 * GameState.GAME_SPEED)))
                #  Connect a player to the game if the game still has room for a new player
                if cls.playerCount >= cls.MAX_PLAYER_COUNT:
                    continue 
                #  Once again, pick a random spot
                x = int()
                y = int()
                attempts = 0
                while True:
                    #  If finding an empty spot just keeps failing then we stop adding the new player
                    x = int((random() * BattleField.MAP_WIDTH))
                    y = int((random() * BattleField.MAP_HEIGHT))
                    attempts += 1
                    if not ((cls.battlefield.getUnit(x, y) != None and attempts < 10)):
                        break
                #  If we didn't find an empty spot, we won't add the new player
                if cls.battlefield.getUnit(x, y) != None:
                    continue 
                finalX = x
                finalY = y
                if cls.battlefield.getUnit(x, y) == None:
                    Player(finalX, finalY)
                    #  Create the new player in a separate
                    # 					 * thread, making sure it does not 
                    # 					 * block the system.
                    # 					 *
                    # 					new Thread(new Runnable() {
                    # 						public void run() {
                    # 							new Player(finalX, finalY);
                    # 						}
                    # 					}).start();
                    # 					
                    cls.playerCount += 1
            except InterruptedException as e:
                e.printStackTrace()
        #  Make sure both the battlefield and
        # 		 * the socketmonitor close down.
        # 		 
        BattleField.getBattleField().shutdown()
        System.exit(0)
        #  Stop all running processes


if __name__ == '__main__':
    import sys
    Core.main(sys.argv)
