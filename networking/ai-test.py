attackDistance = 2
maxHealthPlayer = 100
healthThreshold = 0.50

player = {
    "type": "player",
    "health": 100,
    "x": 3,
    "y": 3}

unit1 = {
    "type": "player",
    "health": 50,
    "x": 4,
    "y": 1}

unit2 = {
    "type": "player",
    "health": 100,
    "x": 4,
    "y": 2}

unit3 = {
    "type": "player",
    "health": 50,
    "x": 4,
    "y": 4}

dragon1 = {
    "type": "dragon",
    "health": 200,
    "x": 0,
    "y": 0}

dragon2 = {
    "type": "dragon",
    "health": 200,
    "x": 0,
    "y": 2}

dragon3 = {
    "type": "dragon",
    "health": 200,
    "x": 0,
    "y": 4}

d = {
    "type": "dragon",
    "health": 200,
    "x": 4,
    "y": 4}

# units = [unit1, unit2, unit3, dragon1, dragon2, dragon3]
units = [d]


def getDistance(unit, x, y):
    return abs(x - unit["x"]) + abs(y - unit["y"])


def findClosestDragon(units, x, y):
    dragons = [unit for unit in units if (unit["type"] is "dragon")]
    return findClosestUnit(dragons, x, y)


def findClosestPlayer(units, x, y):
    players = [unit for unit in units if (unit["type"] is "player")]
    return findClosestUnit(players, x, y)


def findClosestHeal(units, x, y):
    heals = []
    for unit in units:
        if unit["type"] == "player" and unit["health"] < (maxHealthPlayer * healthThreshold):
            heals.append(unit)
    return findClosestUnit(heals, x, y)


def findClosestUnit(units, x, y):
    lowestDistance = 1000
    result = None

    for unit in units:
        distance = getDistance(unit, x, y)
        print "unit at total distance %d (position: %d, %d)" % (distance, unit["x"], unit["y"])

        if distance < lowestDistance:
            result = unit
            lowestDistance = distance

            # # Return early if we are next to a unit
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
def determineMove(units, x, y):
    heal = findClosestHeal(units, x, y)
    if heal:
        return "heal"

    dragon = findClosestDragon(units, x, y)
    if not dragon:
        return "no dragons to attack"

    if getDistance(dragon, x, y) <= attackDistance:
        return "attack dragon at %d, %d with distance %d" % (dragon["x"], dragon["y"], getDistance(dragon, x, y))

    # From here on only moves towards dragons can be the case
    dragonx = dragon["x"]
    dragony = dragon["y"]

    dx = x - dragonx
    dy = y - dragony

    if(abs(dx) >= abs(dy)):
        if dx > 0:
            return "move left"

        return "move right"
    else:
        if dy > 0:
            return "move up"

        return "move down"

    return "Unable to resolve next move"


if __name__ == '__main__':
    x = player["x"]
    y = player["y"]

    # dragon = findClosestDragon(units, x, y)
    # print "closest dragon is at %d, %d" % (dragon["x"], dragon["y"])
    # player = findClosestPlayer(units, x, y)
    # print "closest player is at %d, %d" % (player["x"], player["y"])
    # heal = findClosestHeal(units, x, y)
    # if heal: print "healable with %d health at %d, %d" % (heal["health"], heal["x"], heal["y"])

    print determineMove(units, x, y)