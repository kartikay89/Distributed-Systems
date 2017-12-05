# Distributed-Systems

Keywords:
    Hybrid Architure
    Trailing State Synchronization
    Head Node (?)
    Transient, Delivery-based, Asynchronous: 
        (The sender awaits a confirmation, but does not block while waiting. It raises an exception if the confirmation is not received within a certain amount of time.)

Idea for replication and agreement: use 'Byzantine' system!
    Every client interacts with 4 servers at a time
    Messages and replies are exchanged with all 4 servers
    In case of disagreement (particular on the ORDER of MESSAGES/COMMANDS), the majority decides!
    If the decision is split, THE MESSAGES WERE PROBABLY SENT SO CLOSELY AFTER ANOTHER THAT IT DOESN'T REALLY MATTER WHICH DECISION WE TAKE (this is a game, after all)
        So we just assign a 'boss node' that has a casting vote in this case