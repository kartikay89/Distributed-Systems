from units.Unit import Unit


class Dragon(Unit):
    def dealDamage(self, x, y, damage):
        pass

    def adjustHitPoints(self, modifier):
        pass

    def hi(self):
        print("health is %s\n" % self.maxHealth)

    MIN_TIME_BETWEEN_TURNS = 1
    MAX_TIME_BETWEEN_TURNS = 7

    MIN_HITPOINTS = 50
    MAX_HITPOINTS = 100

    MIN_ATTACKPOINTS = 5
    MAX_ATTACKPOINTS = 10

    def __init__(self, maxHealth=100, attackPoints=50):
        super().__init__(maxHealth, attackPoints)
        # self.maxHealth = maxHealth
        # self.attackPoints = attackPoints

    # def __init__(self, maxHealth, attackPoints):
        # TODO maybe these need to be handled with abc.properties
        # self.hitPoints = self.maxHitPoints = maxHealth
        # self.attackPoints = attackPoints

        # Socket localSocket = new LocalSocket();
        # messageList = newHashMap < Integer, Message > ();
        #
        # // Get a new unit id
        # unitID = BattleField.getBattleField().getNewUnitID();
        #
        # // Create a new socket
        # clientSocket = new SynchronizedSocket(localSocket);
        #
        # try {
        # // Try to register the socket
        # clientSocket.register("D" + unitID);
        # }
        # catch(AlreadyAssignedIDException
        # e) {
        #     System.err.println("Socket \"D" + unitID + "\" was already registered.");
        # }
        #
        # clientSocket.addMessageReceivedHandler(this)