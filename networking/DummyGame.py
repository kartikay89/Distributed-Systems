import random
import threading
import time

from networking import COOLDOWN, DEBUG_PRINT, GAME_SYNC_INTERVAL, GRID_SIZE, \
                       GameAction, GameActionType, GameSynchronizer, Message, \
                       safe_print


class Unit(object):
    def __init__(self):
        self.ap = 0
        self.hp = 0
        self.init_hp = 0
        self.field = None
        self.dead = True
        self.cooldown_time = 0

    def check_cooldown(self, ):
        current_time = time.time()
        if current_time - self.cooldown_time < COOLDOWN:
            safe_print('Unit {:s} could not perform action: on cooldown ({:f}, {:f}, {:d})'.format(self, self.cooldown_time, current_time, COOLDOWN))
            return False
        self.cooldown_time = current_time
        return True
        

    def attack(self, other):
        other.hp -= self.ap
        if other.hp <= 0:
            other.dead = True

    def heal(self, other):
        other.hp += self.ap
        if other.hp > other.init_hp:
            other.hp = other.init_hp


class Player(Unit):
    def __init__(self, player):
        Unit.__init__(self)
        self.ap = random.randint(1, 10)
        self.hp = random.randint(10, 20)
        self.init_hp = self.hp
        # IP address identifying a human being
        self.player = player

    def __repr__(self):
        return '[PLAYER at {:s} (ap {:d}, hp {:d})]'.format(self.field.position, self.ap, self.hp)

    def move(self, target_field):
        target_field.contents = self
        self.field.contents = None
        self.field = target_field
        

class Dragon(Unit):
    def __init__(self, identifier):
        Unit.__init__(self)
        self.ap = random.randint(5, 20)
        self.hp = random.randint(50, 100)
        self.init_hp = self.hp
        self.identifier = identifier

    def __repr__(self):
        return '[DRAGON at {:s} (ap {:d}, hp {:d})]'.format(self.field.position, self.ap, self.hp)


class Field(object):
    def __init__(self, contents=None, position=None):
        self.contents = contents
        self.position = position

    def __repr__(self):
        return '[FIELD at {:s}, contents {:s}]'.format(self.position, self.contents)


