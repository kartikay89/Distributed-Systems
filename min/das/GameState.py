#!/usr/bin/env python
""" generated source for module GameState """
from __future__ import print_function
# package: distributed.systems.das
# 
#  * Class containing the global gamestate. This
#  * state contains small things, which all threads 
#  * need to know. 
#  * 
#  * @author Pieter Anemaet, Boaz Pat-El
#  
class GameState(object):
    """ generated source for class GameState """
    #  Is-the-program-actually-running-flag
    running = True

    #  Relation between game time and real time
    GAME_SPEED = 0.01

    #  The number of players in the game
    playerCount = 0

    # 
    # 	 * Stop the program from running. Inform all threads
    # 	 * to close down.
    # 	 
    @classmethod
    def haltProgram(cls):
        """ generated source for method haltProgram """
        cls.running = False

    # 
    # 	 * Get the current running state 
    # 	 * @return true if the program is supposed to 
    # 	 * keep running.
    # 	 
    @classmethod
    def getRunningState(cls):
        """ generated source for method getRunningState """
        return cls.running

    # 
    # 	 * Get the number of players currently in the game.
    # 	 * @return int: the number of players currently in the game.
    # 	 
    @classmethod
    def getPlayerCount(cls):
        """ generated source for method getPlayerCount """
        return cls.playerCount
