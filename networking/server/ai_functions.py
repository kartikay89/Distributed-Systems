from networking import Dragon, GameAction, GameActionType, Player

attackDistance = 2
healthThreshold = 0.50

def findClosestHeal(game, pos):
    heals = []
    for player in game.players.values():
        if player.hp < (player.init_hp * healthThreshold):
            heals.append(player)
    return findClosestUnit(game, heals, pos)

def findClosestUnit(game, units, pos):
    lowestDistance = 1000
    result = None

    for unit in units:
        distance = game.distance(unit.field.position, pos)
        #print "unit at total distance %d (position: %s)" % (distance, str(unit.field.position))

        if distance > 0 and distance < lowestDistance:
            result = unit
            lowestDistance = distance
            # Return early if we are next to a unit
            if distance == 1:
                return result
    return result


# Determine which move the unit should perform based on the current game state
#
# Strategy: heal a nearby player as soon as there is one that has
# below 50% of its initial hp, and go
# towards the closest dragon and strike otherwise
#
# Returns: either a game action or message TODO @abel
def get_next_action(player, game):
    pos = player.field.position
    heal = findClosestHeal(game, pos)
    if heal:
        return GameAction(type=GameActionType.HEAL, target_pos=heal.field.position)

    dragon = findClosestUnit(game, game.dragons.values(), pos)
    if not dragon:
        return None

    if game.distance(pos, dragon.field.position) <= attackDistance:
        return GameAction(type=GameActionType.ATTACK, target_pos=dragon.field.position)

    # From here on only moves towards dragons can be the case
    dragon_pos = dragon.field.position

    dx = pos[0] - dragon_pos[0]
    dy = pos[1] - dragon_pos[1]

    target_pos = pos

    if(abs(dx) >= abs(dy)):
        if dx > 0:
            target_pos[0] -= 1
        else:
            target_pos[0] += 1
    else:
        if dy > 0:
            target_pos[1] -= 1
        else:
            target_pos[1] += 1
    return GameAction(type=GameActionType.MOVE, target_pos=target_pos)