class DummyGame(object):
    def __init__(self, identifier, server):
        # book keeping variables
        self.identifier = identifier # Should be unique
        self.server = server
        self.servers = [] # List of ips belonging to the servers that host this game
        self.clients_to_update_servers = {} # Maps participating clients to the servers that send them updates
        
        self.units = []

        self.synchronizer = GameSynchronizer(self.server, self, GAME_SYNC_INTERVAL)
        self.synchronizer.start()
        self.checkpoint = None # Set to a copy of the last gamestate that all servers agreed on
        self.checkpoint_nr = 0 # Set to the NUMBER OF ACTIONS that have been executed in the current checkppint (used to identify checkpoints)

        self.sync_msg_lock = threading.RLock()
        self.sync_messages = [] # Will contain messages sent by the other servers that host this game, used to sync our states

        self.buffer_lock = threading.RLock()
        self.action_buffer = [] # Will contain all commands that the servers have not yet agreed on

        # game-defining veriables
        # Maps players (IP addresses) to Player objects
        self.players = {}
        # Maps dragon IDs to Dragon objects
        self.dragon_counter = 0 # Used for dragon IDs
        self.dragons = {}
        # Stores the game board
        self.fields = []
        self.distance = lambda src, dst: abs(dst[0] - src[0]) + abs(dst[1] - src[1])
        self.valid_field = lambda pos: pos[0] >= 0 and pos[0] < GRID_SIZE and pos[1] >= 0 and pos[1] < GRID_SIZE
        for x in range(GRID_SIZE):
            self.fields.append([])
            for y in range(GRID_SIZE):
                self.fields[x].append(Field(position=(x, y)))
    
    def __repr__(self):
        return '[GAME {:d} served by server {:d} at {:s}]'.format(self.identifier, self.server.identifier, self.server.host)

    def dg_print(self, s):
        if DEBUG_PRINT:
            safe_print('[GAME (game {:d}, server {:d})]: {:s}'.format(self.identifier, self.server.identifier, s))

    # Returns the next empty field, given a starting position
    def get_next_empty_field(self, position):
        for row in range(position[0], GRID_SIZE):
            for col in range(position[1], GRID_SIZE):
                if not self.fields[row][col].contents:
                    return self.fields[row][col]
        return None

    def spawn(self, action):
        # Check if the spawn can take place, and if so, what type of unit gets spawned
        if action.player:
            # Check if player is already in this game
            if action.player in self.players.keys():
                return False
            else:
                # Add player to this game
                unit = Player(action.player)
        else:
            # Add dragon to this game
            dragon_id = self.dragon_counter
            self.dragon_counter += 1
            unit = Dragon(dragon_id)
        target_field = self.fields[action.target_pos[0]][action.target_pos[1]]
        if target_field.contents:
            target_field = self.get_next_empty_field(target_pos)
        if not target_field:
            self.dg_print('Could not spawn: no empty fields')
            return False
        # Add the unit to the board
        target_field.contents = unit
        unit.field = target_field
        # Add the unit to our structures
        self.units.append(unit)
        if action.player:
            self.players[action.player] = unit
        else:
            self.dragons[dragon_id] = unit
        return True

    def move(self, action):
        self.dg_print('Moving!')
        # Perform various checks first
        acting_unit = self.players.get(action.player)
        if not acting_unit:
            self.dg_print('Could not move player {:s}: not found'.format(action.player))
            return False
        if not acting_unit.check_cooldown():
            return False
        if self.distance(acting_unit.field.position, action.target_pos) > 1:
            self.dg_print('Could not move {:s} to {:s}: distance too big'.format(acting_unit, action.target_pos))
            return False
        self.dg_print("target_pos = {:s}".format(action.target_pos))
        target_field = self.fields[action.target_pos[0]][action.target_pos[1]]
        if target_field.contents != None:
            self.dg_print('Could not move {:s} to {:s}: found unit {:s}'.format(acting_unit, action.target_pos, target_field.contents))
            return False
        self.dg_print('Moving to {:s}'.format(target_field))
        # Checks ok, move can commence
        acting_unit.move(target_field)
        return True

    def heal(self, action):
        acting_unit = self.players.get(action.player)
        if not acting_unit:
            self.dg_print('Player {:s} could not heal: not found'.format(action.player))
            return False
        if not acting_unit.check_cooldown():
            return False
        healed_unit = self.fields[action.target_pos[0]][action.target_pos[1]].contents
        if not healed_unit:
            self.dg_print('Unit {:s} could not heal on {:s} (empty field)'.format(acting_unit, action.target_pos))
            return False
        if self.distance(acting_unit.field.position, action.target_pos) > 5:
            self.dg_print('Player {:s} could not heal at {:s}: distance too big'.format(acting_unit, action.target_pos))
            return False
        if type(healed_unit) != Player:
            self.dg_print('Unit {:s} could not heal {:s} on {:s} (can only heal fellow players)'.format(acting_unit, healed_unit, action.target_pos))
            return False
        acting_unit.heal(healed_unit)
        return True

    # Remove a unit from our board
    def remove_unit(self, unit):
        unit.field.contents = None
        if type(unit) == Dragon:
            # Reverse lookup in our dragon dict: we have the unit, we want the ID
            dragon_id = [d_id for d_id, d in self.dragons.items() if d == unit][0]
            del self.dragons[dragon_id]
        else:
            # Reverse lookup in our player dict: we have the unit, we want the ID
            player = [p_id for p_id, p in self.players.items() if p == unit][0]
            del self.players[player]
        self.units.remove(unit)

    # Given an attack-GameAction, attempts to perform an attack
    def attack(self, action):
        if action.player:
            acting_unit = self.players[action.player]
        else:
            acting_unit = self.dragons[action.dragon_id]
        if not acting_unit:
            self.dg_print('Player {:s} could not attack: not found'.format(action.player))
            return False
        if not acting_unit.check_cooldown():
            return False
        victim_unit = self.fields[action.target_pos[0], action.target_pos[1]].contents
        if not victim_unit:
            self.dg_print('Unit {:s} could not attack on {:s} (empty field)'.format(acting_unit, action.target_pos))
            return False
        if self.distance(acting_unit.field.pos, victim_unit.field.pos) > 2:
            self.dg_print('Unit {:s} could not attack {:s} on {:s} (distance too great)'.format(acting_unit, victim_unit, action.target_pos))
            return False
        if type(victim_unit) == Player:
            self.dg_print('Unit {:s} could not attack {:s} on {:s} (can\'t attack fellow players)'.format(acting_unit, victim_unit, action.target_pos))
            return False
        acting_unit.attack(victim_unit)
        if victim_unit.dead:
            self.remove_unit(victim_unit)
        return True

    def perform_action(self, action):
        performed = False # Should actually be false here, but for now I want to store all actions

        self.dg_print('Got action: {:s}'.format(action))

        if not self.valid_field(action.target_pos):
            self.dg_print('Could not perform action on {:s} (invalid field)'.format(action.target_pos))
            return

        if action.type == GameActionType.SPAWN:
            performed = self.spawn(action)
        elif action.type == GameActionType.MOVE:
            performed = self.move(action)
        elif action.type == GameActionType.ATTACK:
            performed = self.attack(action)
        elif action.type == GameActionType.HEAL:
            performed = self.heal(action)
        # Store action, if it was actually performed (and not illegal)
        self.dg_print('After! ({:b})'.format(performed))
        if performed:
            with self.buffer_lock:
                self.action_buffer.append(action)
